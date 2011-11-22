import requests
from datetime import datetime, timedelta
from flask import Flask, request, abort
from models import *
from sqlalchemy import create_engine

app = Flask(__name__)

url = "http://127.0.0.1:6543/stats/submit"

# database setup
engine = create_engine('sqlite://', creator=connect)
initialize_db(engine)


@app.route("/", methods=['POST'])
def main():
    session = dbsession()
    try:
        req = Request()
        req.blind_id_header = request.headers['X-D0-Blind-Id-Detached-Signature']
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


def submit_request(req):
    headers = {'X-D0-Blind-Id-Detached-Signature':req.blind_id_header}
    r = requests.post(url=url, data=req.body, headers=headers)

    if r.status_code != 200:
        return False
    else:
        return True


def resubmit_loop():
    session = dbsession()
    try:
        reqs = session.query(Request).\
                filter_by(next_check <= datetime.utcnow()).all()

        for req in reqs:
            if submit_request(req):
                session.delete(req)
            else:
                req.next_check = datetime.utcnow() + \
                        timedelta(minutes=req.next_interval)
                req.next_interval = req.next_interval * 2
                session.add(req)
        session.commit()
    except Exception as e:
        session.rollback()

    session.close()


if __name__ == "__main__":
    app.run(debug=True)
