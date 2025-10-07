from flask import Flask,render_template,request,flash,redirect,url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Boolean, Integer, String, DateTime
from weather_utils import get_weather, get_forecast,get_uv_index,get_city_image
from collections import defaultdict
from dotenv import load_dotenv
import hashlib
import os

load_dotenv()

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")

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
    default_city: Mapped[str] = mapped_column(String(100), default="")

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
    city = current_user.default_city or "Delhi"
    units = "metric" if current_user.temp_unit == "Celsius" else "imperial"

    weather = get_weather(city, units)

    other_city_names = ["Beijing", "California", "Dubai", "Charlottetown"]
    other_cities_weather = []
    for c in other_city_names:
        data = get_weather(c)
        if data:
            other_cities_weather.append({
                "name": c,
                "description": data["weather"][0]["description"].title(),
                "temp": data["main"]["temp"]
            })

    if weather and "coord" in weather:
        lat = weather["coord"]["lat"]
        lon = weather["coord"]["lon"]
        uv_index = get_uv_index(lat, lon)
    else:
        uv_index = None

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
                "temp": round(sum(temps)/len(temps)),
                "icon": weather_icon
            })

        weekly_rain_chances = [day.get('pop', 0) * 100 for day in weekly_forecast] 
        weekly_dates = [day['date'] for day in weekly_forecast]


    return render_template("dashboard.html", weather=weather, weekly_forecast=weekly_forecast, weekly_rain=weekly_rain_chances,weekly_dates=weekly_dates, uv_index=uv_index, other_cities_weather=other_cities_weather, city_image=city_image, city=city)

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
    from datetime import datetime
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
                flash('Invalid password, Please try again.', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Email not found. Please sign up first.', 'warning')
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
            flash("Email already registered. Please sign in.",'warning')
            return redirect(url_for("login"))
        
        if confirm_password == password:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            new_user = User(name=name, email=email, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
        else:
            flash("Passwords don't match",'danger')
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
            flash("Current password is incorrect.", "danger")
            return redirect(url_for('change_password'))

        if new_password != confirm_password:
            flash("New passwords do not match.", "warning")
            return redirect(url_for('change_password'))

        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
        current_user.password = hashed_password
        db.session.commit()

        flash("Your password has been updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('change_password.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/contact')
@login_required
def contact():
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