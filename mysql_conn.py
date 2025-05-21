from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv() 

# print(os.getenv("SEU_HOST"))
# print(os.getenv("SEU_USUARIO"))
# print(os.getenv("SUA_SENHA"))
# print(os.getenv("SEU_BANCO"))

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("SEU_HOST"),
        user=os.getenv("SEU_USUARIO"),
        password=os.getenv("SUA_SENHA"),
        database=os.getenv("SEU_BANCO")
    )
