from app import app, db, bcrypt
from app.models import *
from app.utils import (
    init_game_options, 
    init_menu_items, 
    validate_username, 
    as_time_str,
    login_required
)

from flask import (
    render_template, session, abort, request, redirect, jsonify
)

import json

menu_items = None
game_options = None

@app.before_request
def startUp():
    global menu_items, game_options

    if session.get('LOGGED_IN') is None:
        session['LOGGED_IN'] = False
    
    if menu_items is None:
        menu_items = init_menu_items()
    
    if game_options is None:
        game_options = init_game_options()

@app.errorhandler(404)
def error_404(error):
    return render_template('404.html', menu_items=menu_items), 404

@app.route('/')
@app.route('/index')
def index():
    menu_items.set_active('Home')
    return render_template('index.html', menu_items=menu_items)

@app.route('/options')
def options():
    menu_items.set_active('Options')
    return render_template('options.html', menu_items=menu_items, 
                            game_options=game_options)

@app.route('/profile')
@login_required
def profile():
    menu_items.set_active('Profile')

    curr_user = User.query.filter_by(username=session['USERNAME']).first()
    results = Result.query.filter_by(user=curr_user).all()
    sorted_results = sorted(results, key=lambda x:x.id, reverse=True)
    total_time_played = 0
    for result in results:
        total_time_played += result.total_time

    return render_template('profile.html', menu_items=menu_items,
                            results=sorted_results,
                            total_games=len(results),
                            total_time=as_time_str(total_time_played))

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html', menu_items=menu_items, errors=[])
    elif request.method == 'POST':
        errors = []
        valid = True

        username = request.form['userField']
        password = request.form['passField']

        if len(username) > 80:
            errors.append('Username must not be greater than 80 characters.')
            valid = False
        
        if len(password) > 80:
            errors.append('Password must not be greater than 80 characters.')
            valid = False
        
        if not validate_username(username):
            errors.append('Username can only contain letters, numbers, or underscores.')
            valid = False
        
        user = User.query.filter_by(username=username).first()
        if user is not None:
            errors.append('Username is already taken')
            valid = False
        
        if password != request.form['repeatField']:
            errors.append('Passwords do not match')
            valid = False
        
        if not valid:
            return render_template('signup.html', menu_items=menu_items, errors=errors)
        
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=pw_hash)
        db.session.add(new_user)
        db.session.commit()
        
        session['LOGGED_IN'] = True
        session['USERNAME'] = username
        return redirect('/')
    else:
        abort(404)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        menu_items.set_active(None)
        return render_template('login.html', menu_items=menu_items, login_error=False)
    elif request.method == 'POST':
        username = request.form['userField']
        password = request.form['passField']

        user = User.query.filter_by(username=username).first()
        if user is None:
            return render_template('login.html', menu_items=menu_items, login_error=True)
        
        if not bcrypt.check_password_hash(user.password, password):
            return render_template('login.html', menu_items=menu_items, login_error=True)
        
        session['LOGGED_IN'] = True
        session['USERNAME'] = username
        return redirect('/')
    else:
        abort(404)

@app.route('/logout', methods=['POST'])
def logout():
    session['LOGGED_IN'] = False
    session['USERNAME'] = None
    return redirect('/')

@app.route('/start', methods=['POST'])
def start_game():
    option = request.form['option']
    game_option = "countdown('{x}')".format(x=option)
    return render_template('start.html', menu_items=menu_items, 
                            game_option=game_option)

@app.route('/game', methods=['POST'])
def game():
    option = request.form['option']
    game_option = "startGame('{x}')".format(x=option)
    menu_items.set_active(None)
    return render_template('game.html', menu_items=menu_items, 
                            game_option=game_option)

@app.route('/finish', methods=['POST'])
def finish():
    game_mode = request.form['game_mode']
    num_questions = request.form['num_questions']
    num_answered = request.form['num_answered']
    num_correct = request.form['num_correct']
    accuracy = request.form['accuracy']
    final_score = float(request.form['final_score'])

    total_time = int(request.form['total_time'])
    
    if session['LOGGED_IN']:
        curr_user = User.query.filter_by(username=session['USERNAME']).first()

        result = Result(
            game_mode=game_mode.capitalize(),
            total_time=total_time,
            user=curr_user,
            final_score=final_score
        )

        db.session.add(result)
        db.session.commit()
    
    return render_template('finish.html', menu_items=menu_items,
                            game_mode=game_mode.capitalize(),
                            num_questions=num_questions,
                            num_answered=num_answered,
                            num_correct=num_correct,
                            accuracy=accuracy,
                            final_score=final_score,
                            total_time=as_time_str(total_time))

@app.route('/config/<string:option>', methods=['POST'])
def get_options(option):
    for game_option in game_options:
        if option == game_option.name.lower():
            timer_interval = game_option.seconds_per_question * 10
            return jsonify({
                'status':'ok',
                'num_questions':game_option.num_questions,
                'timer_interval':timer_interval,
                'ironman':game_option.ironman
            })
    
    return jsonify({
        'status':'error'
    })

@app.route('/leaderboard')
def leaderboard():
    menu_items.set_active('Leaderboard')

    results = Result.query.limit(10)
    return render_template('leaderboard.html', menu_items=menu_items)

@app.route('/ranks/<string:option>', methods=['POST'])
def ranks(option):
    game_mode = option.capitalize()

    results = Result.query.filter_by(game_mode=game_mode)\
                            .order_by(-Result.final_score, Result.total_time)\
                            .limit(10).all()
    
    return jsonify(
        list(map(lambda x : {
            'username':x.user.username,
            'final_score':x.final_score,
            'total_time':as_time_str(x.total_time)
        }, results))
    )