FROM python:3

RUN pip3 install -U pynetdicom &&\
    pip3 install python-dateutil

ADD script.py script.py

RUN mkdir logs


ENTRYPOINT ["python3", "script.py"]
