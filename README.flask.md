# Overview
![architecture diagram](/docs/knowmore.osparc-integration.png)

# Setup
Clone the repo and submodules
```
git clone https://github.com/SPARC-FAIR-Codeathon/KnowMore.git --recurse
```
## Setup Flask
### cd into this folder

```sh
cd ./flask_server
```

### Setup venv
```sh
python3 -m venv venv
. venv/bin/activate
```

### Install Python dependencies
```sh
pip install -r requirements.txt
```

### Setup env vars
```sh
cp .env.example .env
```
Then change according to your environment

### start flask server
```sh
flask run 
```

or if you require remote access: (NOTE untested)

```sh
flask run --host=0.0.0.0
```

### View your flask app
http://127.0.0.1:5000/

# Deploy

```
git push heroku main
```

# Develop
## Start in Docker
**NOTE: HASN'T BEEN TESTED RECENTLY**
```
docker-compose  up -d
```

## Build a new docker image
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
