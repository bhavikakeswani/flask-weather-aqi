# SkySQI - Weather Dashboard

SkySQI is a Flask-based weather dashboard that displays real-time weather information, 5-day forecasts, air quality index (AQI), UV index, and more. Users can also explore other cities and submit messages via a contact form.

---

## Features

- 🌡️ **Current Weather**: Temperature, Real Feel, Wind, Pressure, Humidity, Sunrise & Sunset.  
- 📅 **5-Day Forecast**: Daily temperature and chance of rain chart.  
- 🌬️ **Air Quality Index (AQI)**: Toggle to show AQI with a descriptive label (Good, Moderate, etc.).  
- ☀️ **UV Index**: Current UV index display.  
- 🏙️ **City Images**: Beautiful city photos fetched via Unsplash API.  
- 🌍 **Other Cities Weather**: Quick overview of selected cities.  
- ✉️ **Contact Form**: Users can submit messages securely via Flask-Mail with authentication.  

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/bhavikakeswani/flask-weather-aqi.git
cd flask-weather-aqi
  ```
2. Create and activate a virtual environment:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
3. Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
4. Create a .env file in the root directory with the following variables:
 ```bash
  FLASK_SECRET_KEY=your-secret-key
  OPENWEATHER_API_KEY=your-api-key
  UNSPLASH_ACCESS_KEY=your-api-key
  MAIL_ID=your-mail-id
  MAIL_PASSWORD=your-mail-pass
  ```
5. Run the app:
  ```bash
  python main.py
  ```
6. Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🛠️ Technologies Used

- **Backend:** Flask, Python  
- **Frontend:** HTML, Jinja2 Templates, CSS, Chart.js  
- **APIs:** OpenWeatherMap API, Unsplash API  
- **Mailing:** Flask-Mail (SMTP authentication)  
- **Environment Management:** Python-dotenv

---

## 🚀 Usage

- Use the tabs to view **Today**, **Tomorrow**, or the **Next 5 days** forecast.
- Toggle the **Forecast / Air Quality** switch to see the AQI with a descriptive label.
- Explore other cities' weather via the **Search Cities** section.
- Submit messages through the **Contact Form**; emails are sent securely via Flask-Mail.

---

## Screenshots
<img width="1462" height="871" alt="Screenshot 2025-10-16 at 12 32 26 AM" src="https://github.com/user-attachments/assets/31e21a9b-eca0-4570-968f-eec99d570e55" />
<img width="1453" height="867" alt="Screenshot 2025-10-16 at 12 33 03 AM" src="https://github.com/user-attachments/assets/15781d0a-6e75-4fe7-94ec-8016e99e3cdf" />
<img width="1450" height="866" alt="Screenshot 2025-10-16 at 12 33 20 AM" src="https://github.com/user-attachments/assets/e4649a1c-1476-4c8c-ae2a-eead54378f65" />
<img width="1450" height="876" alt="Screenshot 2025-10-16 at 12 33 30 AM" src="https://github.com/user-attachments/assets/90bf6a2f-fe45-427f-a10e-89cb51f8e05f" />
<img width="1451" height="874" alt="Screenshot 2025-10-16 at 12 33 41 AM" src="https://github.com/user-attachments/assets/d79ceb4b-f9cd-4577-89ef-811c6841751a" />
<img width="1448" height="813" alt="Screenshot 2025-10-16 at 12 33 59 AM" src="https://github.com/user-attachments/assets/8450e01c-f05e-4cc7-9376-6f9af0c2f1c3" />

---

## License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
