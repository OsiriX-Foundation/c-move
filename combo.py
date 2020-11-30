from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind

from dateutil.rrule import rrule, DAILY

import datetime
import time
import sys
import functools
import os


def get_c_find_association(ae_c_find, pacs_ip, pacs_port, ae_title):
    for i in range(3):
        assoc_c_find = ae_c_find.associate(pacs_ip, pacs_port, ae_title = ae_title)
        if assoc_c_find.is_established:
            return assoc_c_find
        else:
            if i != 2:
                print(str(datetime.datetime.now()) +' Association (c_find) rejected, aborted or never connected (retry in 30 seconds)')
                time.sleep(30)

    print(str(datetime.datetime.now()) + ' Association (c_find) rejected, aborted or never connected')
    sys.exit()
  

print = functools.partial(print, flush=True)


if len(sys.argv) == 7:
    source_pacs_ip = str(sys.argv[1])
    source_pacs_port = int(sys.argv[2])
    source_pacs_ae_title = str.encode(sys.argv[3])
    destination_pacs_ip = str(sys.argv[4])
    destination_pacs_port = int(sys.argv[5])
    destination_pacs_ae_title = str.encode(sys.argv[6])
else:
    print("Usage : <source_pacs_ip> <source_pacs_port> <source_pacs_ae_title> <destination_pacs_ip> <destination_pacs_port> <destination_pacs_ae_title>")
    exit(2)


print("************************")
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
ds_c_find.PatientName = ''



for filename in os.listdir("logspatientid"):
    if filename != "empty_months.txt":
        with open("logspatientid/"+filename) as f:
            print(filename)
            for line in f:
                line = line.split()

                f = open("logspatientid2/"+filename, "a")

                study_uid_lst = {}
                #C-FIND
                ds_c_find.StudyInstanceUID = line[3]

                try:
                    assoc_c_find = get_c_find_association(ae_c_find, destination_pacs_ip, destination_pacs_port, destination_pacs_ae_title)
                    responses_c_find = assoc_c_find.send_c_find(ds_c_find, StudyRootQueryRetrieveInformationModelFind)
                    for (status_c_find, identifier_c_find) in responses_c_find:
                        if status_c_find.Status == 0xFF00:#Pending
                            study_uid_lst[identifier_c_find.get('StudyInstanceUID')] = str(identifier_c_find.get('PatientName')) 
                except RuntimeError:
                    print(str(datetime.datetime.now()) + " " + line[2] +" c-find RuntimeError")
                    f.write(str(datetime.datetime.now()) + " " + line[2] +" c-find RuntimeError\r\n")
                    f.flush() 
                except ValueError:
                    print(str(datetime.datetime.now()) + " " + line[2] +" c-find ValueError")
                    f.write(str(datetime.datetime.now()) + " " + line[2] +" c-find ValueError\r\n")
                    f.flush()
                finally:
                    assoc_c_find.release()
            


                for studyuid in study_uid_lst.keys():
                    ds_c_find1 = Dataset()
                    ds_c_find1.QueryRetrieveLevel = 'STUDY'
                    ds_c_find1.StudyInstanceUID = studyuid
                    ds_c_find1.PatientName = ''
                    ds_c_find1.PatientID = ''
                    try:
                        assoc_c_find = get_c_find_association(ae_c_find, source_pacs_ip, source_pacs_port, source_pacs_ae_title)
                        responses_c_find = assoc_c_find.send_c_find(ds_c_find1, StudyRootQueryRetrieveInformationModelFind)
                        for (status_c_find, identifier_c_find) in responses_c_find:
                            if status_c_find.Status == 0xFF00:#Pending
                                if str(identifier_c_find.get('PatientName')) not in str(study_uid_lst[studyuid]):
                                    print("error")
                                    f.write(str(datetime.datetime.now()) + " " + line[2] +" "+ studyuid + " " + str(identifier_c_find.get('PatientID')) + " ___" + str(identifier_c_find.get('PatientName')) + "---" + str(study_uid_lst[studyuid]) +"\r\n")
                    except RuntimeError:
                        print(str(datetime.datetime.now()) + " " + line[2] +" c-find RuntimeError")
                        f.write(str(datetime.datetime.now()) + " " + line[2] +" c-find RuntimeError\r\n")
                        f.flush() 
                    except ValueError:
                        print(str(datetime.datetime.now()) + " " + line[2] +" c-find ValueError")
                        f.write(str(datetime.datetime.now()) + " " + line[2] +" c-find ValueError\r\n")
                        f.flush()
                    finally:
                        assoc_c_find.release()
                f.close()


print('End of script')
