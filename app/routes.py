from app import app
from flask import render_template, redirect, session, request
from app import mongodb

@app.route('/')
@app.route('/home')
def index():
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
    session.pop('user_id', None)
    return redirect('/')