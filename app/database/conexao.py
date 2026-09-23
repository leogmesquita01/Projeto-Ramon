import psycopg2
import streamlit as st
from psycopg2.extensions import connection as PGConnection


def obter_conexao() -> PGConnection:

    config = st.secrets["connection"]

    conn = psycopg2.connect(
        host=config["host"],
        port=config["port"],
        dbname=config["database"],
        user=config["user"],
        password=config["password"],
    )
    return conn


def executar_schema(caminho_schema: str = "app/database/schema.sql") -> None:

    with open(caminho_schema, "r", encoding="utf-8") as arquivo:
        script_sql = arquivo.read()

    conn = obter_conexao()
    try:
        cursor = conn.cursor()
        cursor.execute(script_sql)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    executar_schema()