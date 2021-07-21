from dotenv import load_dotenv
import sys

load_dotenv(verbose=True)

from app.osparc import job_api
import time

"""
To not create job, but use existing job, pass in a single arg with job uuid of python job (NOT THE MATLAB JOB ID)
e.g., python3 manual-job-starter.py "e9012487-5ff1-4112-aa4f-8165915973fa"
"""

job_id = None

args = sys.argv

if len(args) > 1:
    # Use existing job
    job_id = args[1]
    print("using existing job", job_id)

else:
    # Create job
    print("creating job:...")
    dataset_dict = {"datasetIds": [60, 64, 65]}
    payload = job_api.start_python_osparc_job(dataset_dict)
    print(payload)
    job_id = payload["job_id"]

# if job is done
done = False

matlab_job_id = None


while not done:
    print("\n\n")
    print("checking status:...")
    result = job_api.check_python_job_status(job_id)
    done = result["finished"]
    matlab_job_id = result.get("matlab_job_id", None)

    time.sleep(10)

matlab_job_done = False
while not matlab_job_done:
    print("\n\n")
    print("checking MATLAB status:...")
    result = job_api.check_matlab_job_status(matlab_job_id)

    matlab_job_done = result["finished"]

