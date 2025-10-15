from flask import Flask,render_template,request,flash,redirect,url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Boolean, Integer, String, DateTime
from weather_utils import get_weather, get_forecast,get_uv_index,get_city_image,get_air_quality,aqi_category
from collections import defaultdict
from flask_babel import Babel, _
from dotenv import load_dotenv
from datetime import datetime
from flask_mail import Mail, Message
import hashlib
import os

load_dotenv()

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
MAIL_ID=os.getenv("MAIL_ID")
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = MAIL_ID
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = ('SkySQI Contact', MAIL_ID)

mail = Mail(app)

def get_locale():
    if current_user.is_authenticated:
        lang_map = {
            "English": "en",
            "Hindi": "hi",
            "French": "fr"
        }
        return lang_map.get(current_user.language, "en")
    return "en"

babel = Babel(app, locale_selector=get_locale)

def gravatar_url(email, size=80, default="retro"):
    email_hash = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}"
@app.context_processor
def inject_gravatar():
    return dict(gravatar_url=gravatar_url)

login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    
    location: Mapped[str] = mapped_column(String(100), default="")
    bio: Mapped[str] = mapped_column(String(250), default="")
    github: Mapped[str] = mapped_column(String(250), default="")
    avatar_url: Mapped[str] = mapped_column(String(250), default="default.jpg")
    default_city: Mapped[str] = mapped_column(String(100), default="Delhi")

    theme: Mapped[str] = mapped_column(String(50), default="Light")   
    font_size: Mapped[str] = mapped_column(String(50), default="Medium") 
    language: Mapped[str] = mapped_column(String(50), default="English")
    temp_unit: Mapped[str] = mapped_column(String(50), default="Celsius") 
    weather_alert: Mapped[bool] = mapped_column(Boolean, default=True)
    aqi_alert: Mapped[bool] = mapped_column(Boolean, default=False)
    aqi_threshold: Mapped[int] = mapped_column(Integer, default=150)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    searched_city = request.args.get('city')
    city = searched_city if searched_city else current_user.default_city

    units = "metric" if current_user.temp_unit == "Celsius" else "imperial"
    unit_symbol = "°C" if units == "metric" else "°F"
    wind_unit = "m/s" if units == "metric" else "mph"

    weather = get_weather(city, units)

    other_city_names = ["Beijing", "California", "Dubai", "Charlottetown"]
    other_cities_weather = []
    for c in other_city_names:
        data = get_weather(c, units)
        if data:
            other_cities_weather.append({
                "name": c,
                "description": data["weather"][0]["description"].title(),
                "temp": data["main"]["temp"]
            })

    aqi_index = None
    aqi_label = None
    if weather and "coord" in weather:
        lat, lon = weather["coord"]["lat"], weather["coord"]["lon"]
        uv_index = get_uv_index(lat, lon)
        aqi_index = get_air_quality(lat, lon)
        aqi_label = aqi_category(aqi_index)


    forecast_data = get_forecast(city, units)
    weekly_forecast = []
    city_image = get_city_image(city)

    if forecast_data and "list" in forecast_data:
        grouped = defaultdict(list)
        for entry in forecast_data["list"]:
            date_str = entry["dt_txt"].split(" ")[0]
            grouped[date_str].append(entry)

        for date, entries in grouped.items():
            temps = [e["main"]["temp"] for e in entries]
            weather_icon = entries[0]["weather"][0]["icon"]
            weekly_forecast.append({
                "date": datetime.strptime(date, "%Y-%m-%d").strftime("%a"),
                "full_date": date,
                "temp": round(sum(temps)/len(temps)),
                "icon": weather_icon,
                "pop": round(max(
                    e.get("pop", 0)
                    or e.get("rain", {}).get("3h", 0)
                    or e.get("snow", {}).get("3h", 0)
                    for e in entries
                ) * 100)
            })

        weekly_forecast.sort(key=lambda x: x["full_date"])
        weekly_dates = [day["date"] for day in weekly_forecast]
        weekly_rain_chances = [day.get("pop", 0) for day in weekly_forecast]

        tomorrow_forecast = weekly_forecast[1] if len(weekly_forecast) > 1 else None
        next_days_forecast = weekly_forecast[1:6]
    else:
        weekly_dates, weekly_rain_chances, tomorrow_forecast, next_days_forecast = [], [], None, []

    return render_template(
        "dashboard.html",
        weather=weather,
        weekly_forecast=weekly_forecast,
        weekly_rain=weekly_rain_chances,
        weekly_dates=weekly_dates,
        tomorrow_forecast=tomorrow_forecast,
        next_days_forecast=next_days_forecast,
        uv_index=uv_index,
        aqi_label=aqi_label,
        other_cities_weather=other_cities_weather,
        city_image=city_image,
        city=city,
        unit_symbol=unit_symbol,
        wind_unit=wind_unit
    )

@app.route('/forecast')
@login_required
def forecast():
    city = current_user.default_city or "Delhi"
    units = "metric" if current_user.temp_unit == "Celsius" else "imperial"

    forecast_data = get_forecast(city, units)

    grouped_forecast = defaultdict(list)
    if forecast_data and "list" in forecast_data:
        for entry in forecast_data["list"]:
            date_str = entry["dt_txt"].split(" ")[0]
            grouped_forecast[date_str].append(entry)

    sorted_forecast = {}
    for date_str, entries in grouped_forecast.items():
        day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%a")
        sorted_forecast[day_name] = entries

    return render_template("forecast.html", forecast=sorted_forecast, city=city)

@app.template_filter("datetimeformat")
def datetimeformat(value):
    return datetime.fromtimestamp(value).strftime("%H:%M")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash(_('Invalid password, Please try again.'), 'danger')
                return redirect(url_for('login'))
        else:
            flash(_('Email not found. Please sign up first.'), 'warning')
            return redirect(url_for('register'))
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password=request.form.get('confirm_password')

        existing_user = db.session.execute(db.select(User).where(User.email == email)).scalar_one_or_none()
        if existing_user:
            flash(_("Email already registered. Please sign in."),'warning')
            return redirect(url_for("login"))
        
        if confirm_password == password:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            new_user = User(name=name, email=email, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
        else:
            flash(_("Passwords don't match"),'danger')
    return render_template('register.html')

@app.route('/delete')
@login_required
def delete():
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not check_password_hash(current_user.password, current_password):
            flash(_("Current password is incorrect."), "danger")
            return redirect(url_for('change_password'))

        if new_password != confirm_password:
            flash(_("New passwords do not match."), "warning")
            return redirect(url_for('change_password'))

        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
        current_user.password = hashed_password
        db.session.commit()

        flash(_("Your password has been updated successfully!"), "success")
        return redirect(url_for('dashboard'))

    return render_template('change_password.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        current_user.name = name
        current_user.email = email
        db.session.commit()  

        return redirect(url_for('profile'))

    return render_template('profile.html')

@app.route('/update_preferences', methods=['POST'])
@login_required
def update_preferences():
    if request.is_json:
        data = request.get_json()
        theme = data.get("theme")
        if theme:
            current_user.theme = theme
        db.session.commit()
        return {"success": True}

    default_city = request.form.get('default_city')
    temp_unit = request.form.get('temp_unit')
    theme = request.form.get('theme')

    if default_city:
        current_user.default_city = default_city
    if temp_unit:
        current_user.temp_unit = temp_unit
    if theme:
        current_user.theme = theme

    db.session.commit()
    return redirect(url_for('profile'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_user.language = request.form.get('language')
        current_user.temp_unit = request.form.get('temp_unit')
        current_user.theme = request.form.get('theme')
        current_user.font_size = request.form.get('font_size')
        current_user.weather_alert = bool(request.form.get('weather_alert'))
        current_user.aqi_alert = bool(request.form.get('aqi_alert'))
        current_user.aqi_threshold = int(request.form.get('aqi_threshold', 150))

        db.session.commit()
        return redirect(url_for('settings'))

    return render_template('settings.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        html_content = f"""
        <h2>New Contact Form Submission</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Message:</strong></p>
        <p>{message}</p>
        """

        msg = Message(
            subject=f"Contact Form: {subject}",
            recipients=[MAIL_ID],
            html=html_content
        )

        mail.send(msg)
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run()