import os
import cx_Oracle
from dotenv import load_dotenv


load_dotenv()


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "1521")
DB_SERVICE = os.getenv("DB_SERVICE")

dsn = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)

try:
    connection = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)
    cursor = connection.cursor()
    print("Connected")

    cursor.execute("SELECT SYSDATE FROM dual")
    result = cursor.fetchone()
    print("Response:", result)

    
    cursor.close()
    connection.close()

except cx_Oracle.DatabaseError as e:
    print("FAIL.")
    print(e)
