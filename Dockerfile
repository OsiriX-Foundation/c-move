FROM python:3

ADD combo.py combo.py

RUN pip3 install -U pynetdicom

ENTRYPOINT ["python3", "combo.py"]
