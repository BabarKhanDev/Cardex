from pgvector.psycopg import register_vector
from psycopg_pool import ConnectionPool

from cardex.config import load_database_config


def _configure(conn):
    register_vector(conn)


pool = ConnectionPool(
    kwargs=load_database_config("config.ini"),
    min_size=2,
    max_size=10,
    configure=_configure,
    open=True,
)
