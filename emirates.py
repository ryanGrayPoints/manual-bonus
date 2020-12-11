
import csv
from manual_bonus import *

cid_prefix = "Emirates_Manual_Bonus"
ticket_id = ""

reader = csv.DictReader(open('emirates.csv', encoding="utf-8-sig"))
dict_list = []
for line in reader:
    dict_list.append(line)

logs = []
for x in dict_list:
    cid = generate_cid(cid_prefix)
    ticket = "https://jira.points.com/browse/" + ticket_id
    mb = manual_bonus(x["parent_order"], x["offer"], ticket, cid)
    logs.append(mb)

csv_columns = ["ticket", "offer", "parent_order", "order_url", "parent_order_amount", "bonus_amount", "credit_status",
               "order_status", "pts_app_cid"]

ts = str(int(time.time()))
csv_file = "Manual_bonus_logs_" + ts + ".csv"

try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in logs:
            writer.writerow(data)
except :
    print("error writing to csv")

for log in logs:
    print(log)
