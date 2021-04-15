
#######################################
#Warning
#You need to enable less secure app from your google account
#https://myaccount.google.com/lesssecureapps
#######################################
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mysql.connector
from getpass import getpass

def send_email(email_from, email_pass, email_to, subject, msg):
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = email_from
    message['To'] = email_to
    message['Subject'] = subject  #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(msg, 'plain'))
    #Create SMTP session for sending the mail
    sender_session = session(email_from, email_pass)
    text = message.as_string()
    sender_session.sendmail(email_from, email_to, text)
    sender_session.quit()
    print('Mail Sent To {}'.format(email_to))


#The mail addresses and password
def session(email_from, email_from_pass):
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(email_from, email_from_pass) #login with mail_id and password
    return session

def get_emails(group):
    mydb = mysql.connector.connect(
        host='192.168.1.4',
        port=3000,
        user = 'admin',
        password = 'Password-123',
        database = 'usermgt'
    )

    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT email FROM mappings where GNAME='{group}'")

    myresult = mycursor.fetchall()
    email_list = []
    for query in myresult:
        email_list.append(query[0])
        
    return email_list


"""
def read_csv_email(file_name):
    TO_EMAILs = []
    with open('contact_info.csv', 'r') as file:
        reader = csv.reader(file)
        counter=0
        for row in reader:
            if counter == 0:
                pass
                counter = counter+1
            else: 
                counter = counter+1
                email = row
                TO_EMAILs.append(email)
    return TO_EMAILs
"""
def generate_msg(tags, alert, contacts):
    msg = "Hello {}, we have a new alert corresponding to {} that requires immediate attention. Here's what we found. {}".format(contacts, tags, alert)
    return msg

# def get_alerts(filename):
#     alert_json = []
#     with open(file_name, 'r') as file:
#         reader = csv.reader(file)
#         counter=0
#         for row in reader:
#             if counter == 0:
#                 pass
#                 counter = counter+1
#             else: 
#                 counter = counter+1
#                 alert = row[1]
#                 alert_json.append(alert)
#     return alert_json

def send_emails(group): 
    #The mail addresses and password
    FROM_EMAIL = "aproject490@gmail.com"
    FROM_EMAIL_PASS = getpass() 
    path = '/home/student/contact_info.csv' #path of the csv file that has the information of the receiver end
    Contacts = get_emails(group)
    print(Contacts)
    for contact in Contacts:
        name = contact[0]
        email = contact[1]
        group = contact[2]
        tags = "malicious activity"
        alert = "json Alert blah blah"
        subject = 'IMMEDIATE ATTENTION REQUIRED:{}'.format(tags)
        msg = generate_msg(tags, alert, name)
        #send_email(FROM_EMAIL, FROM_EMAIL_PASS,email, subject, msg)
send_emails("Network")




