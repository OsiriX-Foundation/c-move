from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelMove


import datetime
import time
import sys
import functools
import os
import urllib
import requests


AET = "DCM4CHEE"
host_port = "localhost:8080"
request_url = "http://"+host_port+"/dcm4chee-arc/aets/"+AET+"/rs/studies/"+studyUID+"/reject/113039%5EDCM"
delete_url = "http://"+host_port+"/dcm4chee-arc/reject/113039%5EDCM?"

logfile = open("logsdelete/log.txt", "a")


arr = []
for filename in os.listdir("studylist"):
    if filename != "empty_months.txt":
        with open("studylist/"+filename) as f:
            for line in f:
                arr.append(line.split()[3])


for studyUID in arr:

    AET = "DCM4CHEE"
    host_port = "localhost:8080"
    request_url = "http://"+host_port+"/dcm4chee-arc/aets/"+AET+"/rs/studies/"+studyUID+"/reject/113039%5EDCM"
    response = requests.post(request_url)
    if response.status_code != 200:
        logfile.write(studyUID+" "+str(response.status_code))
        logfile.flush()




delete_url = "http://"+host_port+"/dcm4chee-arc/reject/113039%5EDCM?"
response = requests.post(delete_url)
if response.status_code != 204:
    logfile.write("Last delete "+str(response.status_code))

logfile.close()