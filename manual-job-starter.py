from dotenv import load_dotenv

load_dotenv(verbose=True)

from app.osparc import job_api
import time

print("creating job:...")
payload = job_api.start_osparc_job("")
print(payload)
job_id = payload["job_id"]
done = False

while not done:
    print("\n\n")
    print("checking status:...")
    result = job_api.check_job_status(job_id)
    done = result["finished"]

    print(result)
    time.sleep(10)
