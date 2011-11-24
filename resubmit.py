from datetime import datetime
from xonstat_queue import *

session = dbsession()

try:
    reqs = session.query(Request).\
            filter(Request.next_check <= datetime.utcnow()).all()

    if len(reqs) > 0:
        print "Processing {0} queued requests.".format(len(reqs))
    else:
        print "No requests to process."

    for req in reqs:
        if submit_request(req):
            print "Successfully resubmitted request {0} from server {1}".\
                    format(req.request_id, req.ip_addr)
            session.delete(req)
        else:
            print "Request {0} failed. Queuing it for later resubmission.".\
                    format(req.request_id)
            req.next_check = datetime.utcnow() + \
                    timedelta(minutes=req.next_interval)
            req.next_interval = req.next_interval * 2
            session.add(req)
    session.commit()
except Exception as e:
    session.rollback()

session.close()

