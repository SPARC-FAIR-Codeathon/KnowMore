from flask import Flask, url_for, render_template, send_from_directory, request
from flask import make_response
from flask_cors import CORS, cross_origin
import json
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
        print("data as received:", request.json)
        # validate data

        dataset_dict = request.json
        if dataset_dict.get("datasetIds", False) == False:
            error_message = make_response("Invalid data: need a json with key 'datasetIds' and value an array of integers", 400)
            return error_message

        print("json:", request.json)

        payload = job_api.start_python_osparc_job(dataset_dict)

        resp = make_response(json.dumps(payload), payload["status_code"])
        return resp


    # letting cors get setup in settings.py instead
    @app.route('/api/check-osparc-job/<string:job_type>', defaults={'job_id': ""}, methods=['GET'])
    @app.route('/api/check-osparc-job/<string:job_type>/<string:job_id>', methods=['GET'])
    def check_job_status(job_type, job_id):
        if job_id == "":
            return "Job ID is required"

        if job_type == "":
            return "Job type is required (currently only two types: python or matlab)"

        elif job_type == "python":
            payload = job_api.check_python_job_status(job_id)
        elif job_type == "matlab":
            payload = job_api.check_matlab_job_status(job_id)

        resp = make_response(json.dumps(payload), payload["status_code"])
        return resp

    # e.g., http://localhost:5000/api/results-images/example-job-id/Plots-3.x.png
    @app.route('/api/results-images/<string:job_id>/<string:image_name>', methods=['GET'])
    def result_images(job_id, image_name):
        if job_id == "":
            return "Job ID is required"

        if image_name == "":
            return "image name is required"

        # for now just allow all
        # image_types = {
        #     "Plots-3.x": "Plots-3.x.png"
        # }

        # file_name = image_types[image_type]
        file_name = image_name
        print("job id:", job_id)
        print("image type:", image_name)

        file_path = os.path.join('jobs-results', job_id, file_name)
        return send_from_directory('static', file_path)

    #######################

    return app

