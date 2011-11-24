import requests
from datetime import datetime, timedelta
from flask import Flask, request, abort, render_template
from models import *
from sqlalchemy import create_engine

app = Flask(__name__)

url = "http://127.0.0.1:6543/stats/submit"

# database setup
engine = create_engine('sqlite://', creator=connect)
initialize_db(engine)


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
        session.rollback()
        abort(500)

    return "Success!"


@app.route("/", methods=['GET', 'POST'])
def index():
    session = dbsession()
    reqs = session.query(Request).all()
    session.close()
    if request.method == 'POST':
        print request.form.getlist('requests')
    return render_template('index.jinja', reqs=reqs)


@app.route("/request/<int:request_id>")
def request_info(request_id):
    session = dbsession()

    try:
        req = session.query(Request).\
                filter(Request.request_id==request_id).one()
    except:
        req = None

    return render_template('request_info.jinja', req=req)



def submit_request(req):
    headers = {'X-D0-Blind-Id-Detached-Signature':req.blind_id_header}
    r = requests.post(url=url, data=req.body, headers=headers)

    if r.status_code != 200:
        return False
    else:
        return True


if __name__ == "__main__":
    app.run(debug=True)
