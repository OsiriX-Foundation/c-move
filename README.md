# c-move

## How to test

  1. Cretate a docker network `docker network create pacs_network`
  2. Run the 2 dcm4che pacs (path docker/dcm4chee and docker/dcm4chee2)`docker-compose up`
  3. Add dicom images in the first pacs ([localhost:8080/dcm4chee-arc/ui2/#/study/study](localhost:8080/dcm4chee-arc/ui2/#/study/study)) select the aetitle DCM4CHEE More functions => Upload DICOM Object
  4. Add AETitle of the 2nd pacs in the 1st pacs
  5. [localhost:8080/dcm4chee-arc/ui2/#/device/aelist](localhost:8080/dcm4chee-arc/ui2/#/device/aelist)
  6. clic on +New AET
  7. Hostname arc
  8. Port 11113
  9. AE Title TESTCMOVE
  10. Test Connection
  11. Calling AET: DCM4CHEE
  12. TEST
  13. If OK => APPLY
  14. Run python script (path docker/python) `docker-compose up`
  15. Verify if there is data in the second pacs (localhost:5080/dcm4chee-arc/ui2/#/study/study) select the aetitle TESTCMOVE clic on SUBMIT and OK
  16. Logs are available here : `docker/python/logs`
