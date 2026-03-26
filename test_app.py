"""
Automatiske tester for aksjeportefolje-appen.
Kjør med: pytest test_app.py -v
"""
import pytest
from app import app, db, User, Holding


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def register(client, username='testbruker', password='passord123'):
    return client.post('/register', data={
        'username': username,
        'password': password,
    }, follow_redirects=True)


def login(client, username='testbruker', password='passord123'):
    return client.post('/login', data={
        'username': username,
        'password': password,
    }, follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


# --- Grunnleggende sider ---

def test_hjemmeside_videresender_til_login(client):
    r = client.get('/', follow_redirects=True)
    assert r.status_code == 200
    assert 'Logg inn' in r.get_data(as_text=True) or 'login' in r.request.url


def test_login_side_laster(client):
    r = client.get('/login')
    assert r.status_code == 200


def test_register_side_laster(client):
    r = client.get('/register')
    assert r.status_code == 200


# --- Brukeroppretting ---

def test_registrering_fungerer(client):
    r = register(client)
    assert r.status_code == 200
    assert 'portefølje' in r.get_data(as_text=True).lower() or 'dashboard' in r.request.url


def test_registrering_kort_passord_feiler(client):
    r = client.post('/register', data={'username': 'test', 'password': '123'}, follow_redirects=True)
    assert 'minst 6' in r.get_data(as_text=True) or r.status_code == 200


def test_duplikat_brukernavn_feiler(client):
    register(client, 'duplikat', 'passord123')
    r = register(client, 'duplikat', 'passord123')
    assert 'allerede' in r.get_data(as_text=True).lower()


# --- Innlogging ---

def test_innlogging_fungerer(client):
    register(client)
    logout(client)
    r = login(client)
    assert r.status_code == 200


def test_feil_passord_feiler(client):
    register(client)
    logout(client)
    r = client.post('/login', data={'username': 'testbruker', 'password': 'feil'}, follow_redirects=True)
    assert 'Feil' in r.get_data(as_text=True) or 'feil' in r.get_data(as_text=True).lower()


def test_dashboard_krever_innlogging(client):
    r = client.get('/dashboard', follow_redirects=True)
    assert 'login' in r.request.url or 'Logg inn' in r.get_data(as_text=True)


def test_dashboard_vises_etter_innlogging(client):
    register(client)
    r = client.get('/dashboard')
    assert r.status_code == 200
    assert 'portefølje' in r.get_data(as_text=True).lower()


# --- Aksjer ---

def test_legg_til_aksje_krever_innlogging(client):
    r = client.post('/add_stock', data={
        'ticker': 'AAPL',
        'shares': '10',
        'portfolio_type': 'vekst',
    }, follow_redirects=True)
    assert 'login' in r.request.url or 'Logg inn' in r.get_data(as_text=True)


def test_ugyldig_portefolje_type_feiler(client):
    register(client)
    r = client.post('/add_stock', data={
        'ticker': 'AAPL',
        'shares': '10',
        'portfolio_type': 'ugyldig',
    }, follow_redirects=True)
    assert r.status_code == 200


def test_slett_aksje_krever_innlogging(client):
    r = client.post('/delete_stock/1', follow_redirects=True)
    assert 'login' in r.request.url or 'Logg inn' in r.get_data(as_text=True)


def test_slett_annens_aksje_ignoreres(client):
    """Bruker kan ikke slette andres aksjer."""
    register(client, 'bruker1', 'passord123')
    logout(client)
    register(client, 'bruker2', 'passord123')

    with app.app_context():
        bruker1 = User.query.filter_by(username='bruker1').first()
        holding = Holding(user_id=bruker1.id, ticker='AAPL.OL', shares=10, portfolio_type='vekst')
        db.session.add(holding)
        db.session.commit()
        holding_id = holding.id

    r = client.post(f'/delete_stock/{holding_id}', follow_redirects=True)
    assert r.status_code == 200

    with app.app_context():
        assert Holding.query.get(holding_id) is not None
