import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import datetime
import sqlite3

f = open('C:/Users/user/Desktop/text.txt', 'r')
list = f.read().strip()
file = list.split()

date = datetime.datetime.now()
id_report = 1
connect = sqlite3.connect(file[7])
cursor = connect.cursor()
sql = '''CREATE TABLE IF NOT EXISTS GODSZN
    (id_report INT, date REAL, total_issue_in_period INT, total_in_work INT, total_changes_in_period INT,
     solved_in_period INT, total_solved INT, total_fail_sla INT, prc_total_fail_sla INT,
     change_fail_sla_in_period INT, prc_change_fail_sla_in_period INT, total_issue INT)'''
cursor.execute(sql)
txt = cursor.execute("INSERT INTO GODSZN VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     (id_report, date, 0, 5, 0, 0, 0, 31, 0, 0, 0, 0))
connect.commit()
connect.close()

