import pyodbc

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=tcp:greencart-server.database.windows.net,1433;"
    "DATABASE=greencart-db;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Authentication=ActiveDirectoryMsi;"
)

try:
    with pyodbc.connect(connection_string, timeout=15) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id_product, name, price FROM dbo.Products")

        for product in cursor.fetchall():
            print(product)

        print("\nConnexion à Azure SQL réussie !")

except Exception as error:
    print("Échec de la connexion :")
    print(error)
