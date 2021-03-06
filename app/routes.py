from flask import render_template, redirect, session, request, url_for
from app import app, mongodb, stocks, user_account, qpemail
from app.portfolio import portfolio_v1

test_stocks = {
    'Ticker': ['AAPL', 'AMZN'],
    'Open': [99.26, 747.79],
    'High': [99.30, 751.28],
    'Low': [98.31, 743.53],
    'Close': [98.66, 744.86],
    'Volume': [28313669.0, 2277711.0],
    'Date': ['2016-07-22', '2016-07-22']
}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        shown_stocks = stocks.get_home_stocks(request.form['stock_search'].upper())
    else:
        shown_stocks = stocks.get_home_stocks()
    return render_template('index.html', session=session, stocks=shown_stocks, stocks_len=len(shown_stocks['Ticker']))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session and session['user_id'] != None:
        return redirect(url_for('account'))

    error = ''
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        subscription = request.form['subscription']
        if mongodb.check_user(email):
            error = 'Please try a different email. This email is already in use.'
            return render_template('signup.html', session=session, error=error, msg=msg)
        else:
            new_user = mongodb.add_user(email, password, subscription)
            qpemail.verify_code_email(mongodb.get_user_by_id(new_user))
            msg = 'A verification code and url have been sent to your email to complete signing up your account.'
            return render_template('signup.html', session=session, error=error, msg=msg)
    return render_template('signup.html', session=session, error=error, msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session and session['user_id'] != None:
        return redirect(url_for('account'))
        
    error = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        found_user = mongodb.check_user(email, password)
        if found_user:
            if mongodb.is_verified_user(found_user):
                session['user_id'] = found_user
                return redirect(url_for('account'))
            else:
                error = 'This account is not yet verified.'
                return render_template('login.html', session=session, error=error)
        else:
            error = 'Email or password is incorrect. Please try again.'
            return render_template('login.html', session=session, error=error)
    return render_template('login.html', session=session, error=error)

@app.route('/logout')
def logout():
    if 'user_id' not in session or session['user_id'] == None:
        return url_for('login')
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html', session=session)

@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    if 'user_id' not in session or session['user_id'] == None or \
        ('user_id' in session and not mongodb.is_verified_user(session['user_id'])):
        return redirect(url_for('login'))

    if request.method == 'POST':
        portfolio_v1.create_add_portfolio(session['user_id'])
        return redirect(url_for('portfolio'))

    return render_template('portfolio.html', session=session,
                            portfolios=mongodb.get_portfolios(session['user_id']),
                            portfolio_settings=mongodb.get_portfolio_settings(session['user_id']))

@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session or session['user_id'] == None or \
        ('user_id' in session and not mongodb.is_verified_user(session['user_id'])):
        return redirect(url_for('login'))

    if request.method == 'POST':
        confirm_button = request.form['account_button']
        user_id = session['user_id']
        if confirm_button == 'update_billing':
            user_account.update_billing_info(user_id, request.form)
            return redirect(url_for('account'))
        elif confirm_button == 'confirm_delete':
            mongodb.delete_user_by_id(user_id)
            return redirect(url_for('logout'))
        elif confirm_button == 'update_portfolio_settings':
            user_account.update_portfolio_settings(user_id, request.form)
            return redirect(url_for('account'))
        elif confirm_button == 'update_account':
            user_account.update_account(user_id, request.form)
            return redirect(url_for('account'))

    user_id = session['user_id']
    return render_template('account.html', session=session,
                            email=mongodb.get_email(user_id),
                            billing_info=user_account.get_billing_info(user_id),
                            portfolio_settings=user_account.get_portfolio_settings(user_id))

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', session=session)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'user_id' in session and session['user_id'] != None:
        return redirect(url_for('account'))

    error = ''
    if 'a' not in request.args or 'b' not in request.args:
        error = 'This is not a valid verification link.'
        render_template('verify.html', session=session, error=error)
    else:
        if request.method == 'POST':
            is_verified = mongodb.check_verify_code(request.args['b'], request.args['a'], request.form['codeVerifyInput'])
            if is_verified:
                return redirect(url_for('login'))
            else:
                error = 'Incorrect validation code.'
                render_template('verify.html', session=session, error=error)
    
        return render_template('verify.html', session=session, error=error)