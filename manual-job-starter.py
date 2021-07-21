from dotenv import load_dotenv

load_dotenv(verbose=True)

from app.osparc import job_api
import time

print("creating job:...")
dataset_dict = {"datasetIds": [60, 64, 65]}
payload = job_api.start_python_osparc_job(dataset_dict)
print(payload)
job_id = payload["job_id"]
done = False

matlab_job_id = None
while not done:
    print("\n\n")
    print("checking status:...")
    result = job_api.check_python_job_status(job_id)
    done = result["finished"]
    matlab_job_id = result["matlab_job_id"]

    time.sleep(10)

matlab_job_done = False
while not matlab_job_done:
    print("\n\n")
    print("checking MATLAB status:...")
    result = job_api.check_matlab_job_status(matlab_job_id)

    matlab_job_done = result["finished"]

