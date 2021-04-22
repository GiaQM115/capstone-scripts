FROM ubuntu:18.04
RUN apt update -y && apt upgrade -y && apt install -y python3.6 && apt install -y python3-pip && apt install -y cron
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY client_sock.py .
COPY correlate.py .
COPY send_emails.py .
COPY run.sh . 
COPY fetch.py .
COPY watchdog.sh .
COPY schedule.sh .

ENTRYPOINT ["bash"]
CMD ["run.sh"]
