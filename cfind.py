from pydicom.dataset import Dataset

from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind
import datetime
from dateutil.rrule import rrule, DAILY

start_date = datetime.datetime(1999, 1, 1)
end_date = datetime.datetime(2006, 12, 31)
source_pacs_ip = '172.18.32.108'
source_pacs_port = 11112
source_pacs_ae_title = b'DCM4CHEE'

#string_date = start_date.strftime("%Y%m%d")
#print(string_date)
#next_date = start_date + datetime.timedelta(days=1)
#print (next_date)

#debug_logger()

ae = AE()
ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)

# Create our Identifier (query) dataset
ds = Dataset()
ds.QueryRetrieveLevel = 'STUDY'
ds.StudyInstanceUID = ''

# Associate with the peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate(source_pacs_ip, source_pacs_port, ae_title = source_pacs_ae_title)

if assoc.is_established:

    for date in rrule(DAILY, dtstart=start_date, until=end_date):

        ds.StudyDate =  date.strftime("%Y%m%d")
        responses = assoc.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)
        for (status, identifier) in responses:
            if status.Status == 0xFF00:#Pending
                print('studyUID: ' + identifier.get('StudyInstanceUID'))
                print(date.strftime("%Y-%m-%d"))







    # Send the C-FIND request
    #responses = assoc.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)
    #for (status, identifier) in responses:
        #if status:
        #    print('C-FIND query status: 0x{0:04X}'.format(status.Status))
        #else:
        #    print('Connection timed out, was aborted or received invalid response')


        #if status.Status == 0xFF00:#Pending
            #print("studyUID: "+identifier.get('StudyInstanceUID'))
    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')
