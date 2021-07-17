from flask import make_response
import requests
import os
import json
import time
from osparc.api import FilesApi, SolversApi
from osparc.models import File, Job, JobInputs, JobOutputs, JobStatus, Solver

OSPARC_API_KEY = os.environ.get("OSPARC_API_KEY")
OSPARC_API_SECRET = os.environ.get("OSPARC_API_SECRET")

cfg = osparc.Configuration(
    username=OSPARC_API_KEY,
    password=OSPARC_API_SECRET,
)

assets_dir = os.path(os.path.abspath(os.getcwd()), "assets)"

def start_osparc_job(req):
    """
    everything needed to visualize
    creates job in osparc server
    """

    print(req)
    print("data as received:", req.data)
    print("ES json:", req.json)
    data_json = json.dumps(req.json)


    with osparc.ApiClient(cfg) as api_client:
        files_api = FilesApi(api_client)
        input_file1: File = files_api.upload_file(file=f"{assets_dir}/requirements-for-osparc.zip")
        input_file2: File = files_api.upload_file(file=f"{assets_dir}/INPUT_FOLDER/input.xlsx")

        solver: Solver = get_solver_release()
        job: Job = solvers_api.create_job(
            solver.id,
            solver.version,
            JobInputs(
            {
                "input_2": input_file2,
                "input_1": input_file1,
            }
            ),
        )

        payload = {
            "job": job,
        }

        # resp = make_response(payload.json(), payload.status_code)
        resp = make_response(json.dump(payload), payload.status_code)


def check_job_status(job_id):
    """
    check if job is done. If done, send results
    - expects teh full job dict from the frontend currently (frontend sends as json)
    """

    solver: Solver = get_solver_release()
    status: JobStatus = solvers_api.start_job(solver.id, solver.version, job_id)
    with osparc.ApiClient(cfg) as api_client:
        if not status.stopped_at:
            time.sleep(3)
            status = solvers_api.inspect_job(solver.id, solver.version, job_id)
            print("Solver progress", f"{status.progress}/100", flush=True)
        #
        # Solver progress 0/100
        # Solver progress 100/100
        outputs: JobOutputs = solvers_api.get_job_outputs(solver.id, solver.version, job_id)
        print(f"Job {outputs.job_id} got these results:")

        for output_name, result in outputs.results.items():
            print(output_name, "=", result)
        #
        # Job 19fc28f7-46fb-4e96-9129-5e924801f088 got these results:
        #
        # output_1 = {'checksum': '859fda0cb82fc4acb4686510a172d9a9-1',
        # 'content_type': 'text/plain',
        # 'filename': 'single_number.txt',
        # 'id': '9fb4f70e-3589-3e9e-991e-3059086c3aae'}
        # output_2 = 4.0
        results_file: File = outputs.results["output_1"]
        download_path: str = files_api.download_file(file_id=results_file.id)
        print(Path(download_path).read_text())

        payload = {
            "download_path": download_path,
        }

        # resp = make_response(payload.json(), payload.status_code)
        resp = make_response(json.dump(payload), payload.status_code)
        return resp


####################
# helpers
def get_solver_release():
    """
    helper code to get solver metadata
    """
    solvers_api = SolversApi(api_client)
    solver: Solver = solvers_api.get_solver_release(
        "simcore/services/comp/osparc-python-runner", "1.2.0"
    )
