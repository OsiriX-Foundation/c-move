FROM python:3

ADD combo.py combo.py

RUN pip3 install -U pynetdicom
RUN pip3 install python-dateutil

ENTRYPOINT python3 combo.py
#CMD ["python3", "combo.py"]
#CMD ["toto"]
#CMD ["python3", "combo.py", "1999-11-10", "2006-12-31", "arc1", "11112", "DCM4CHEE", "TESTCMOVE"]
