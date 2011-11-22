import requests
from datetime import datetime, timedelta
from flask import Flask, request
from models import *
from sqlalchemy import create_engine

app = Flask(__name__)

url = "http://127.0.0.1:6543/stats/submit"

# database setup
engine = create_engine('sqlite://', creator=connect)
initialize_db(engine)

@app.route("/", methods=['POST'])
def log_request():
    session = dbsession()

    try:
        req = Request()
        req.blind_id_header = request.headers['X-D0-Blind-Id-Detached-Signature']
        req.body = request.data
        req.create_dt = datetime.utcnow()
        req.next_check = datetime.utcnow() + timedelta(minutes=1)
        req.next_interval = 2

        try_request(req)
        session.add(req)
    except e:
        session.rollback()

    session.commit()
    return "Success!"

def try_request(req):
    headers = {'X-D0-Blind-Id-Detached-Signature':req.blind_id_header}
    r = requests.post(url=url, data=req.body, headers=headers)


if __name__ == "__main__":
    app.run(debug=True)