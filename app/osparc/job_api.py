import requests
import os
import json
import time
import osparc
from osparc.api import FilesApi, SolversApi
from osparc.models import File, Job, JobInputs, JobOutputs, JobStatus, Solver
import pathlib
import zipfile
from pathlib import Path

OSPARC_API_KEY = os.environ.get("OSPARC_API_KEY")
OSPARC_API_SECRET = os.environ.get("OSPARC_API_SECRET")
OSPARC_TEST_MODE = os.environ.get("OSPARC_TEST_MODE", "false") != "false"

cfg = osparc.Configuration(
    username=OSPARC_API_KEY,
    password=OSPARC_API_SECRET,
)

osparc_extracted_tmp_path = "/tmp/osparc-extracted/"

current_dir = pathlib.Path(__file__).parent.resolve()
assets_dir = os.path.join(current_dir, "../..", "assets")

def start_osparc_job(data):
    """
    creates job in osparc server

    @param data ....nothing yet. But it is what we receive from frontend
    @return job info
    """

    print(osparc.__version__)
    print(cfg.host)

    if OSPARC_TEST_MODE:
        # return false job ID
        payload = {
            "job_id": "fake-job-for-testing",
            "status_code": 200,
        }

        return payload


    with osparc.ApiClient(cfg) as api_client:
        solvers_api, solver, files_api = setup_api(api_client)
        input_file1: File = files_api.upload_file(file=f"{assets_dir}/requirements-for-osparc.current.zip")
        #input_file2: File = files_api.upload_file(file=f"{assets_dir}/INPUT_FOLDER/input.xlsx")
        # TODO remove
        # testing teh zip
        input_file2: File = files_api.upload_file(file=f"{assets_dir}/INPUT_FOLDER/input.zip")

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

            # starting job after creation
            status: JobStatus = solvers_api.start_job(solver.id, solver.version, job.id)
            print("start_job result", status)
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

        return payload


def check_job_status(job_id):
    """
    check if job is done. If done, send results
    - expects teh full job dict from the frontend currently (frontend sends as json)

    @param job_id job id of the job to check
    @return dict with status, and if done then job results
    """


    # what we're returning to requester
    payload = {}

    if OSPARC_TEST_MODE or job_id == "fake-job-for-testing":
        # this is test mode, send back sucessful and mock data


        payload = {
            "download_path": "fake-path",
            "outputs": ["fake-output1", "fake-output2"],
            "finished": True,
            "progress_percent": 100,
            "success": True,
            "job_id": job_id,
            "job_state": "SUCCESS",
            "status_code": 200,
        }
        return payload


    # Ok, now for real mode:
    try:
        with osparc.ApiClient(cfg) as api_client:
            solvers_api, solver, files_api = setup_api(api_client)
            status = solvers_api.inspect_job(solver.id, solver.version, job_id)
            print("solver info:", solver.id, solver.version)

            # just check progress
            if not status.stopped_at:
                print("Solver progress", f"{status.progress}/100", flush=True)


            # Solver progress 0/100
            # Solver progress 100/100

            payload["job_id"] = job_id

            if status.state == "SUCCESS":
                outputs: JobOutputs = solvers_api.get_job_outputs(solver.id, solver.version, job_id)
                print(f"SUCCESS: Job {outputs.job_id} got these results:")

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
                print(f"Now downloading to disk path:")
                results_file: File = outputs.results["output_1"]
                print(f"file id: {results_file.id}")
                download_path: str = files_api.download_file(file_id=results_file.id)
                
                print(f"Download path: {download_path}")
                Path(osparc_extracted_tmp_path).mkdir(parents=True, exist_ok=True)

                # dir where the outputs will be written 
                tmp_dir_path_for_job_outputs = os.path.join(osparc_extracted_tmp_path, job_id)
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir_path_for_job_outputs)

                # file to read
                # right now assuming just that one file
                # would just make a loop for doing multiple files
                final_file_path = os.path.join(tmp_dir_path_for_job_outputs, "my_output_file.txt")
                plaintext_response = Path(final_file_path).read_text()
                print(plaintext_response)

                payload = {
                    "download_path": download_path,
                    "outputs": {
                        "output1": plaintext_response,
                        # for other files, add more here probably
                    },
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
        print("OSPARC ERROR:")
        print(e)
        payload = {
            "osparc_error": true,
            "error": str(e.body),
            "status_code": 500,
            "finished": True,
        }

    except Exception as e:
        # any other exception
        print("INTERNAL FLASK SERVER ERROR:")
        print(e)
        payload = {
            "error": str(e.__class__),
            "status_code": 500,
            "finished": True,
        }

    print("payload: ", payload)

    return payload


####################
# helpers
def setup_api(api_client):
    """
    helper code to get solver metadata
    """
    solvers_api = SolversApi(api_client)
    solver: Solver = solvers_api.get_solver_release(
        "simcore/services/comp/osparc-python-runner", "1.2.0"
    )
    files_api = FilesApi(api_client)
    print(solver.id, solver.version)

    return [solvers_api, solver, files_api]
