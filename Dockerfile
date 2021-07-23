# borrowing from https://www.digitalocean.com/community/tutorials/how-to-build-and-deploy-a-flask-application-using-docker-on-ubuntu-18-04
FROM python:3.9
#ENV STATIC_URL /static
#ENV STATIC_PATH /var/www/app/static
# will be overwritten by whatever volume we attach (for dev), but (I believe) in prod we have no volumne, so grab all the files at the start
COPY . /
RUN pip install -r /requirements.txt
CMD ["python", "main.py"]
