import psycopg2

def connect_to_postgresql():
    DB_HOST = '192.168.40.105'
    DB_PORT = 5432
    DB_USER = 'simongps'
    DB_PASSWORD = 's1m0ngps*.*'
    DB_NAME = 'simongpsdev_1'

    try:
        con = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        print("Conexión exitosa a PostgreSQL!")
        return con

    except psycopg2.Error as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        return None

