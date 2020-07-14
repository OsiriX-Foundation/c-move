FROM python:3

ADD combo.py combo.py

RUN pip3 install -U pynetdicom
RUN pip3 install python-dateutil

ENTRYPOINT ["python3", "combo.py"]
