import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

from app.database.conexao import obter_conexao

st.title("Teste de conexão com o banco")

conn = None
try:
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM culturas;")
    resultado = cursor.fetchall()
    cursor.close()

    st.success("Conexão funcionando!")
    st.write("Culturas cadastradas:", resultado)

except Exception as e:  # noqa: BLE001
    st.error("Falha na conexão com o banco de dados.")
    st.exception(e)

finally:
    if conn:
        conn.close()