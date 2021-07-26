# Overview
![architecture diagram](/docs/knowmore.osparc-integration.png)

# Prerequisites 
We recommend using Anaconda to create and manage your development environments for KnowMore. All the subsequent instructions are provided assuming you are using [Anaconda (Python 3 version)](https://www.anaconda.com/products/individual).

# Setup

## Clone repo
Clone the repo and submodules
```
git clone https://github.com/SPARC-FAIR-Codeathon/KnowMore.git --recurse
```
## Setup Flask
### cd into the root folder of this repo

Open Anaconda prompt (Windows) or the system Command line interface then naviguate to the KnowMore folder
```sh
$ cd ./KnowMore
```

### Setup conda env
```sh
$ conda create -n "knowmore-flask-env" python=3.6
$ conda activate knowmore-flask-env
```

### Install Python dependencies
```sh
$ conda install pip
$ pip install -r requirements.txt
```

### Setup env vars
The environment variables required are listed in the table below along with information on how to get them


<table>
<thead>
  <tr>
    <th>Suggested name</th>
    <th>Value or instructions for obtaining it</th>
    <th>Purpose</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>FLASK_ENV</td>
    <td>"development"</td>
    <td>Prod or dev</td>
  </tr>
  <tr>
    <td>SERVER_NAME</td>
    <td>"localhost:5000"</td>
    <td>server url</td>
  </tr>
  <tr>
    <td> LISTEN_PORT</td>
    <td>"5000"</td>
    <td>Port for flask app to listen to</td>
  </tr>
  <tr>
    <td>CLIENT_URL</td>
    <td>"http://localhost:3000"</td>
    <td>Sparc-App url</td>
  </tr>
  <tr>
    <td>OSPARC_TEST_MODE</td>
    <td>false</td>
    <td>whether to use test mode, so you don't have to contact osparc to develop your frontend</td>
  </tr>
  <tr>
    <td>OSPARC_API_KEY</td>
    <td> <a href="mailto: support@osparc.io"> Contact osparc support </a> </td>
    <td> Sending jobs to osparc</td>
  </tr>
  <tr>
    <td>OSPARC_API_SECRET</td>
    <td><a href="mailto: support@osparc.io"> Contact osparc support </a></td>
    <td>Sending jobs to osparc </td>
  </tr>
  <tr>
    <td>SECRET_KEY</td>
    <td></td>
    <td>flask secret key</td>
  </tr>
</tbody>
</table>


Each of them can be set in your conda environment as follows
```sh
$ conda env config vars set MY_VAR=value1 MY_OTHER_VAR=value2
```

### start flask server
```sh
$ flask run 
```

or if you require remote access: (NOTE untested)

```sh
$ flask run --host=0.0.0.0
```

### View your flask app
http://127.0.0.1:5000/

## Test mode
Want to develop without starting the osparc jobs? 

set env var (to anything other than string 'false')
```
OSPARC_TEST_MODE=true
```

This will make it so you don't actually contact osparc, but instead receive sample data back. Helpful for debugging frontend without having to wait for osparc job everytime. 

## Run in Docker
### 1) Install Docker

[See Docker's official documentation](https://docs.docker.com/get-docker/).

### 2) Create image and start container
```
docker-compose up -d
```

### 3) Check Container Status
```
docker ps
```

Should get something like this: 

```
CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS         PORTS                                                        NAMES
368be64c60c1   knowmore_flaskapp   "/entrypoint.sh /sta…"   10 seconds ago   Up 9 seconds   80/tcp, 443/tcp, 0.0.0.0:5000->5000/tcp, :::5000->5000/tcp   knowmore-flask-web-app
```

Note that this container is exposing port 5000 (the port where flask is listening) to your host.

### 4) Check and follow logs 
```
docker logs knowmore-flask-web-app -f
```

### 5) Test the endpoints
- Using browser or `curl` from your host, try out `http://localhost:5000/`.
    * Response should be: `status: up`
- Get a sample image: `http://localhost:5000/api/results-images/example-job-id/Plots-PlotID-3.7.png`
    * Flask should return the image file.

# Deploy
```
git push heroku main
```

# TODOs
- use production server, rather than dev server
- build a new docker image (current one is outdated)
- upload all files to s3 instead of to local filesystem (especially due to the nature of [Heroku's ephemeral filesystem](https://devcenter.heroku.com/articles/dynos#ephemeral-filesystem))


# Debugging
## Helpful scripts
### Test connection to osparc
```
curl http://127.0.0.1:5000/api/check-osparc-job/123e4567-e89b-12d3-a456-426614174000
# example response: {"error": "{\"errors\":[\"project 123e4567-e89b-12d3-a456-426614174000 not found\"]}", "status_code": 500}
```

### Test out the python methods without using frontend
```
python3 manual-job-starter.py
```

To not create job, but use existing job, pass in a single arg with job uuid of python job (NOT THE MATLAB JOB ID)
e.g., 
```
python3 manual-job-starter.py e9012487-5ff1-4112-aa4f-8165915973fa
```
