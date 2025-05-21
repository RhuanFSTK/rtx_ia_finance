from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error

# Carrega variáveis do arquivo .env
load_dotenv()

def get_connection():
    try:
        # Lê as variáveis de ambiente
        host = os.getenv("SEU_HOST")
        user = os.getenv("SEU_USUARIO")
        password = os.getenv("SUA_SENHA")
        database = os.getenv("SEU_BANCO")
        
        if not all([host, user, password, database]):
            raise ValueError("Faltando variáveis de ambiente para conexão com o banco de dados.")
        
        # Conecta ao banco
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        if connection.is_connected():
            print(f"✅ Conexão com o banco de dados '{database}' estabelecida com sucesso.")
            return connection

    except Error as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        if 'connection' in locals() and connection.is_connected():
            connection.close()
        return None
    except ValueError as ve:
        print(f"⚠️ {ve}")
        return None
    except Exception as ex:
        print(f"❗ Erro desconhecido: {ex}")
        return None

# Teste local
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        conn.close()
