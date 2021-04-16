
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

misp_url = 'https://192.168.1.4/events/view/'

def send(email_from, email_pass, email_to, subject, msg):
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

def get_emails(tags):
    mydb = mysql.connector.connect(
        host='192.168.1.4',
        port=3000,
        user = 'admin',
        password = 'Password-123',
        database = 'usermgt'
    )
    email_set = set()
    mycursor = mydb.cursor()
    for tag in tags:
        mycursor.execute(f"SELECT mappings.EMAIL from mappings inner join groups on groups.GNAME = mappings.GNAME inner join events on groups.NOTIFY = events.NAME where events.IDENTIFIER = '{tag}'")
        myresult = mycursor.fetchall()
        for query in myresult:
            email_set.add(query[0])
    print(email_set)
    return email_set


def generate_msg(event, tags):
    global misp_url
    msg = f"Hello, we have a new alert corresponding to Event {event} that requires immediate attention. Tags found on the event are {tags}. For more information go to the MISP Dashboard: {misp_url}{event}"
    return msg

def send_emails(event, tags): 
    #The mail addresses and password
    FROM_EMAIL = "aproject490@gmail.com"
    #FROM_EMAIL_PASS = getpass() 
    FROM_EMAIL_PASS = "Possum@490"
    Contacts = get_emails(tags)
    print(Contacts)
    for contact in Contacts:
        email = contact
        subject = f'MISP ALERT EVENT {event}'
        msg = generate_msg(event, tags)
        send(FROM_EMAIL, FROM_EMAIL_PASS,email, subject, msg)




