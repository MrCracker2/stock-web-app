from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
import yfinance as yf
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        users = load_users()

        if email in users:
            error = f"User already exists with email: {email}. Please login."
        else:
            users[email] = {'name': name, 'password': password}
            save_users(users)
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()

        if email in users and users[email]['password'] == password:
            session['user'] = {'email': email, 'name': users[email]['name']}
            profile_file = 'user_profiles.xlsx'
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ip_address = request.remote_addr

            if os.path.exists(profile_file):
                df = pd.read_excel(profile_file)
            else:
                df = pd.DataFrame(columns=['Email', 'Name', 'Password', 'First Login', 'IP Address'])

            if not (df['Email'] == email).any():
                new_row = pd.DataFrame({
                    'Email': [email],
                    'Name': [users[email]['name']],
                    'Password': [users[email]['password']],
                    'First Login': [current_time],
                    'IP Address': [ip_address]
                })
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_excel(profile_file, index=False)

            log_file = 'user_log_history.xlsx'
            login_time = current_time

            if os.path.exists(log_file):
                log_df = pd.read_excel(log_file)
            else:
                log_df = pd.DataFrame(columns=['Email', 'Name', 'Login Time', 'Logout Time'])

            new_log = pd.DataFrame({
                'Email': [email],
                'Name': [users[email]['name']],
                'Login Time': [login_time],
                'Logout Time': ['']
            })
            log_df = pd.concat([log_df, new_log], ignore_index=True)
            log_df.to_excel(log_file, index=False)

            return redirect(url_for('dashboard'))
        else:
            error = "❌ Invalid email or password."

    return render_template('login.html', error=error)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    message = None
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        users = load_users()

        if email in users:
            users[email]['password'] = new_password
            save_users(users)
            message = "Password updated successfully! Please login."
            return redirect(url_for('login'))
        else:
            message = "Email not found! Try registering."

    return render_template('reset_password.html', message=message)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    chart_html = None
    symbol = None
    price = None
    performance = {}
    company_info = {}
    news = []

    if request.method == 'POST':
        symbol = request.form['symbol'].strip().upper()
        range_option = request.form['range']

        trial_symbols = [symbol, symbol + '.NS'] if '.' not in symbol and len(symbol) <= 6 else [symbol]

        for s in trial_symbols:
            try:
                ticker = yf.Ticker(s)
                df = ticker.history(period=range_option)
                if not df.empty:
                    symbol = s
                    info = ticker.info
                    price = info.get('currentPrice') or info.get('regularMarketPrice')

                    # 📊 Stock Performance
                    performance = {
                        'today_low': info.get('dayLow'),
                        'today_high': info.get('dayHigh'),
                        '52_week_low': info.get('fiftyTwoWeekLow'),
                        '52_week_high': info.get('fiftyTwoWeekHigh'),
                        'open': info.get('open'),
                        'prev_close': info.get('previousClose'),
                    }

                    # 🏢 Company Info
                    company_info = {
                        'name': info.get('longName'),
                        'sector': info.get('sector'),
                        'industry': info.get('industry'),
                        'market_cap': info.get('marketCap')
                    }

                    # 📰 Recent News
                    news = ticker.news[:5]  # show only latest 5 articles

                    # 📈 Plot Chart
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price', line=dict(color='blue')))
                    fig.update_layout(title=f"{symbol}", xaxis_title="Date", yaxis_title="Price", height=500, template="plotly_dark")
                    chart_html = pio.to_html(fig, full_html=False)
                    break
            except Exception as e:
                print("Error fetching stock:", e)
                continue

    return render_template('dashboard.html',
                           user=session['user'],
                           chart_html=chart_html,
                           symbol=symbol,
                           price=price,
                           performance=performance,
                           company_info=company_info,
                           news=news)


@app.route('/logout')
def logout():
    if 'user' in session:
        email = session['user']['email']
        logout_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file = 'user_log_history.xlsx'

        if os.path.exists(log_file):
            df = pd.read_excel(log_file)
            for i in range(len(df) - 1, -1, -1):
                if df.loc[i, 'Email'] == email and (pd.isna(df.loc[i, 'Logout Time']) or df.loc[i, 'Logout Time'] == ''):
                    df.loc[i, 'Logout Time'] = logout_time
                    break
            df.to_excel(log_file, index=False)

    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/alert', methods=['GET', 'POST'])
def alert():
    if 'user' not in session:
        return redirect(url_for('login'))

    chart_html = None
    symbol = request.args.get('symbol', '').strip().upper()
    price = None

    if symbol:
        trial_symbols = [symbol, symbol + '.NS'] if '.' not in symbol else [symbol]
        for s in trial_symbols:
            try:
                ticker = yf.Ticker(s)
                df = ticker.history(period='6mo')
                if not df.empty:
                    price = ticker.info.get('currentPrice') or ticker.info.get('regularMarketPrice')
                    symbol = s
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price', line=dict(color='cyan')))
                    fig.update_layout(title=f"{symbol}", xaxis_title="Date", yaxis_title="Price", height=500, template="plotly_dark")
                    chart_html = pio.to_html(fig, full_html=False)
                    break
            except:
                continue

    return render_template('alert.html', symbol=symbol, chart_html=chart_html, price=price, user=session['user'])


@app.route('/set_alert', methods=['POST'])
def set_alert():
    symbol = request.form['symbol'].strip().upper()
    target = float(request.form['target'])
    email = request.form['email']

    try:
        stock = yf.Ticker(symbol)
        price = stock.info.get('currentPrice') or stock.info.get('regularMarketPrice')

        if price is None:
            return "Stock price not available.", 400

        if price >= target:
            send_email_alert(email, symbol, price, target)
            return f"📩 Alert sent! {symbol} is ₹{price}, which meets or exceeds your target ₹{target}."
        else:
            return f"{symbol} is ₹{price}. Target not yet reached."
    except Exception as e:
        return f"Error: {str(e)}"

def send_email_alert(to_email, symbol, current_price, target_price):
    msg = MIMEMultipart("alternative")
    msg['Subject'] = f"📈 {symbol} Alert: Target ₹{target_price} hit!"
    msg['From'] = "belikeapro123@gmail.com"
    
    
    msg['To'] = to_email

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color:#f1f5f9; padding:20px;">
        <div style="max-width:600px; margin:auto; background:#ffffff; border-radius:10px; padding:25px; box-shadow:0 0 15px rgba(0,0,0,0.1);">
          <h2 style="color:#007bff;">📊 StockTracker Pro</h2>
          <p style="font-size:16px;">🎯 Your target has been reached for <strong>{symbol}</strong>!</p>
          <table style="margin: 20px 0; font-size:15px;">
            <tr><td><strong>📍 Current Price:</strong></td><td>₹{current_price}</td></tr>
            <tr><td><strong>🎯 Target Price:</strong></td><td>₹{target_price}</td></tr>
          </table>
          <p style="margin-bottom: 20px;">Click below to view the live chart and more insights.</p>
          <a href="http://localhost:5050/dashboard" style="display:inline-block; background:#28a745; color:white; padding:12px 22px; font-weight:bold; text-decoration:none; border-radius:6px;">📈 Open Dashboard</a>
          <p style="margin-top:30px; font-size:13px; color:#888;">This email was sent by <strong>StockTracker Pro</strong>.</p>
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login("belikeapro123@gmail.com", "ecmi gfqp vumu nzwi")
        server.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True, port=5050)