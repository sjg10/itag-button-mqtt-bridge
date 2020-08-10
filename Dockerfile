FROM python:3

# Grab requirements and install them
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

# Grab the rest of the app
COPY ./*.py /app/
CMD python3 -u mqttbridge.py


