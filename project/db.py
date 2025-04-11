from sqlite3 import Connection

with Connection("dbusers.db") as conn:
    ijin_exeQ = conn.cursor()
    ijin_exeQ.execute("SELECT * FROM users")
    data = ijin_exeQ.fetchall()
    for i in data:
          print(i)
    