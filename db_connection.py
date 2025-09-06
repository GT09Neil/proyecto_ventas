import pyodbc

def get_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\SQLEXPRESS;"  # o NOMBRE_PC\SQLEXPRESS
        "DATABASE=VentasElectrodomesticos;"
        "Trusted_Connection=yes;"
    )
    return conn
