from flask import make_response
import requests
import os
import json
import time
import osparc
from osparc.api import FilesApi, SolversApi
from osparc.models import File, Job, JobInputs, JobOutputs, JobStatus, Solver

OSPARC_API_KEY = os.environ.get("OSPARC_API_KEY")
OSPARC_API_SECRET = os.environ.get("OSPARC_API_SECRET")

cfg = osparc.Configuration(
    username=OSPARC_API_KEY,
    password=OSPARC_API_SECRET,
)

working_dir = os.path.abspath(os.getcwd())
assets_dir = os.path.join(working_dir, "assets")

def start_osparc_job(req):
    """
    creates job in osparc server

    @return job info
    """

    print(req)
    print("data as received:", req.data)
    print("json:", req.json)


    with osparc.ApiClient(cfg) as api_client:
        files_api = FilesApi(api_client)
        input_file1: File = files_api.upload_file(file=f"{assets_dir}/requirements-for-osparc.current.zip")
        input_file2: File = files_api.upload_file(file=f"{assets_dir}/INPUT_FOLDER/input.xlsx")

        solvers_api, solver = setup_solver(api_client)

        try:
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

            print("job we got", job)
            payload = {
                "job_id": job.id,
                "status_code": 200,
            }

        except Exception as e:
            print(e)
            payload = {
                "error": e,
                "status_code": 500,
            }

        resp = make_response(json.dumps(payload), payload["status_code"])
        return resp


def check_job_status(job_id):
    """
    check if job is done. If done, send results
    - expects teh full job dict from the frontend currently (frontend sends as json)

    @param job_id job id of the job to check
    @return dict with status, and if done then job results
    """


    # what we're returning to requester
    payload = {}

    try:
        with osparc.ApiClient(cfg) as api_client:
            solvers_api, solver = setup_solver(api_client)
            status = solvers_api.inspect_job(solver.id, solver.version, job_id)

            # just check progress
            if not status.stopped_at:
                print("Solver progress", f"{status.progress}/100", flush=True)


            # Solver progress 0/100
            # Solver progress 100/100

            payload["job_id"] = job_id

            if status.state == "SUCCESS":
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
                    "outputs": outputs,
                    "finished": True,
                    "progress_percent": status.progress,
                    "success": True,
                    "job_id": job_id,
                    "job_state": status.state,
                    "status_code": 200,
                }



            elif status.state in ["ABORTED", "FAILED"]:
                # Something went wrong in OSPARC, user should not keep retrying
                payload = {
                    "finished": True,
                    "success": False,
                    "progress_percent": status.progress,
                    "job_id": job_id,
                    "job_state": status.state,
                    "status_code": 500,
                }

            else:
                # not done yet, user should keep polling 
                payload = {
                    "finished": False,
                    "success": False,
                    "progress_percent": status.progress,
                    "job_id": job_id,
                    "job_state": status.state,
                    "status_code": 200,
                }

    except osparc.exceptions.ApiException as e:
        # exception returned by osparc
        print(e)
        payload = {
            "error": str(e.body),
            "status_code": 500,
        }

    except Exception as e:
        # any other exception
        print(e)
        payload = {
            "error": str(e.__class__),
            "status_code": 500,
        }

    print("payload: ", payload)

    resp = make_response(json.dumps(payload), payload["status_code"])
    return resp


####################
# helpers
def setup_solver(api_client):
    """
    helper code to get solver metadata
    """
    solvers_api = SolversApi(api_client)
    solver: Solver = solvers_api.get_solver_release(
        "simcore/services/comp/osparc-python-runner", "1.2.0"
    )

    return [solvers_api, solver]