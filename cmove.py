from pydicom.dataset import Dataset, DataElement

from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelMove

source_pacs_ip = '172.18.32.108'
source_pacs_port = 11112
source_pacs_ae_title = b'DCM4CHEE'
destination_pacs_ae_title = b'TESTCMOVE'

#debug_logger()

# Initialise the Application Entity
ae = AE()

# Add a requested presentation context
ae.add_requested_context(StudyRootQueryRetrieveInformationModelMove)

# Create out identifier (query) dataset
ds = Dataset()
#http://dicom.nema.org/medical/dicom/current/output/chtml/part04/sect_C.6.html  (PATIENT, STUDY, SERIES, IMAGES)
ds.QueryRetrieveLevel = 'STUDY'
# Unique key for PATIENT level
#ds.StudyDate = '20060722'
#ds[0x0008, 0x0020] = DataElement(0x00080020, 'DA', '20060722')
ds.StudyInstanceUID = '*'
# Unique key for STUDY level
#ds.StudyInstanceUID = '1.3.6.1.4.1.5962.1.2.0.1175775771.5702.0'
# Unique key for SERIES level
# ds.SeriesInstanceUID = '1.2.3.4'

# Associate with peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate(source_pacs_ip, source_pacs_port, ae_title = source_pacs_ae_title)


if assoc.is_established:
    # Use the C-MOVE service to send the identifier
    responses = assoc.send_c_move(ds, destination_pacs_ae_title, StudyRootQueryRetrieveInformationModelMove)
    for (status, identifier) in responses:
        #status : Failure, Cancel, Warning, Success, Pending
        if status:
            if status.Status == 0xFF00:
                print('Pending')
            elif status.Status == 0x0000:
                print('Success')
                print('Number of Completed Sub-operations ' + str(status.get(0x1021).value))
                print('Number of Failed Sub-operations ' + str(status.get(0x1022).value))
                print('Number of Warning Sub-operations ' + str(status.get(0x1023).value))
            else:
                print('status : 0x{0:04X}'.format(status.Status))
                print('Failed SOP Instance UID List ' + str(status.get(0x00080058)))
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')
