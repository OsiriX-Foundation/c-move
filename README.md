# c-move

## How to test

  1. Cretate a docker network `docker network create pacs_network`
  2. Run the 2 dcm4che pacs (path docker/dcm4chee and docker/dcm4chee2)`docker-compose up`
  3. Add dicom images in the first pacs (http://localhost:8080/dcm4chee-arc/ui2/#/study/study) select the aetitle DCM4CHEE More functions => Upload DICOM Object
  4. Add AETitle of the 2nd pacs in the 1st pacs
  5. http://localhost:8080/dcm4chee-arc/ui2/#/device/aelist
  6. Click on +New AET
     * Hostname arc
     * Port 11113
     * AE Title TESTCMOVE
  7. Test Connection
     * Calling AET: DCM4CHEE
     * TEST
     * If OK => APPLY
  8. Edit command in docker/python/docker-compose.yml <start_date yyyy-mm-dd> <end_date yyyy-mm-dd> <source_pacs_ip> <source_pacs_port> <source_pacs_ae_title> <destination_pacs_ae_title> (edit only the start and end date according to the dates of the study added in point 3)
  9. Run python script (path docker/python) `docker-compose up`
  10. Verify if there is data in the second pacs (http://localhost:5080/dcm4chee-arc/ui2/#/study/study) select the aetitle TESTCMOVE click on SUBMIT and OK
  11. Logs are available here : `docker/python/logs` and containes `<time> <date> <studyUID> Success` or `<time> <date> <studyUID> error <error details>`

## How use with another pacs

  1. Edit command in docker/python/docker-compose.yml <start_date yyyy-mm-dd> <end_date yyyy-mm-dd> <source_pacs_ip> <source_pacs_port> <source_pacs_ae_title> <destination_pacs_ae_title>
  2. Run python script (path docker/python) `docker-compose up`
  3. Logs are available here : `docker/python/logs`



## Docs

 - https://pydicom.github.io/pynetdicom/stable/reference/generated/pynetdicom.association.Association.html#pynetdicom.association.Association.send_c_move
 - https://pydicom.github.io/pynetdicom/dev/examples/qr_find.html
 - https://pydicom.github.io/pynetdicom/dev/examples/qr_move.html

