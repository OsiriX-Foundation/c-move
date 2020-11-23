from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelMove

from dateutil.rrule import rrule, DAILY

import datetime
import time
import sys
import functools
import os


def get_c_move_association(ae_c_move, source_pacs_ip, source_pacs_port, ae_title):
    for i in range(3):
        assoc_c_move = ae_c_move.associate(source_pacs_ip, source_pacs_port, ae_title = source_pacs_ae_title)
        if assoc_c_move.is_established:
            return assoc_c_move
        else:
            if i != 2:
                print(str(datetime.datetime.now()) + ' Association (c_move) rejected, aborted or never connected (retry in 30 seconds)')
                time.sleep(30)

    print(str(datetime.datetime.now()) + ' Association (c_move) rejected, aborted or never connected')
    sys.exit()
  

print = functools.partial(print, flush=True)


if len(sys.argv) == 7:
    s = str(sys.argv[1]).split("-")
    start_date = datetime.datetime(int(s[0]), int(s[1]), int(s[2]))
    s = str(sys.argv[2]).split("-")
    end_date = datetime.datetime(int(s[0]), int(s[1]), int(s[2]))
    source_pacs_ip = str(sys.argv[3])
    source_pacs_port = int(sys.argv[4])
    source_pacs_ae_title = str.encode(sys.argv[5])
    destination_pacs_ae_title = str.encode(sys.argv[6])
else:
    print("Usage : <start_date yyyy-mm-dd> <end_date yyyy-mm-dd> <source_pacs_ip> <source_pacs_port> <source_pacs_ae_title> <destination_pacs_ae_title>")
    exit(2)


print("************************")
print("C-MOVE from " + start_date.strftime("%Y-%m-%d") + " to " + end_date.strftime("%Y-%m-%d"))
print("source pacs { ip :" + source_pacs_ip + " port :" + str(source_pacs_port) + " ae_title :" + str(source_pacs_ae_title) + "}")
print("destination pacs { ae_title :" + str(destination_pacs_ae_title) + "}")
print("************************")

#debug_logger()


ae_c_move = AE()
ae_c_move.add_requested_context(StudyRootQueryRetrieveInformationModelMove)


arr = []
for filename in os.listdir("logs"):
if filename != "empty_months.txt":
    with open("logs/"+filename) as f:
        for line in f:
            if "Error" in line:
                arr.append(line.split()[2] + " " +line.split()[3])

arr = list(dict.fromkeys(arr))
arr2 = {}
for a in arr:
    if a.split()[0] in arr2.keys():
        arr2[a.split()[0]].append(a.split()[1])
    else:
        arr2[a.split()[0]] = [a.split()[1]]


for date in rrule(DAILY, dtstart=start_date, until=end_date):

    f = open("logs2/log"+date.strftime("%Y-%m")+".txt", "a")

        
    study_uid_lst = []
    if date.strftime("%Y-%m-%d") in arr2.keys():
        study_uid_lst = arr2[date.strftime("%Y-%m-%d")]
    else:
        study_uid_lst = []


    #C-MOVE
    for study_uid in study_uid_lst:

        ds_c_move = Dataset()
        ds_c_move.QueryRetrieveLevel = 'STUDY'
        ds_c_move.StudyInstanceUID = str(study_uid)
        assoc_c_move = get_c_move_association(ae_c_move, source_pacs_ip, source_pacs_port, source_pacs_ae_title)
        try:
            responses_c_move = assoc_c_move.send_c_move(ds_c_move, destination_pacs_ae_title, StudyRootQueryRetrieveInformationModelMove)
            for (status_c_move, identifier_c_move) in responses_c_move:
                #status : Failure, Cancel, Warning, Success, Pending
                if status_c_move:
                    if status_c_move.Status == 0xFF00:
                        print('Pending (C-Move)')
                    elif status_c_move.Status == 0x0000:
                        print('Success (C-Move)')
                        print('Number of Completed Sub-operations ' + str(status_c_move.get(0x1021).value))
                        f.write(str(datetime.datetime.now()) + ' Number of Completed Sub-operations ' + str(status_c_move.get(0x1021).value) + ' ')
                        f.write('Number of Failed Sub-operations ' + str(status_c_move.get(0x1022).value) + ' ')
                        f.write('Number of Warning Sub-operations ' + str(status_c_move.get(0x1023).value) + ' ')
                        f.flush()
                        if status_c_move.get(0x1022).value != 0 or status_c_move.get(0x1023).value != 0:
                            f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" "+ study_uid + " error")
                            f.write('Number of Failed Sub-operations ' + str(status_c_move.get(0x1022).value))
                            f.write('Number of Warning Sub-operations ' + str(status_c_move.get(0x1023).value) + "\r\n")
                        else:
                            f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" "+ study_uid + " Success\r\n")
                        f.flush()
                    else:
                        stringStatus = '0x{0:04X}'.format(status_c_move.Status)
                        print('status : ' + stringStatus)
                        print(identifier_c_move)
                        if identifier_c_move is not None:
                            print('Failed SOP Instance UID List ' + str(identifier_c_move.get(0x00080058)))
                            f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" "+ study_uid + " Error with status : " + stringStatus + ' Failed SOP Instance UID List ' + str(identifier_c_move.get(0x00080058)) + "\r\n")
                        else:
                            f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" "+ study_uid + " Error with status : " + stringStatus + ' Failed SOP Instance UID List ' + "\r\n")
                        f.flush()
                else:
                    print('Connection timed out, was aborted or received invalid response')
                    f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" "+ study_uid + " Error\r\n")
                    f.flush()
        except RuntimeError:
            print(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" "+ study_uid + " RuntimeError")
            f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" "+ study_uid + " RuntimeError\r\n")
            f.flush() 
        except ValueError:
            print(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" "+ study_uid + " ValueError")
            f.write(str(datetime.datetime.now()) + " " + date.strftime("%Y-%m-%d") +" "+ study_uid + " ValueError\r\n")
            f.flush()
        finally:
            assoc_c_move.release()

    f.close()

f = open("logs2/empty_months.txt", "a")
for file in os.listdir("/logs2"):
    if file.startswith("log") and file.endswith(".txt") and os.stat("/logs2/" + file).st_size == 0:
        f.write(file.replace("log","").replace(".txt","") + "\r\n")
        f.flush()
        os.remove("/logs2/" + file)
f.close()

print('End of script')
