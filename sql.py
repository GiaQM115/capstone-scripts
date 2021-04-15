import mysql.connector


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

    for x in myresult:
        print(x[0])

get_emails("Network")
