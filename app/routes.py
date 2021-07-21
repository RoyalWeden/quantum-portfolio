from flask.helpers import url_for
from app import app
from flask import render_template, redirect, session, request
from app import mongodb

@app.route('/')
def home():
    return render_template('index.html', session=session)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        new_user = mongodb.add_user(request.form['email'], request.form['password'], request.form['subscription'])
        if new_user != None:
            session['user_id'] = new_user
            return redirect('/')
        return 'sign up error'
    return render_template('signup.html', session=session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        found_user = mongodb.check_user(request.form['email'], request.form['password'])
        if found_user != None:
            session['user_id'] = found_user
            return redirect('/')
        return 'log in error'
    return render_template('login.html', session=session)

@app.route('/logout')
def logout():
    if 'user_id' not in session or session['user_id'] == None:
        return url_for('login')
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html', session=session)

@app.route('/portfolio')
def portfolio():
    if 'user_id' not in session or session['user_id'] == None:
        return redirect(url_for('login'))
    return 'portfolio'

@app.route('/account')
def account():
    if 'user_id' not in session or session['user_id'] == None:
        return redirect(url_for('login'))
    return 'account'

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', session=session)