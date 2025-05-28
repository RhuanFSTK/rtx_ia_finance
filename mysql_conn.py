from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
import logging
import sys

# Carrega variáveis do arquivo .env
load_dotenv()

# Logger para terminal (Uvicorn)
logger = logging.getLogger("consulta_gastos")
if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def get_connection():
    try:
        # Usa variáveis do .env ou fallback para valores locais
        host = os.getenv("SEU_HOST", "localhost")
        user = os.getenv("SEU_USUARIO", "root")
        password = os.getenv("SUA_SENHA", "")
        database = os.getenv("SEU_BANCO", "meu_banco_local")
        
        # Conecta ao banco
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        if connection.is_connected():
            logger.info("✅ Conexão com o banco de dados '{database}' estabelecida com sucesso.")
            return connection

    except Error as e:
        logger.info("❌ Erro ao conectar ao MySQL: {e}")
        if 'connection' in locals() and connection.is_connected():
            connection.close()
        return None
    except Exception as ex:
        logger.info("❗ Erro desconhecido: {ex}")
        return None

# Teste local
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        conn.close()
