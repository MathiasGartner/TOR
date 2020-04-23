import mysql.connector as mysql

import tor.TORSettingsPrivate as tsp

db = mysql.connect(
    host = tsp.DATABASE_HOST,
    user = tsp.DATABASE_USER,
    passwd = tsp.DATABASE_PASSWORD,
    database = "tor"
)

cursor = db.cursor()

def writeResult(clientId, result):
    query = "INSERT INTO diceresult (clientId, result) VALUES ({}, {})".format(clientId, result)
    cursor.execute(query)
    db.commit()

