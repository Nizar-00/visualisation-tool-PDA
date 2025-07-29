import os
import cx_Oracle
from flask import Flask, jsonify, request
from flask_cors import CORS
from contextlib import contextmanager

app = Flask(__name__)
CORS(app)

@contextmanager
def get_connection():
    conn = None
    try:
        conn = cx_Oracle.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_SERVICE')}"
        )
        yield conn
    finally:
        if conn:
            conn.close()

@app.route('/api/declarations/count_par_pda', methods=['POST'])
def declarations_count_par_pda():
    data = request.get_json()
    pda_code = data.get('pda_code')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not (pda_code and start_date and end_date):
        return jsonify({'error': 'Missing parameters'}), 400

    query = """
        SELECT COUNT(DISTINCT a.NUMEROVISA) AS total_declarations_distinct
        FROM pe_prd_declarationpeche a
        INNER JOIN pe_prd_sourceespdc b ON a.id = b.id_refdeclaration
        INNER JOIN pm_ref_espece c ON c.id = b.id_refespece
        WHERE a.NUMEROVISA LIKE '%' || :pda_code || '%'
          AND a.DATEDECLARATION BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') AND TO_DATE(:end_date, 'YYYY-MM-DD')
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, {
                'pda_code': pda_code,
                'start_date': start_date,
                'end_date': end_date
            })
            result = cursor.fetchone()
            return jsonify({'total_declarations_distinct': result[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/declarations/count_par_port', methods=['POST'])
def declarations_count_par_port():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    port_name = data.get('port_name')

    if not (start_date and end_date and port_name):
        return jsonify({'error': 'Missing parameters'}), 400

    query = """
        SELECT 
          e.CODE AS entite_code,
          e.NOM AS entite_nom,
          COUNT(DISTINCT CASE 
              WHEN REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
                   AND TO_NUMBER(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3)) BETWEEN 286 AND 400
              THEN a.ID
          END) AS nombre_declarations_new_pda
        FROM pe_prd_declarationpeche a
        INNER JOIN adm_ref_entite e ON e.id = a.id_refentitedeclar
        WHERE a.NUMEROVISA LIKE '%PDA%'
          AND INSTR(a.NUMEROVISA, 'PDA') > 0
          AND a.DATEDECLARATION BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') AND TO_DATE(:end_date, 'YYYY-MM-DD')
          AND REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
          AND e.NOM = :port_name
        GROUP BY e.CODE, e.NOM
        ORDER BY e.CODE
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, {
                'start_date': start_date,
                'end_date': end_date,
                'port_name': port_name
            })
            rows = cursor.fetchall()
            result = [
                {
                    'entite_code': row[0],
                    'entite_nom': row[1],
                    'nombre_declarations_new_pda': row[2]
                }
                for row in rows
            ]
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    



@app.route('/api/declarations/par_mois', methods=['GET'])
def declarations_par_mois():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not (start_date and end_date):
        return jsonify({'error': 'Missing parameters: start_date and end_date are required'}), 400

    query = """
        SELECT 
          e.CODE AS entite_code,
          e.NOM AS entite_nom,
          EXTRACT(MONTH FROM a.DATEDECLARATION) AS mois,
          COUNT(DISTINCT CASE 
              WHEN REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
                   AND TO_NUMBER(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3)) BETWEEN 286 AND 400
              THEN a.ID
          END) AS nombre_declarations_new_pda
        FROM pe_prd_declarationpeche a
        INNER JOIN adm_ref_entite e ON e.id = a.id_refentitedeclar
        WHERE a.NUMEROVISA LIKE '%PDA%'
          AND INSTR(a.NUMEROVISA, 'PDA') > 0
          AND a.DATEDECLARATION BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') AND TO_DATE(:end_date, 'YYYY-MM-DD')
          AND REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
        GROUP BY e.CODE, e.NOM, EXTRACT(MONTH FROM a.DATEDECLARATION)
        ORDER BY e.CODE, mois
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, start_date=start_date, end_date=end_date)
            rows = cursor.fetchall()
            result = [
                {
                    'entite_code': row[0],
                    'entite_nom': row[1],
                    'mois': row[2],
                    'nombre_declarations_new_pda': row[3]
                }
                for row in rows
            ]
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@app.route('/api/declarations/par_mois_selection', methods=['POST'])
def declarations_par_mois_selection():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    months = data.get('months')

    if not (start_date and end_date and months and isinstance(months, list) and all(isinstance(m, int) for m in months)):
        return jsonify({'error': 'Missing or invalid parameters: start_date, end_date and months (list of int) required'}), 400

    
    months_tuple = tuple(months)
    if len(months_tuple) == 1:
       
        months_sql = f"({months_tuple[0]})"
    else:
        months_sql = str(months_tuple)

    query = f"""
        SELECT 
          e.CODE AS entite_code,
          e.NOM AS entite_nom,
          EXTRACT(MONTH FROM a.DATEDECLARATION) AS mois,
          COUNT(DISTINCT CASE 
              WHEN REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
                   AND TO_NUMBER(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3)) BETWEEN 286 AND 400
              THEN a.ID
          END) AS nombre_declarations_new_pda
        FROM pe_prd_declarationpeche a
        INNER JOIN adm_ref_entite e ON e.id = a.id_refentitedeclar
        WHERE a.NUMEROVISA LIKE '%PDA%'
          AND INSTR(a.NUMEROVISA, 'PDA') > 0
          AND a.DATEDECLARATION BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') AND TO_DATE(:end_date, 'YYYY-MM-DD')
          AND EXTRACT(MONTH FROM a.DATEDECLARATION) IN {months_sql}
          AND REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
        GROUP BY e.CODE, e.NOM, EXTRACT(MONTH FROM a.DATEDECLARATION)
        ORDER BY e.CODE, mois
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, {'start_date': start_date, 'end_date': end_date})
            rows = cursor.fetchall()
            result = [
                {
                    'entite_code': row[0],
                    'entite_nom': row[1],
                    'mois': row[2],
                    'nombre_declarations_new_pda': row[3]
                }
                for row in rows
            ]
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/declarations/count_par_ports_all', methods=['POST'])
def declarations_count_par_ports_all():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not (start_date and end_date):
        return jsonify({'error': 'Missing parameters: start_date and end_date'}), 400

    query = """
        SELECT 
          e.CODE AS entite_code,
          e.NOM AS entite_nom,
          COUNT(DISTINCT CASE 
              WHEN REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
                   AND TO_NUMBER(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3)) BETWEEN 286 AND 400
              THEN a.ID
          END) AS nombre_declarations_new_pda
        FROM pe_prd_declarationpeche a
        INNER JOIN adm_ref_entite e ON e.id = a.id_refentitedeclar
        WHERE a.NUMEROVISA LIKE '%PDA%'
          AND INSTR(a.NUMEROVISA, 'PDA') > 0
          AND a.DATEDECLARATION BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') AND TO_DATE(:end_date, 'YYYY-MM-DD')
          AND REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
        GROUP BY e.CODE, e.NOM
        ORDER BY e.CODE
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, {'start_date': start_date, 'end_date': end_date})
            rows = cursor.fetchall()
            result = [
                {
                    'entite_code': row[0],
                    'entite_nom': row[1],
                    'nombre_declarations_new_pda': row[2]
                }
                for row in rows
            ]
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/declarations/count_par_entite_mere', methods=['POST'])
def declarations_count_par_entite_mere():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not (start_date and end_date):
        return jsonify({'error': 'Missing parameters: start_date and end_date'}), 400

    query = """
        SELECT 
          entite_mere.CODE AS entite_mere_code,
          entite_mere.NOM AS entite_mere_nom,
          COUNT(DISTINCT CASE 
              WHEN REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
                   AND TO_NUMBER(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3)) BETWEEN 286 AND 400
              THEN a.ID
          END) AS nombre_declarations_new_pda
        FROM pe_prd_declarationpeche a
        INNER JOIN adm_ref_entite e ON e.id = a.id_refentitedeclar
        INNER JOIN adm_ref_entite entite_mere ON entite_mere.CODE = REGEXP_SUBSTR(e.CODE, '^[0-9]+')
        WHERE a.NUMEROVISA LIKE '%PDA%'
          AND INSTR(a.NUMEROVISA, 'PDA') > 0
          AND a.DATEDECLARATION BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') AND TO_DATE(:end_date, 'YYYY-MM-DD')
          AND REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
        GROUP BY entite_mere.CODE, entite_mere.NOM
        ORDER BY entite_mere.CODE
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, {'start_date': start_date, 'end_date': end_date})
            rows = cursor.fetchall()
            result = [
                {
                    'entite_mere_code': row[0],
                    'entite_mere_nom': row[1],
                    'nombre_declarations_new_pda': row[2]
                }
                for row in rows
            ]
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/declarations/count_par_entite_mere_nom', methods=['POST'])
def declarations_count_par_entite_mere_nom():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    entite_mere_nom = data.get('entite_mere_nom')

    if not (start_date and end_date and entite_mere_nom):
        return jsonify({'error': 'Missing parameters: start_date, end_date and entite_mere_nom are required'}), 400

    query = """
        SELECT 
          entite_mere.CODE AS entite_mere_code,
          entite_mere.NOM AS entite_mere_nom,
          COUNT(DISTINCT CASE 
              WHEN REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
                   AND TO_NUMBER(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3)) BETWEEN 286 AND 400
              THEN a.ID
          END) AS nombre_declarations_new_pda
        FROM pe_prd_declarationpeche a
        INNER JOIN adm_ref_entite e ON e.id = a.id_refentitedeclar
        INNER JOIN adm_ref_entite entite_mere ON entite_mere.CODE = REGEXP_SUBSTR(e.CODE, '^[0-9]+')
        WHERE a.NUMEROVISA LIKE '%PDA%'
          AND INSTR(a.NUMEROVISA, 'PDA') > 0
          AND a.DATEDECLARATION BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') AND TO_DATE(:end_date, 'YYYY-MM-DD')
          AND REGEXP_LIKE(SUBSTR(a.NUMEROVISA, INSTR(a.NUMEROVISA, 'PDA') + 3, 3), '^[0-9]+$')
          AND entite_mere.NOM = :entite_mere_nom
        GROUP BY entite_mere.CODE, entite_mere.NOM
        ORDER BY entite_mere.CODE
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, {
                'start_date': start_date,
                'end_date': end_date,
                'entite_mere_nom': entite_mere_nom
            })
            rows = cursor.fetchall()
            result = [
                {
                    'entite_mere_code': row[0],
                    'entite_mere_nom': row[1],
                    'nombre_declarations_new_pda': row[2]
                }
                for row in rows
            ]
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/declarations/par_port_selection', methods=['POST'])
def declarations_par_port_selection():
    data = request.get_json()

    start_date = data.get('start_date')
    end_date = data.get('end_date')
    entite_mere_nom = data.get('entite_mere_nom')
    selected_port = data.get('selected_port', '')
    selected_pda_code = data.get('selected_pda_code', '')

    if not (start_date and end_date and entite_mere_nom):
        return jsonify({'error': 'Missing parameters: start_date, end_date, entite_mere_nom'}), 400

    where_conditions = [
        "D.DATEDECLARATION BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') AND TO_DATE(:end_date, 'YYYY-MM-DD')"
    ]
    bind_vars = {
        'start_date': start_date,
        'end_date': end_date,
        'entite_mere_nom': entite_mere_nom
    }

    # Join with adm_ref_entite as E on foreign key
    # filter port on E.CODE (code of port) instead of non-existent D.ENTITE_CODE
    if selected_port:
        where_conditions.append("E.CODE = :selected_port")
        bind_vars['selected_port'] = selected_port

    if selected_pda_code:
        where_conditions.append("D.NUMEROVISA LIKE '%' || :selected_pda_code || '%'")
        bind_vars['selected_pda_code'] = selected_pda_code

    where_clause = " AND ".join(where_conditions)

    query = f"""
        SELECT
            A.ENTITE_MERE_CODE,
            A.ENTITE_MERE_NOM,
            COUNT(DISTINCT D.NUMEROVISA) AS NOMBRE_DECLARATIONS_NEW_PDA
        FROM PE_PRD_DECLARATIONPECHE D
        JOIN ADM_REF_ENTITE E ON E.ID = D.ID_REFENTITEDECLAR  -- join to get port/entity details
        JOIN (
            SELECT DISTINCT
                REGEXP_SUBSTR(CODE, '^[^/]+') AS ENTITE_MERE_CODE,
                NOM AS ENTITE_MERE_NOM
            FROM ADM_REF_ENTITE
            WHERE CODE NOT LIKE '%/%'
        ) A ON A.ENTITE_MERE_CODE = REGEXP_SUBSTR(E.CODE, '^[^/]+')
        WHERE
            A.ENTITE_MERE_NOM = :entite_mere_nom
            AND {where_clause}
        GROUP BY
            A.ENTITE_MERE_CODE,
            A.ENTITE_MERE_NOM
        ORDER BY
            A.ENTITE_MERE_CODE
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, bind_vars)
            rows = cursor.fetchall()
            result = [
                {
                    'entite_mere_code': row[0],
                    'entite_mere_nom': row[1],
                    'nombre_declarations_new_pda': row[2]
                }
                for row in rows
            ]
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


    


    
@app.route('/api/entites_mere', methods=['GET'])
def get_entites_mere():
    query = """
        SELECT CODE, NOM
        FROM adm_ref_entite
        WHERE CODE NOT LIKE '%/%'
        ORDER BY CODE
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            result = [{'code': row[0], 'name': row[1]} for row in rows]
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ports', methods=['GET'])
def get_ports_by_entite():
    entite_code = request.args.get('entiteCode')
    if not entite_code:
        return jsonify({'error': 'entiteCode parameter required'}), 400

    query = """
        SELECT CODE, NOM
        FROM adm_ref_entite
        WHERE CODE LIKE :entite_code || '/%'
        ORDER BY CODE
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, {'entite_code': entite_code})
            rows = cursor.fetchall()
            result = [{'code': row[0], 'name': row[1]} for row in rows]
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)
