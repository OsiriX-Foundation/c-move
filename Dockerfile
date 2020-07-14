FROM python:3

ADD cmove.py cmove.py

RUN pip3 install -U pynetdicom

CMD ["python3", "cmove.py"]
