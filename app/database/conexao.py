import psycopg2
from psycopg2.pool import ThreadedConnectionPool
import streamlit as st


@st.cache_resource
def _obter_pool() -> ThreadedConnectionPool:
    """
    Mantém um pool de conexões persistente na memória do Streamlit
    para evitar o custo de abrir handshake TCP/TLS com o Supabase a cada consulta.
    """
    config = st.secrets["connection"]
    return ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        host=config["host"],
        port=config["port"],
        dbname=config["database"],
        user=config["user"],
        password=config["password"],
        connect_timeout=10,
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5,
    )


class _ConexaoPoolWrapper:
    """
    Wrapper que intercepta o .close() para devolver a conexão ao pool
    em vez de fechar o socket TCP/TLS com o banco de dados.
    """
    def __init__(self, pool: ThreadedConnectionPool, raw_conn):
        self._pool = pool
        self._raw_conn = raw_conn
        self._devolvida = False

    def close(self):
        if not self._devolvida:
            self._devolvida = True
            try:
                if not self._raw_conn.closed:
                    self._raw_conn.rollback()
                self._pool.putconn(self._raw_conn)
            except Exception:
                try:
                    self._pool.putconn(self._raw_conn, close=True)
                except Exception:
                    pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getattr__(self, name):
        return getattr(self._raw_conn, name)


def obter_conexao():
    """
    Obtém uma conexão reaproveitável do pool para máxima velocidade.
    """
    try:
        pool = _obter_pool()
        raw_conn = pool.getconn()
        if raw_conn.closed != 0:
            pool.putconn(raw_conn, close=True)
            raw_conn = pool.getconn()
        return _ConexaoPoolWrapper(pool, raw_conn)
    except Exception:
        # Fallback de segurança para modo standalone/scripts fora do Streamlit
        config = st.secrets["connection"]
        return psycopg2.connect(
            host=config["host"],
            port=config["port"],
            dbname=config["database"],
            user=config["user"],
            password=config["password"],
            connect_timeout=10,
        )


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