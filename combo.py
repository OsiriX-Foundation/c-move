from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind

from dateutil.rrule import rrule, DAILY

import datetime
import time
import sys
import functools
import os


def get_c_find_association(ae_c_find, source_pacs_ip, source_pacs_port, ae_title):
    for i in range(3):
        assoc_c_find = ae_c_find.associate(source_pacs_ip, source_pacs_port, ae_title = source_pacs_ae_title)
        if assoc_c_find.is_established:
            return assoc_c_find
        else:
            if i != 2:
                print(str(datetime.datetime.now()) +' Association (c_find) rejected, aborted or never connected (retry in 30 seconds)')
                time.sleep(30)

    print(str(datetime.datetime.now()) + ' Association (c_find) rejected, aborted or never connected')
    sys.exit()
  

print = functools.partial(print, flush=True)


if len(sys.argv) == 9:
    s = str(sys.argv[1]).split("-")
    start_date = datetime.datetime(int(s[0]), int(s[1]), int(s[2]))
    s = str(sys.argv[2]).split("-")
    end_date = datetime.datetime(int(s[0]), int(s[1]), int(s[2]))
    source_pacs_ip = str(sys.argv[3])
    source_pacs_port = int(sys.argv[4])
    source_pacs_ae_title = str.encode(sys.argv[5])
    destination_pacs_ip = str(sys.argv[6])
    destination_pacs_port = int(sys.argv[7])
    destination_pacs_ae_title = str.encode(sys.argv[8])
else:
    print("Usage : <start_date yyyy-mm-dd> <end_date yyyy-mm-dd> <source_pacs_ip> <source_pacs_port> <source_pacs_ae_title> <destination_pacs_ip> <destination_pacs_port> <destination_pacs_ae_title>")
    exit(2)


print("************************")
print("Compare patientid study list from " + start_date.strftime("%Y-%m-%d") + " to " + end_date.strftime("%Y-%m-%d"))
print("source pacs { ip :" + source_pacs_ip + " port :" + str(source_pacs_port) + " ae_title :" + str(source_pacs_ae_title) + "}")
print("destination pacs { ip :" + destination_pacs_ip + " port :" + str(destination_pacs_port) + " ae_title :" + str(destination_pacs_ae_title) + "}")
print("************************")

#debug_logger()


ae_c_find = AE()
ae_c_find.add_requested_context(StudyRootQueryRetrieveInformationModelFind)

#ae_c_find2 = AE()
#ae_c_find2.add_requested_context(StudyRootQueryRetrieveInformationModelFind)


# Create our Identifier (query) dataset
ds_c_find = Dataset()
ds_c_find.QueryRetrieveLevel = 'STUDY'
ds_c_find.StudyInstanceUID = ''
ds_c_find.PatientName = ''


for date in rrule(DAILY, dtstart=start_date, until=end_date):

    if date.strftime("%d") == "01": print(date.strftime("%Y-%m"))

    f = open("logspatientid/log"+date.strftime("%Y-%m")+".txt", "a")

    study_uid_lst = {}
    #C-FIND
    ds_c_find.StudyDate =  date.strftime("%Y%m%d")

    try:
        assoc_c_find = get_c_find_association(ae_c_find, source_pacs_ip, source_pacs_port, source_pacs_ae_title)
        responses_c_find = assoc_c_find.send_c_find(ds_c_find, StudyRootQueryRetrieveInformationModelFind)
        for (status_c_find, identifier_c_find) in responses_c_find:
            if status_c_find.Status == 0xFF00:#Pending
                print("S:" + str(date.strftime("%Y-%m-%d")) + " (C-Find)")
                study_uid_lst[identifier_c_find.get('StudyInstanceUID')] = identifier_c_find.get('PatientName') 
    except RuntimeError:
        print(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" c-find RuntimeError")
        f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" c-find RuntimeError\r\n")
        f.flush() 
    except ValueError:
        print(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" c-find ValueError")
        f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" c-find ValueError\r\n")
        f.flush()
    finally:
        assoc_c_find.release()
  


    for studyuid in study_uid_lst.keys():
        ds_c_find1 = Dataset()
        ds_c_find1.QueryRetrieveLevel = 'STUDY'
        ds_c_find1.StudyInstanceUID = studyuid
        ds_c_find1.PatientName = ''
        try:
            assoc_c_find = get_c_find_association(ae_c_find, destination_pacs_ip, destination_pacs_port, destination_pacs_ae_title)
            responses_c_find = assoc_c_find.send_c_find(ds_c_find1, StudyRootQueryRetrieveInformationModelFind)
            for (status_c_find, identifier_c_find) in responses_c_find:
                if status_c_find.Status == 0xFF00:#Pending
                    print("D:" + str(date.strftime("%Y-%m-%d")) + " (C-Find)")
                    if str(identifier_c_find.get('PatientName')) not in study_uid_lst[studyuid]:
                        f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" "+ studyuid)
        except RuntimeError:
            print(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" c-find RuntimeError")
            f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" c-find RuntimeError\r\n")
            f.flush() 
        except ValueError:
            print(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" c-find ValueError")
            f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" c-find ValueError\r\n")
            f.flush()
        finally:
            assoc_c_find.release()
    f.close()


f = open("logspatientid/empty_months.txt", "a")
for file in os.listdir("/logspatientid"):
    if file.startswith("log") and file.endswith(".txt") and os.stat("/logspatientid/" + file).st_size == 0:
        f.write(file.replace("log","").replace(".txt","") + "\r\n")
        f.flush()
        os.remove("/logspatientid/" + file)
f.close()

print('End of script')
