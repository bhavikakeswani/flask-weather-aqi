from flask import Flask,render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, Integer, String, DateTime

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/forecast')
def forecast():
    return render_template('forecast.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run()