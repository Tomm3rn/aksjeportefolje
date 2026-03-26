from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import yfinance as yf
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bytt-denne-i-produksjon-123!')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Render.com bruker postgres://, SQLAlchemy krever postgresql://
database_url = os.environ.get('DATABASE_URL', 'sqlite:///portfolio.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Opprett tabeller ved oppstart (kjøres av gunicorn i produksjon)
with app.app_context():
    db.create_all()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    holdings = db.relationship('Holding', backref='user', lazy=True)


class Holding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker = db.Column(db.String(20), nullable=False)
    shares = db.Column(db.Float, nullable=False)
    portfolio_type = db.Column(db.String(20), nullable=False)  # 'utbytte' eller 'vekst'
    added_date = db.Column(db.DateTime, default=datetime.utcnow)


# Enkel cache for å unngå for mange API-kall
price_cache = {}


def get_stock_info(ticker):
    if ticker in price_cache:
        cached_time, cached_data = price_cache[ticker]
        if datetime.now() - cached_time < timedelta(minutes=15):
            return cached_data
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        data = {
            'name': info.get('longName') or info.get('shortName') or ticker,
            'price': info.get('currentPrice') or info.get('regularMarketPrice') or 0,
            'dividend_yield': round((info.get('dividendYield') or 0) * 100, 2),
            'currency': info.get('currency', 'NOK'),
            'change_pct': round(info.get('regularMarketChangePercent') or 0, 2),
            'sector': info.get('sector', ''),
            'valid': True,
        }
        price_cache[ticker] = (datetime.now(), data)
        return data
    except Exception:
        return {'name': ticker, 'price': 0, 'dividend_yield': 0,
                'currency': 'NOK', 'change_pct': 0, 'sector': '', 'valid': False}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        flash('Feil brukernavn eller passord', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if len(password) < 6:
            flash('Passordet må være minst 6 tegn', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Brukernavnet er allerede i bruk', 'danger')
        else:
            user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    holdings = Holding.query.filter_by(user_id=session['user_id']).all()

    utbytte = []
    vekst = []

    utbytte_sum = {'value': 0, 'dividends': 0}
    vekst_sum = {'value': 0}

    for h in holdings:
        info = get_stock_info(h.ticker)
        current_value = info['price'] * h.shares
        annual_dividend = current_value * (info['dividend_yield'] / 100)

        row = {
            'id': h.id,
            'ticker': h.ticker,
            'name': info['name'],
            'shares': h.shares,
            'current_price': info['price'],
            'current_value': current_value,
            'dividend_yield': info['dividend_yield'],
            'annual_dividend': annual_dividend,
            'currency': info['currency'],
            'change_pct': info['change_pct'],
            'valid': info['valid'],
        }

        if h.portfolio_type == 'utbytte':
            utbytte.append(row)
            utbytte_sum['value'] += current_value
            utbytte_sum['dividends'] += annual_dividend
        else:
            vekst.append(row)
            vekst_sum['value'] += current_value

    return render_template('dashboard.html',
        username=session['username'],
        utbytte=utbytte,
        vekst=vekst,
        utbytte_sum=utbytte_sum,
        vekst_sum=vekst_sum,
        last_updated=datetime.now().strftime('%d.%m.%Y %H:%M'),
    )


@app.route('/add_stock', methods=['POST'])
@login_required
def add_stock():
    ticker = request.form['ticker'].upper().strip()
    try:
        shares = float(request.form['shares'].replace(',', '.'))
    except ValueError:
        flash('Ugyldig tall for antall aksjer', 'danger')
        return redirect(url_for('dashboard'))

    portfolio_type = request.form['portfolio_type']
    if portfolio_type not in ('utbytte', 'vekst'):
        flash('Ugyldig porteføljetype', 'danger')
        return redirect(url_for('dashboard'))

    if '.' not in ticker:
        ticker += '.OL'

    # Verifiser at tickeren finnes
    info = get_stock_info(ticker)
    if not info['valid'] or info['price'] == 0:
        flash(f'Fant ikke aksjen "{ticker}". Sjekk at ticker-koden er riktig.', 'danger')
        return redirect(url_for('dashboard'))

    holding = Holding(
        user_id=session['user_id'],
        ticker=ticker,
        shares=shares,
        portfolio_type=portfolio_type
    )
    db.session.add(holding)
    db.session.commit()
    flash(f'{ticker} lagt til i {"utbytte" if portfolio_type == "utbytte" else "vekst"}-porteføljen', 'success')
    return redirect(url_for('dashboard'))


@app.route('/delete_stock/<int:holding_id>', methods=['POST'])
@login_required
def delete_stock(holding_id):
    holding = Holding.query.filter_by(id=holding_id, user_id=session['user_id']).first()
    if holding:
        db.session.delete(holding)
        db.session.commit()
        flash('Aksje fjernet', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
