import sqlite3

conn = sqlite3.connect('user.db')
conn.execute("drop table if exists USER")
conn.execute(''' CREATE TABLE USER 
		( username CHAR(50),
		  password CHAR(50) ); ''')
#conn.close()

#conn = sqlite3.connect('file.db')
conn.execute("drop table if exists FILE")
conn.execute(''' CREATE TABLE FILE
		( filename CHAR(50),
		  username CHAR(50) ); ''')
conn.close()
