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
    <td></td>
  </tr>
  <tr>
    <td>SERVER_NAME</td>
    <td>"localhost:5000"</td>
    <td></td>
  </tr>
  <tr>
    <td> LISTEN_PORT</td>
    <td>"5000"</td>
    <td></td>
  </tr>
  <tr>
    <td>CLIENT_URL</td>
    <td>"http://localhost:3000"</td>
    <td></td>
  </tr>
  <tr>
    <td>OSPARC_TEST_MODE</td>
    <td>false</td>
    <td></td>
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
    <td></td>
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
OSPARC_TEST_MODE=true

# Deploy
```
git push heroku main
```

# TODOs
- use production server, rather than dev server
- build a new docker image (current one is outdated)
```
# remove old container 
docker stop flask-for-podcast-tool
docker rm flask-for-podcast-tool

# write new image
docker build -t flask-for-podcast-image .

# start it again
docker run --name flask-for-podcast-tool -p 5000:5000 flask-for-podcast-image:latest
```

# Debugging
## Helpful scripts
### Test connection to osparc
```
curl http://127.0.0.1:5000/api/check-osparc-job/123e4567-e89b-12d3-a456-426614174000
# example response: {"error": "{\"errors\":[\"project 123e4567-e89b-12d3-a456-426614174000 not found\"]}", "status_code": 500}
```
