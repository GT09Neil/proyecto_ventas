import pyodbc

def get_connection():

    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost\SQLEXPRESS;" 
            "DATABASE=VentasElectrodomesticos;"
            "Trusted_Connection=yes;"
        )
        return conn
    
    except pyodbc.Error as e:
        print("Error al conectar:", e)
