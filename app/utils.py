from flask import session, redirect

import string
from functools import wraps

class MenuItems:
    '''a class for holding menu items'''
    def __init__(self):
        self.items = []
    
    def add_item(self, new_item):
        for item in self.items:
            if item.label == new_item.label:
                return
        self.items.append(new_item)
    
    def __iter__(self):
        for item in self.items:
            if item.needs_login and not session['LOGGED_IN']:
                continue
            yield item
    
    def set_active(self, label):
        for item in self.items:
            if item.label == label:
                item.active = True
            else:
                item.active = False

class MenuItem:
    '''a class representing a single menu item'''
    def __init__(self, label, url, active = False, needs_login = False):
        self.label = label
        self.url = url
        self.active = active
        self.needs_login = needs_login

class GameOption:
    '''a class representing a game option'''
    def __init__(self, name, num_questions, seconds_per_question, ironman = False):
        self.name = name
        self.num_questions = num_questions
        self.seconds_per_question = seconds_per_question
        self.ironman = ironman

        self.description = '{} questions. {} seconds per question.'.format(
            num_questions, seconds_per_question)
        if ironman:
            self.description += ' 1 mistake ends the game prematurely.'
        
        self.id = name.lower()

def validate_username(username):
    for c in username:
        if c in string.ascii_letters:
            continue
        if c in string.digits:
            continue
        if c == '_':
            continue
        return False
    
    return True

def init_menu_items():
    menu_items = MenuItems()
    home = MenuItem('Home', '/')
    options = MenuItem('Options', '/options')
    profile = MenuItem('Profile', '/profile', False, True)
    leaderboard = MenuItem('Leaderboard', '/leaderboard')
    menu_items.add_item(home)
    menu_items.add_item(options)
    menu_items.add_item(profile)
    menu_items.add_item(leaderboard)
    return menu_items

def init_game_options():
    normal = GameOption('Normal', 100, 3)
    easy = GameOption('Easy', 100, 5)
    hard = GameOption('Hard', 100, 2)
    marathon = GameOption('Marathon', 500, 3)
    ironman = GameOption('Ironman', 100, 3, True)
    quickie = GameOption('Quickie', 20, 3)
    game_options = [normal, easy, hard, marathon, ironman, quickie]
    return game_options

def as_time_str(time_s):
    minutes = '{}'.format(time_s // 60)
    seconds = '{}'.format(time_s % 60)
    if len(seconds) == 1:
        seconds = '0' + seconds
    return '{}:{}'.format(minutes, seconds)

def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if not session['LOGGED_IN']:
            return redirect('/login')
        
        return f(*args, **kwargs)
    
    return inner