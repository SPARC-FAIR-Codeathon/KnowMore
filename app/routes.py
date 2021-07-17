from flask import Flask, url_for, render_template, send_from_directory, request
from flask_cors import CORS, cross_origin
from app.osparc import job_api
import os


# avoiding error: `UserWarning: The session cookie domain is an IP address. This may not work as intended in some browsers. Add an entry to your hosts file, for example "localhost.localdomain", and use that instead` so using www.local.test
CLIENT_URL = os.environ.get("CLIENT_URL", "http://localhost:3000")

def set_routes(app):

    ####################################
    # Routes

    # TODO should only be our frontend server really
    @cross_origin(origin="*")
    @app.route('/')
    def index():
        return "status: up"

    @app.route('/test/', methods=['GET'])
    def test():

        return "test"


    # letting cors get setup in settings.py instead
    #@cross_origin(origin=CLIENT_URL)
    @app.route('/api/start-osparc-job/', methods=['POST'])
    def create_job():
        result = job_api.start_osparc_job(request)

        return result


    # letting cors get setup in settings.py instead
    #@cross_origin(origin=CLIENT_URL)
    @app.route('/api/check-osparc-job/', defaults={'job_id': ""}, methods=['GET'])
    @app.route('/api/check-osparc-job/<string:job_id>', methods=['GET'])
    def check_job_status(job_id):
        if job_id == "":
            return "Job ID is required"

        result = job_api.check_job_status(job_id)

        return result


    #######################

    return app

