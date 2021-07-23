import requests
import os
import json
import time
import uuid
import osparc
from osparc.api import FilesApi, SolversApi
from osparc.models import File, Job, JobInputs, JobOutputs, JobStatus, Solver
import pathlib
import zipfile
from pathlib import Path
from .sample_outputs import sample_output

OSPARC_API_KEY = os.environ.get("OSPARC_API_KEY")
OSPARC_API_SECRET = os.environ.get("OSPARC_API_SECRET")
OSPARC_TEST_MODE = os.environ.get("OSPARC_TEST_MODE", "false") != "false"

cfg = osparc.Configuration(
    username=OSPARC_API_KEY,
    password=OSPARC_API_SECRET,
)

# set some vars up front so we can adjust later if we need to not break everything
osparc_extracted_tmp_path = os.path.join("tmp", "osparc-extracted")

current_dir = pathlib.Path(__file__).parent.resolve()

static_dir = os.path.join(current_dir, "..", "..", "static")
input_assets_dir = os.path.join(current_dir, "..", "..", "assets", "INPUT_FOLDER")
# key of output received from osparc to use 
output_result_to_use = "output_1"





def start_python_osparc_job(dataset_info):
    """
    @param dataset_info dict with single key: "datasetIds" which has value of an array of pennsieve ids (integers)
    """

    # create dir for this request
    # we don't know job id yet, so just make a uuid for this request
    asset_dirname_for_job = str(uuid.uuid4())
    asset_dir_for_job = os.path.join(input_assets_dir, "tmp", asset_dirname_for_job)
    path_for_input_json = os.path.join(asset_dir_for_job, "input.json")
    os.mkdir(asset_dir_for_job)

    # write our input to file
    with open(path_for_input_json, 'w') as input_file_json:
        #json.dump({"datasetIds": [60, 64, 65]}, input_file_json)
        json.dump(dataset_info, input_file_json)

    main_input_zip_path = os.path.join(input_assets_dir, "main.zip")

    input_file_paths = {
        "input_1": main_input_zip_path,
        "input_2": path_for_input_json,
    }

    payload = start_osparc_job("python", input_file_paths)

    return payload


def start_matlab_osparc_job(matlab_zip_filepath):
    """
    @param matlab_zip_filepath path to the matlab-input-folder.zip
    """
    input_file_paths = {
        "input_1": matlab_zip_filepath,
    }

    payload = start_osparc_job("matlab", input_file_paths)

    return payload

def start_osparc_job(job_type, input_file_paths):
    """
    uploads files according to paths passed in
    Then creates job in osparc server

    @param input_file_paths dict paths to files to upload. Keys will be used for keys to send to osparc
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
        solvers_api, solver, files_api = setup_api(job_type, api_client)

        # clone the dict for a new dict to send to osparc
        job_inputs = dict(input_file_paths)

        for key, input_file_path in input_file_paths.items():
            print("upload input found at:", input_file_path)
            input_file: File = files_api.upload_file(file=input_file_path)
            # set to respective key for the dict to send to osparc
            job_inputs[key] = input_file

        print("job inputs dict:", job_inputs)
        try:
            job: Job = solvers_api.create_job(
                solver.id,
                solver.version,
                JobInputs(job_inputs),
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

        # TODO can now remove the tmp assets dir for job we made
        return payload


def check_python_job_status(job_id):
    """
    Check status of the python job in osparc
    - if finished, unzips results and sends json to frontend. 
    - zip received from python osparc job also has a matlab.zip that is sent back to osparc to start a matlab osparc job.
    """

    payload = check_job_status("python", job_id)
    
    if payload.get("success", False):
        # get outputs. Unzip to a different tmp path for now, then just get the plaintext response to send to frontend
        dir_path_for_job_outputs = unzip_osparc_outputs(job_id, payload["download_path"], osparc_extracted_tmp_path)

        # file in the output that has the json that we expect from python osparc job
        # right now assuming just that one file
        # would just make a loop for doing multiple files
        final_json_file_path = os.path.join(dir_path_for_job_outputs, "output.json")

        plaintext_response = Path(final_json_file_path).read_text()
        print(plaintext_response)

        # add outputs to payload before returning to the front and
        payload["outputs"] = {
            "output1": json.loads(plaintext_response),
        }

        # also start matlab job. create job to get the job ID so frontend knows what job to poll for, but start job asyncronously for now
        matlab_zip_filepath = os.path.join(dir_path_for_job_outputs, "matlab-input-folder.zip")

        try:
            matlab_job_payload = start_matlab_osparc_job(matlab_zip_filepath)
            payload["matlab_job_id"] = matlab_job_payload["job_id"]
        except Exception as e:
            # don't want the whole thing to fail if the matlab part doesn't run
            print("failed to create matlab job, just continue on without that")
            print(e)


        # also move this Correlation_heatmap.png image to static dir so frontend can grab it
        # note that other images will be in static dir under the matlab osparc job ID, this one under the python osparc job id
        # again, don't let whole job fail if this doesn't work
        try:
            # take from subdir in /tmp 
            correlation_png_source_file_path = os.path.join(dir_path_for_job_outputs, "Correlation_heatmap.png")
            # place in static dir
            dest_dir_path_for_correlation_png = get_static_dir_for_job(job_id)

            # create destination dir first
            Path(dest_dir_path_for_correlation_png).mkdir(parents=True, exist_ok=True)

            # path to the file within that dir
            correlation_png_destination_file_path = os.path.join(dest_dir_path_for_correlation_png, "Correlation_heatmap.png")

            os.rename(correlation_png_source_file_path, correlation_png_destination_file_path)

        except Exception as e:
            # don't want the whole thing to fail if the matlab part doesn't run
            print(e)
            print("failed to move correlation heatmap, just continue on without that")



    return payload

def check_matlab_job_status(job_id):
    """
    Check status of the matlab job in osparc
    - if finished, unzips results and puts in static folder for frontend to view
    """
    payload = check_job_status("matlab", job_id)

    if payload.get("success", False):
        # get outputs. Unzip to static dir so frontend can read the image path
        # unzip_osparc_outputs will namespace by job id
        static_dir_for_job = os.path.join(static_dir, "jobs-results")
        dir_path_for_job_outputs = unzip_osparc_outputs(job_id, payload["download_path"], static_dir_for_job)

        # let's send the matlab json as well...if we can
        # TODO fix the json, right now there's some commas that are messesd up. So for now make this optinoal
        try:
            final_json_file_path = os.path.join(dir_path_for_job_outputs, "matlab_output.json")
            plaintext_response = Path(final_json_file_path).read_text()

            payload["outputs"] = {
                "matlab_output": json.loads(plaintext_response)
            }

        except Exception as e:
            # any other exception
            print("INTERNAL FLASK SERVER ERROR:")
            print(e)
            print("don't need it, continuing on")

    # don't need to return outputs to the front end, just tell the front and that we are done, and frontend can then retrieve images from the flask static folder
    return payload


def check_job_status(job_type, job_id):
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
            "outputs": sample_output,
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
            solvers_api, solver, files_api = setup_api(job_type, api_client)
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

                # we're only taking the first one
                print(f"Now downloading to disk path:")
                results_file: File = outputs.results[output_result_to_use]
                #print(f"file id: {results_file.id}")
                download_path: str = files_api.download_file(file_id=results_file.id)
                
                print(f"Download path: {download_path}")

                payload = {
                    "download_path": download_path,
                    "finished": True,
                    "progress_percent": status.progress,
                    "success": True,
                    "job_id": job_id,
                    "job_state": status.state,
                    "status_code": 200,
                }

                return payload



            elif status.state in ["ABORTED", "FAILED"]:
                # Something went wrong in OSPARC, user should not keep retrying
                print("status for osparc job:", status)

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
        print(e.body)
        payload = {
            "osparc_error": True,
            "error": str(e.body),
            "status_code": 500,
            "success": False,
            "job_id": job_id,
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
            "success": False,
            "job_id": job_id,
        }

    print("payload: ", payload)

    return payload


####################
# helpers
def setup_api(job_type, api_client):
    """
    helper code to get solver metadata
    """

    solver_types = {
        "python": {
            "runner": "simcore/services/comp/osparc-python-runner",
            "version": "1.2.0"
        },
        "matlab": {
            "runner": "simcore/services/comp/mat-parser",
            "version": "1.1.0",
        }
    }

    solvers_api = SolversApi(api_client)
    solver: Solver = solvers_api.get_solver_release(
        solver_types[job_type]["runner"],
        solver_types[job_type]["version"],
    )

    files_api = FilesApi(api_client)
    print(solver.id, solver.version)

    return [solvers_api, solver, files_api]

def unzip_osparc_outputs(job_id, download_path, target_unzip_dir_path):
    """
    @param target_unzip_dir_path where to unzip the output_1 zip to. This script will add a subdirectory based on job_id to namespace the different files
    @return dir_path_for_job_outputs, where the unzipped files got put
    """
    # namespace using subdirectory based on job id
    # TODO use get_static_dir_for_job instead, to DRY up code
    dir_path_for_job_outputs = os.path.join(target_unzip_dir_path, job_id)

    # make sure target dir exists if not already
    Path(dir_path_for_job_outputs).mkdir(parents=True, exist_ok=True)

    # dir where the outputs will be written 
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(dir_path_for_job_outputs)

    return dir_path_for_job_outputs

def get_static_dir_for_job(job_id):
    """
    takes job_id and returns the static dir for that job, where frontend can access it
    """
    dir_path_for_job_outputs = os.path.join(static_dir, "jobs-results", job_id)

    return dir_path_for_job_outputs
