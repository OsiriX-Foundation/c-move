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


ae_c_find = AE()
ae_c_find.add_requested_context(StudyRootQueryRetrieveInformationModelFind)

arr = []
for filename in os.listdir("logs3"):
    if filename != "empty_months.txt":
        with open("logs3/"+filename) as f:
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

    f = open("logs4/log"+date.strftime("%Y-%m")+".txt", "a")






#C-FIND
    ds_c_find = Dataset()
    ds_c_find.StudyDate = date.strftime("%Y%m%d")
    ds_c_find.QueryRetrieveLevel = 'SERIES'
    ds_c_find.SeriesInstanceUID = ''

    try:
        assoc_c_find = get_c_find_association(ae_c_find, source_pacs_ip, source_pacs_port, source_pacs_ae_title)
        responses_c_find = assoc_c_find.send_c_find(ds_c_find, StudyRootQueryRetrieveInformationModelFind)
        for (status_c_find, identifier_c_find) in responses_c_find:
            
            if status_c_find.Status == 0xFF00:#Pending
                print(str(date.strftime("%Y-%m-%d")) + " (C-Find)")
                print('\tstudyUID: ' + identifier_c_find.get('SeriesInstanceUID'))
            else:
                print("**************************************************************************************")
                print(status_c_find.Status)
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

f = open("logs4/empty_months.txt", "a")
for file in os.listdir("/logs4"):
    if file.startswith("log") and file.endswith(".txt") and os.stat("/logs4/" + file).st_size == 0:
        f.write(file.replace("log","").replace(".txt","") + "\r\n")
        f.flush()
        os.remove("/logs4/" + file)
f.close()

print('End of script')
