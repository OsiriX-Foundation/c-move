from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelMove

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


if len(sys.argv) == 5:
    source_pacs_ip = str(sys.argv[1])
    source_pacs_port = int(sys.argv[2])
    source_pacs_ae_title = str.encode(sys.argv[3])
    destination_pacs_ae_title = str.encode(sys.argv[4])
else:
    print("Usage : <source_pacs_ip> <source_pacs_port> <source_pacs_ae_title> <destination_pacs_ae_title>")
    exit(2)


print("************************")
print("source pacs { ip :" + source_pacs_ip + " port :" + str(source_pacs_port) + " ae_title :" + str(source_pacs_ae_title) + "}")
print("destination pacs { ae_title :" + str(destination_pacs_ae_title) + "}")
print("************************")

#debug_logger()


ae_c_move = AE()
ae_c_move.add_requested_context(StudyRootQueryRetrieveInformationModelMove)


study_uid_lst = []
for filename in os.listdir("logspatientid"):
    with open("logspatientid/"+filename) as f:
        for line in f:
            study_uid_lst.append(line.split()[3])


f = open("logtransfert/log.txt", "a")
f2 = open("logtransfert/success.txt", "a")

    

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
                        f.write(str(datetime.datetime.now()) +" "+ study_uid + " error")
                        f.write('Number of Failed Sub-operations ' + str(status_c_move.get(0x1022).value))
                        f.write('Number of Warning Sub-operations ' + str(status_c_move.get(0x1023).value) + "\r\n")
                        f.flush()
                    else:
                        f.write(str(datetime.datetime.now()) + study_uid + " Success\r\n")
                        f.flush()
                        f2.write(str(study_uid) + '\r\n')
                        f2.flush()
                else:
                    stringStatus = '0x{0:04X}'.format(status_c_move.Status)
                    print('status : ' + stringStatus)
                    print(identifier_c_move)
                    if identifier_c_move is not None:
                        print('Failed SOP Instance UID List ' + str(identifier_c_move.get(0x00080058)))
                        f.write(str(datetime.datetime.now()) +" "+ study_uid + " Error with status : " + stringStatus + ' Failed SOP Instance UID List ' + str(identifier_c_move.get(0x00080058)) + "\r\n")
                    else:
                        f.write(str(datetime.datetime.now()) +" "+ study_uid + " Error with status : " + stringStatus + ' Failed SOP Instance UID List ' + "\r\n")
                    f.flush()
            else:
                print('Connection timed out, was aborted or received invalid response')
                f.write(str(datetime.datetime.now()) + " " + study_uid + " Error\r\n")
                f.flush()
    except RuntimeError:
        print(str(datetime.datetime.now()) + " " + study_uid + " RuntimeError")
        f.write(str(datetime.datetime.now()) + " " + study_uid + " RuntimeError\r\n")
        f.flush() 
    except ValueError:
        print(str(datetime.datetime.now()) + " " + study_uid + " ValueError")
        f.write(str(datetime.datetime.now()) + " " + study_uid + " ValueError\r\n")
        f.flush()
    finally:
        assoc_c_move.release()

f.close()
f2.close()


print('End of script')
