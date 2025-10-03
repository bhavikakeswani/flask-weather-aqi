from flask import Flask,render_template,request,flash,redirect,url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Boolean, Integer, String, DateTime

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'your-secret-key'

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
    return render_template('dashboard.html')

@app.route('/forecast')
@login_required
def forecast():
    return render_template('forecast.html')

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

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    db.session.delete(current_user)
    db.session.commit()
    return redirect(url_for('login'))

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