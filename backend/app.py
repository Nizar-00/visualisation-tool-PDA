import os
import cx_Oracle
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  #for React frontend calls


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "1521")  
DB_SERVICE = os.getenv("DB_SERVICE")


dsn = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)

connection = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)

cursor = connection.cursor()



@app.route('/api/dashboard', methods=['GET']) #fetch = get by default.
#when the frontend requests /api/dashboard, run function dashboard ( ) which only responds to get requests. Can set up "post" requests later.


def dashboard():

    start_date = request.args.get('startDate', '') 
    end_date = request.args.get('endDate', '')
    pda_number = request.args.get('pdaNumber', '')  
#pull out the filter inputs from the URL and save them in user defined vars

#user defined vars stored in bind_vars dict
    bind_vars = {
        'pdaNumber': f"%PDA{pda_number}%" if pda_number else '%PDA%',
        'startDate': start_date if start_date else '01/01/2025', #in case empty put 2025 first date.
        'endDate': end_date if end_date else '31/12/2025' #in case empty
    }


    return jsonify(bind_vars)



@app.route('/api/stats/total-new-pda', methods=['GET'])
def total_new_pda():
    start_date = request.args.get('startDate', '')
    end_date = request.args.get('endDate', '')

    bind_vars = {
        'startDate': start_date if start_date else '01/01/2025',
        'endDate': end_date if end_date else '31/12/2025'
    }

    sql_query = """
        SELECT 
            COUNT(DISTINCT a.IMEI_PDA) AS total_new_pda
        FROM 
            pe_prd_declarationpeche a
        WHERE 
            a.IMEI_PDA IS NOT NULL
            AND a.DATEDECLARATION BETWEEN TO_DATE(:startDate, 'DD/MM/YYYY') AND TO_DATE(:endDate, 'DD/MM/YYYY')
    """

    try:
        cursor.execute(sql_query, bind_vars)
        result = cursor.fetchone()
        return jsonify({"total_new_pda": result[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500