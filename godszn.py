from jira import JIRA
import requests
import shutil
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json
from datetime import datetime
import sqlite3

f = open('C:/Users/user/Desktop/text.txt', 'rb')
list = f.read().strip()
file = list.split()
date = datetime.now().strftime('%Y-%m-%d')

#############   Подключение к серверу jira

jira_options = {'server': 'https://job-jira.itargo.ru/', 'verify': False}
jira = JIRA(options=jira_options, basic_auth=(file[0], file[1]))

# ВЫГРУЗКА PDF

jira_pdf = 'https://job-jira.itargo.ru/rest/com.midori.jira.plugin.pdfview/1.0/pdf/pdf-view/20/dashboard/10301/render?context=dashboard'
file_pdf = requests.get(jira_pdf, auth=(file[0], file[1]), stream=True, verify=False)
file_pdf.raise_for_status()
file_pdf.raw.decode_content = True
with open(file[11], 'wb') as file:
    shutil.copyfileobj(file_pdf.raw, file)

#Данные из прошлого отчета
f = open('C:/Users/user/Desktop/text.txt', 'r')
list = f.read().strip()
file = list.split()


data_b = file[7]
connect = sqlite3.connect(data_b)
cursor = connect.cursor()
tmp_id = 'SELECT MAX(id_report) FROM GODSZN'
cursor.execute(tmp_id)
old_id = cursor.fetchone()[0]
new_id = old_id + 1
connect.close()

connect = sqlite3.connect(data_b)
cursor = connect.cursor()
tmp_total_fail_sla = 'SELECT total_fail_sla FROM GODSZN WHERE id_report = (SELECT MAX(id_report) FROM GODSZN)'
cursor.execute(tmp_total_fail_sla)
old_total_fail_sla = cursor.fetchone()[0]
connect.close()

connect = sqlite3.connect(data_b)
cursor = connect.cursor()
tmp_total_in_work = 'SELECT total_in_work FROM GODSZN WHERE id_report = (SELECT MAX(id_report) FROM GODSZN)'
cursor.execute(tmp_total_in_work)
old_total_in_work = cursor.fetchone()[0]
connect.close()

# Выгрузка issue, подсчет задачь

total_issue = jira.search_issues('project=GODSZN', maxResults=False)
total_issue = len(total_issue)

total_issue_in_period = jira.search_issues('project= GODSZN AND created > -7d', maxResults=False)
total_issue_in_period = len(total_issue_in_period)
total_in_work = jira.search_issues('project = GODSZN AND status in '
                              '(Open, "В работе 1 линии", "В работе 2 линии",'
                              ' "Запрос информации", "Передано заказчику")', maxResults=False)
total_in_work = len(total_in_work)
total_changes_in_period = total_in_work - old_total_in_work
solved_in_period = jira.search_issues('project = GODSZN AND resolved >= -7d', maxResults=False)
solved_in_period = len(solved_in_period)
total_solved = jira.search_issues('project = GODSZN AND status in (Closed, Решено)', maxResults=False)
total_solved = len(total_solved)
total_fail_sla = jira.search_issues('project = GODSZN AND "Срок нарушен" = Да', maxResults=False)
total_fail_sla = len(total_fail_sla)
prc_total_fail_sla = (total_fail_sla * 100) // total_issue
change_fail_sla_in_period = total_fail_sla - old_total_fail_sla
prc_change_fail_sla_in_period = (change_fail_sla_in_period * 100) // total_fail_sla

############# Заносим результаты в DB (за отчетную неделю)

connect = sqlite3.connect(data_b)
cursor = connect.cursor()
sql = '''CREATE TABLE IF NOT EXISTS GODSZN
    (id_report INT, date REAL, total_issue_in_period INT, total_in_work INT, total_changes_in_period INT,
     solved_in_period INT, total_solved INT, total_fail_sla INT, prc_total_fail_sla INT,
     change_fail_sla_in_period INT, prc_change_fail_sla_in_period INT, total_issue INT)'''
cursor.execute(sql)
txt = cursor.execute("INSERT INTO GODSZN VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     (new_id, date, total_issue_in_period, total_in_work, total_changes_in_period,
                      solved_in_period, total_solved, total_fail_sla, prc_total_fail_sla,
                      change_fail_sla_in_period, prc_change_fail_sla_in_period, total_issue))
connect.commit()
connect = sqlite3.connect(data_b)
connect.row_factory = sqlite3.Row
cursor = connect.cursor()
sql = 'SELECT * FROM GODSZN WHERE id_report = (SELECT MAX(id_report) FROM GODSZN)'
cursor.execute(sql)
result = cursor.fetchall()[0]
connect.close()

############# Выгрузка финального отчета в json
f = open('C:/Users/user/Desktop/text.txt', 'r')
list = f.read().strip()
file = list.split()


connect = sqlite3.connect(data_b)
cursor = connect.cursor()
sql = 'SELECT * FROM GODSZN WHERE id_report = (SELECT MAX(id_report) FROM GODSZN)'
cursor.execute(sql)
rows = cursor.fetchall()[0]
connect.close()
jira_json = rows
db = file[10]
with open(db, 'w') as f:
    json.dump(jira_json, f)

#ОТПРАВКА ОТЧЕТА
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

addr_from = file[13]
addr_to = file[14]
password = file[15]
msg = MIMEMultipart()
msg['From'] = addr_from
msg['To'] = addr_to
msg['Subject'] = 'Отчет по гарантийному обслуживанию СВТ ДИТ'
files = file[11]
with open(files, 'rb') as f:
    file_data = f.read()
attachedfile = MIMEApplication(file_data, _subtype="pdf")
attachedfile.add_header('Content-Disposition', 'attachment', filename="jiraPDF.pdf")
msg.attach(attachedfile)
body = "Добрый день!\n\nНаправляем отчет по гарантийному обслуживанию СВТ ДИТ на " + date + "\n\nПоступило за период: " \
       + str(result[2]) + "\nВ работе: " + str(result[3]) + "\nИзменение очереди за период: " + str(result[4]) + \
       "\nРешено за период: " + str(result[5]) + "\nРешено всего: " + str(result[6]) + "\nНарушено SLA: " + \
       str(result[7]) + " что, составляет: " + str(result[8]) + "%\nИзменение нарушения SLA за период: " + str(result[9]) +\
       " что, составляет: " + str(result[10]) + "%\n"
msg.attach(MIMEText(str(body), 'plain'))
server = smtplib.SMTP('smtp.gmail.com', 587)                         # УКАЗАТЬ СЕРВЕР И ПОРТ
server.set_debuglevel(True)
server.starttls()
server.login(addr_from, password)
server.send_message(msg)
server.quit()

# ПЕРЕНОС PDF и json В АРХИВ ПЕРЕНОСИМ В ПАПКУ old

from zipfile import ZipFile
import os
import shutil

zipObj = ZipFile(file[8], 'w')
zipObj.write(file[10])
zipObj.write(file[11])
zipObj.close()
old_sender_zip = shutil.move((file[8]), file[9])
os.remove(file[10])
os.remove(file[11])
os.listdir()
