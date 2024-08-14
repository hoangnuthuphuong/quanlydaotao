import mysql.connector

mydb = mysql.connector.connect(user="root", password="123456", host="localhost", database="htsystem_data",
                               use_pure=False)
myCursor = mydb.cursor()


def view_all_data():
    myCursor.execute('select * from result_reporta')
    data = myCursor.fetchall()
    return data

def week_training_reportabc():
    myCursor.execute('select * from week_training_reportabc')
    week_data = myCursor.fetchall()
    return week_data


def result_report():
    myCursor.execute('select * from result_reporta')
    result_data = myCursor.fetchall()
    result_data = result_data.fillna('0')
    return result_data