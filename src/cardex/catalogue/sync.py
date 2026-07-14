from pokemontcgsdk import RestClient, Set
from tqdm import tqdm

from cardex.catalogue.repository import cache_set
from cardex.db import pool


def setup_database(tcg_api_key):
    print("Beginning Data Caching")
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            print("Successfully registered vector extension")

            # Cache all cards
            RestClient.configure(tcg_api_key)
            for s in tqdm(Set.all()):
                try:
                    cache_set(s)
                    conn.commit()
                except Exception:
                    print(f"Could not cache set: {s.id}")

            print("Successfully Cached Sets")

    print("Data Caching Complete")
