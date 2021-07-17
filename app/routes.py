from flask import Flask, url_for, render_template, send_from_directory, request
from flask_cors import CORS, cross_origin
from app.osparc.job import check_job_status, start_osparc_job
import os


# avoiding error: `UserWarning: The session cookie domain is an IP address. This may not work as intended in some browsers. Add an entry to your hosts file, for example "localhost.localdomain", and use that instead` so using www.local.test
CLIENT_URL = os.environ.get("CLIENT_URL", "localhost:3000")

def set_routes(app):

    ####################################
    # Routes

    # TODO should only be our frontend server really
    @cross_origin(origin='*')
    @app.route('/')
    def index():
        return "home page. Nothing here yet, but check out <a href='/api/check-osparc-job/1'>Search</a>"

    @app.route('/test/', methods=['GET'])
    def test():

        return "test"


    @app.route('/api/start-osparc-job/', methods=['POST'])
    def create_job():
        result = start_osparc_job(request)

        return result


    @app.route('/api/check-osparc-job/', defaults={'job_id': ""}, methods=['GET'])
    @app.route('/api/check-osparc-job/<string:job_id>', methods=['GET'])
    def check_job_status(job_id):
        if job_id == "":
            return "Job ID is required"

        result = check_job_status(job_id)

        return result


    #######################

    return app

