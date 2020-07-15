from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelMove

from dateutil.rrule import rrule, DAILY

import datetime
import sys
import functools

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
elif len(sys.argv) != 1:
    print("Usage : <start_date yyyy-mm-dd> <end_date yyyy-mm-dd> <source_pacs_ip> <source_pacs_port> <source_pacs_ae_title> <destination_pacs_ae_title>")
    exit(2)
else:
    start_date = datetime.datetime(1999, 11, 15)
    end_date = datetime.datetime(2006, 12, 31)
    source_pacs_ip = 'arc1'
    source_pacs_port = 11112
    source_pacs_ae_title = b'DCM4CHEE'
    destination_pacs_ae_title = b'TESTCMOVE'

print("************************")
print("C-MOVE from " + start_date.strftime("%Y-%m-%d") + " to " + end_date.strftime("%Y-%m-%d"))
print("source pacs { ip :" + source_pacs_ip + " port :" + str(source_pacs_port) + " ae_title :" + str(source_pacs_ae_title) + "}")
print("destination pacs { ae_title :" + str(destination_pacs_ae_title) + "}")
print("************************")

#debug_logger()


ae = AE()
ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)

ae2 = AE()
ae2.add_requested_context(StudyRootQueryRetrieveInformationModelMove)

# Create our Identifier (query) dataset
ds = Dataset()
ds.QueryRetrieveLevel = 'STUDY'
ds.StudyInstanceUID = ''

# Associate with the peer AE at IP 127.0.0.1 and port 11112

assoc = ae.associate(source_pacs_ip, source_pacs_port, ae_title = source_pacs_ae_title)
assoc2 = ae2.associate(source_pacs_ip, source_pacs_port, ae_title = source_pacs_ae_title)
if assoc.is_established and assoc2.is_established:
    for date in rrule(DAILY, dtstart=start_date, until=end_date):

        f = open("logs/log"+date.strftime("%Y-%m")+".txt", "a")

        study_uid_lst = []
        #C-FIND
        ds.StudyDate =  date.strftime("%Y%m%d")
        responses = assoc.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)
        for (status, identifier) in responses:
            if status.Status == 0xFF00:#Pending
                print(date.strftime("%Y-%m-%d"))
                print('\tstudyUID: ' + identifier.get('StudyInstanceUID'))
                study_uid_lst.append(identifier.get('StudyInstanceUID'))


        #C-MOVE
        for study_uid in study_uid_lst:

            ds2 = Dataset()
            ds2.QueryRetrieveLevel = 'STUDY'
            ds2.StudyInstanceUID = str(study_uid)
            responses2 = assoc2.send_c_move(ds2, destination_pacs_ae_title, StudyRootQueryRetrieveInformationModelMove)
            for (status2, identifier2) in responses2:
                #status : Failure, Cancel, Warning, Success, Pending
                if status2:
                    if status2.Status == 0xFF00:
                        print('Pending')
                    elif status2.Status == 0x0000:
                        print('Success')
                        print('Number of Completed Sub-operations ' + str(status2.get(0x1021).value))
                        f.write('Number of Completed Sub-operations ' + str(status2.get(0x1021).value) + ' ')
                        f.write('Number of Failed Sub-operations ' + str(status2.get(0x1022).value) + ' ')
                        f.write('Number of Warning Sub-operations ' + str(status2.get(0x1023).value) + ' ')
                        if status2.get(0x1022).value != 0 or status2.get(0x1023).value != 0:
                            f.write(date.strftime("%Y-%m-%d") +" "+ study_uid + " error")
                            f.write('Number of Failed Sub-operations ' + str(status2.get(0x1022).value))
                            f.write('Number of Warning Sub-operations ' + str(status2.get(0x1023).value) + "\r\n")
                        else:
                            f.write(date.strftime("%Y-%m-%d") +" "+ study_uid + " Success\r\n")
                    else:
                        print('status : 0x{0:04X}'.format(status2.Status))
                        print(identifier2)
                        print('Failed SOP Instance UID List ' + str(identifier2.get(0x00080058)))
                        f.write(date.strftime("%Y-%m-%d") +" "+ study_uid + " Error" + 'Failed SOP Instance UID List ' + str(identifier2.get(0x00080058)) + "\r\n")
                else:
                    print('Connection timed out, was aborted or received invalid response')
                    f.write(date.strftime("%Y-%m-%d") +" "+ study_uid + " Error\r\n")

        f.close()

    # Release the association
    assoc2.release()
    assoc.release()
else:
    print('Association rejected, aborted or never connected')
