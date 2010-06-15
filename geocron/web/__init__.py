from flask import Flask, g, render_template, session
from geocron import settings
from geocron.location import Latitude
from geocron.web.auth import auth
from pymongo import Connection

application = Flask(__name__)
application.register_module(auth)

conn = Connection(settings.MONGODB_HOST, settings.MONGODB_PORT)

# request lifecycle

@application.before_request
def before_request():
    g.db = conn.geocron
    if 'identity' in session:
        g.user = g.db.users.find_one({'_id': session['identity']})
    else:
        g.user = None
    
@application.after_request
def after_request(response):
    return response

# application

@application.route("/")
def hello():
    
    if 'access_token' in session and 'access_secret' in session:
        l = Latitude(session['access_token'], session['access_secret'])
        content = l.current_location()
    else:
        content = ""
    
    if g.user == None:
        return render_template('hello.html', content=content)
    else:
        return render_template('rules.html')

@application.route("/users")
def user_list():
    users = g.db.users.find()
    for user in users:
        l = Latitude(user['oauth']['token'], user['oauth']['secret'])
        print l.locations(granularity='best')
    return render_template('user_list.html', users=g.db.users.find())
