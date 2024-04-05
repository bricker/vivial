from flask import Flask, request
import time

app = Flask(__name__)

# the all important eave rolling ctx
import threading 
glob_ctx = threading.local()

def build_this_bundle(ctx):
    """
    need to set some kind of pseudo global, that is only accessible in curr execution
    """
    global glob_ctx
    glob_ctx.ctx = ctx

def log_eave():
    global glob_ctx
    app.logger.debug("EAVE HAS LOGGED AN EVENT!!!: %s", getattr(glob_ctx, 'ctx', None))

# Define a request logger middleware
@app.before_request
def log_request_info():
    build_this_bundle(request.args)

# Define a route for GET requests at /test
@app.route('/test', methods=['GET'])
def test_route():
    db_action()
    return f"This is a test route {request.args['vis_id']}\n"

def db_action():
    time.sleep(3)
    log_eave()

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
