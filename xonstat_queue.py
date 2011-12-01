import requests
from cryptacular.bcrypt import BCRYPTPasswordManager
from datetime import datetime, timedelta
from flask import Flask, abort, flash, redirect, render_template
from flask import request, session, url_for
from flaskext.login import LoginManager, login_required, login_user
from models import *
from sqlalchemy import create_engine

###############################################################################
# CONFIGURATION
###############################################################################
SECRET_KEY = 'dfwihiewdkvh53#$%$29djgh4eSDEHFsidkehttjsshqa$#(gjd23seirnsaktrd'
app = Flask(__name__)
app.config.from_object(__name__)
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = "login"
manager = BCRYPTPasswordManager()
url = "http://127.0.0.1:6543/stats/submit"

# database setup
engine = create_engine('sqlite://', creator=connect)
initialize_db(engine)


###############################################################################
# VIEWS
###############################################################################
@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    session = dbsession()
    if request.method == 'POST':
        action = request.form.get('action')

        for id in [int(str_id) for str_id in request.form.getlist('requests')]:
            req = session.query(Request).filter(Request.request_id==id).one()
            if action == 'resubmit':
                if not submit_request(req):
                    req.next_check = datetime.utcnow() + \
                        timedelta(minutes=req.next_interval)
                    req.next_interval = req.next_interval * 2
                    session.add(req)

            elif action == 'delete':
                session.delete(req)


    reqs = session.query(Request).all()
    session.commit()
    return render_template('index.jinja', reqs=reqs, num_reqs=len(reqs))


@app.route("/submit", methods=['POST'])
def main():
    session = dbsession()
    try:
        req = Request()
        req.blind_id_header = request.headers['X-D0-Blind-Id-Detached-Signature']
        req.ip_addr = request.remote_addr
        req.body = request.data
        req.create_dt = datetime.utcnow()
        req.next_check = datetime.utcnow() + timedelta(minutes=1)
        req.next_interval = 2

        if not submit_request(req):
            session.add(req)
            session.commit()
    except Exception as e:
        print e
        session.rollback()
        abort(500)

    return "Success!"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            session = dbsession()
            user = session.query(User).filter(User.username==username).one()
        except Exception as e:
            user = User()
            user.password = ''

        if manager.check(user.password, password):
            print "Logged in successfully."
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for("index"))
        else:
            return redirect(url_for('login'))

    else:
        return render_template('login.jinja')


@app.route("/request/<int:request_id>")
@login_required
def request_info(request_id):
    session = dbsession()

    try:
        req = session.query(Request).\
                filter(Request.request_id==request_id).one()
    except:
        req = None

    return render_template('request_info.jinja', req=req)


###############################################################################
# SUPPORTING FUNCTIONS
###############################################################################
def submit_request(req):
    headers = {'X-D0-Blind-Id-Detached-Signature':req.blind_id_header,
               'X-Server-IP':req.ip_addr}
    try:
        r = requests.post(url=url, data=req.body, headers=headers)

        if r.status_code != 200:
            return False
        else:
            return True
    except Exception as e:
        return False


@login_manager.user_loader
def load_user(userid):
    session = dbsession()

    try:
        user = session.query(User).filter(User.user_id==int(userid)).one()
    except:
        user = None

    session.close()

    return user


###############################################################################
# MAIN HANDLER
###############################################################################
if __name__ == "__main__":
    app.run(debug=True)
