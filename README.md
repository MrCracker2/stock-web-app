Stock Tracker Web App 📈

A Flask-based web application that allows users to track stock performance, view company details, recent news, and monitor login activity. The app uses Excel to store user profiles and login history, with an interactive Plotly chart for stock performance visualization.

🚀 Live Demo

https://stock-web-app-v7jq.onrender.com

📸 Screenshots

Login Page


<img width="1470" height="956" alt="Login" src="https://github.com/user-attachments/assets/17497512-05ce-4527-84af-730cc82c9c05" />


Dashboard

<img width="1470" height="956" alt="Ploty chart" src="https://github.com/user-attachments/assets/3e486c58-d01c-47e2-9e4f-54a199ad38d3" />


Alert Stock Chart

<img width="1470" height="956" alt="alert" src="https://github.com/user-attachments/assets/5c4a89b4-e6e9-4390-9591-e239f6268fec" />



📘 About the Project

This web app provides:

User registration and login

Dashboard showing stock price info: today's low/high, 52-week low/high, open, prev. close

Plotly-based stock chart

About the company section and recent news

Excel-based user management and login history logging

🛠 Tech Stack

Backend: Python, Flask

Frontend: HTML, CSS, Bootstrap, JavaScript

Data: yfinance, pandas

Visualization: Plotly

Storage: Excel (openpyxl), JSON

Folder Structure
stock-web-app/
├── app.py
├── requirements.txt
├── render.yaml
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── alert.html
├── static/
│   └── background.mp4
├── users.json
├── user_profiles.xlsx
├── user_log_history.xlsx


⚙️ Installation

# Clone the repository
git clone https://github.com/MrCracker2/stock-web-app.git
cd stock-web-app

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# or
venv\Scripts\activate  # For Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

🧑‍💻 Usage

Register or log in to your account.

Enter a stock symbol (e.g., TCS.NS).

View interactive stock chart.

See today’s stock stats (open, low, high, 52-week high/low, etc.).

Read company profile and news.

User login time and logout are recorded in Excel.

🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

📄 License

This project is licensed under the MIT License.

📬 Contact

Author: Shashwat KumarEmail: kumarshashwat890@gmail.comGitHub: MrCracker2
