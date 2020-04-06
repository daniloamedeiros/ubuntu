import json
import requests

# --------------Requisição post-----------------------------------------
# url = "http://tcp.logstash.video.globoi.com"
# data = {'client': 'nome_do_cliente','owner': 'nome_do_time'}
# headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# r = requests.post(url, data=json.dumps(data), headers=headers)
# print(r)
# -------------------------------------------------------
# import mysql.connector
# from mysql.connector import errorcode
# try:
# 	db_connection = mysql.connector.connect(host='localhost', user='root', password='Aa123123', database='bd')
# 	print("Database connection made!")
# except mysql.connector.Error as error:
# 	if error.errno == errorcode.ER_BAD_DB_ERROR:
# 		print("Database doesn't exist")
# 	elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
# 		print("User name or password is wrong")
# 	else:
# 		print(error)
# else:
# 	db_connection.close()

# ------------------------------------------------------

from datetime import date
import mysql.connector

test_id = "123"
tipo  = "step"
feature  = "continue assistindo"
scenario  = "trilho CA"
step  ="step 2"
_status  ="passed"
tags_feature  ="tag_feature"
tags_scenarios  ="tag_scenario"
_datetime  ="10/10/2000"
platforma  ="andoid"
device  = "132123ee"
origin  = "local"



db_connection = mysql.connector.connect(host="localhost", user="root", passwd="Aa123123", database="bd")
cursor = db_connection.cursor()
sql = "INSERT INTO relatorio (test_id, tipo, feature, scenario, step, _status, tags_feature, tags_scenarios,_datetime, platforma, device, origin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
values = (test_id, tipo, feature, scenario, step, _status, tags_feature, tags_scenarios,_datetime, platforma, device, origin)
cursor.execute(sql, values)
current_date = date.today()
formatted_date = current_date.strftime('%d/%m/%Y')

print(formatted_date)
print("\n")
print(cursor.rowcount, "record inserted.")
print("\n")

sql = ("SELECT test_id, tipo origin,feature FROM relatorio")
cursor.execute(sql)

for (test_id, tipo,feature) in cursor:
    print(test_id, tipo,feature)
print("\n")


cursor.close()
db_connection.commit()
db_connection.close()

# -------------------------------------------------------

# relatorio = {
#     "Feature": "Feature",
#     "Scenario": "Scenario",
#     "Step": "Step",
#     "Step_status": "Step_status",
#     "Tags_feature": "Tags_feature",
#     "Tags_scenarios": "Tags_scenario",
#     "datetime": "Datetime"
# }
#
# cliente = MongoClient("mongodb+srv://teste:123123123@gplay-bphh6.mongodb.net/test?authSource=admin&replicaSet=Gplay-shard-0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=true")
# banco = cliente.mongodba
# collection = banco.relatorio_python
# # relatorio_id = album.insert_one(relatorio).inserted_id
# # relatorio_id
#
# # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# # mydb = myclient["mydatabase"]
# # mycol = mydb["customers"]
#
# # myquery = {"Step_status":"failed","datetime":"12/03/2020_00:01:24"}
# #
# # mydoc = album.find(myquery.values())
# #
# # for x in mydoc:
# #   print(x)
#
# result = collection.find({"Step_status":"failed"})
# for document in result:
#
#   print(document)

