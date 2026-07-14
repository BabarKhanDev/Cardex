import json
from typing import List

import numpy as np
from pokemontcgsdk import Card, Set

from cardex.db import pool


def find_closest_cards(feature_vector: np.ndarray) -> List[str]:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM sdk_cache.card ORDER BY features <+> %s LIMIT 5;",
                (feature_vector,),
            )
            return [card[0] for card in cur.fetchall()]


def serialise_features(out_path: str = "serialised_features.json"):
    out = {}
    with pool.connection() as conn:
        with conn.cursor() as cur:
            for row in cur.fetchall():
                if row[1] is not None:
                    card_id, array = row[0], row[1].strip("[]").split(",")
                    out[card_id] = array

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)


def cache_set(s: Set) -> None:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # If the set is already cached then skip
            cur.execute("select count(*) from sdk_cache.set where id = %s", (s.id,))
            if cur.fetchone()[0] > 0:
                return

            # Add the set details to the DB
            cur.execute(
                "INSERT INTO sdk_cache.set (id, image_uri, name, series, release_date) VALUES (%s, %s, %s, %s, %s)",
                (s.id, s.images.logo, s.name, s.series, s.releaseDate),
            )

            cards = Card.where(q=f"set.id:{s.id}")
            for card in cards:

                cur.execute(
                    """
                INSERT INTO sdk_cache.card (id, image_uri_large, image_uri_small, name, set_id) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                    (
                        card.id,
                        card.images.large,
                        card.images.small,
                        card.name,
                        s.id,
                    ),
                )


def get_all_card_ids_and_urls():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select id, image_uri_large from sdk_cache.card where features is NULL"
            )
            return cur.fetchall()


def set_card_features(card_id, features):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE sdk_cache.card SET features = %s WHERE id = %s ",
                (features, card_id),
            )


def get_sets():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select id, image_uri, name, series, release_date from sdk_cache.set"
            )
            all_sets = cur.fetchall()

            return [
                {
                    "id": set_id,
                    "image_url": image_uri,
                    "name": name,
                    "series": series,
                    "release_date": release_date,
                }
                for set_id, image_uri, name, series, release_date in all_sets
            ]


def get_set_details(set_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                select id, image_uri, name, series, release_date 
                from sdk_cache.set
                where id = %s
            """,
                (set_id,),
            )

            response = cur.fetchone()
            if response is None:
                return None

            set_id, image_uri, name, series, release_date = response

            return {
                "id": set_id,
                "image_url": image_uri,
                "name": name,
                "series": series,
                "release_date": release_date,
            }


def get_cards(set_id: str):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    c.id, 
                    c.image_uri_large, 
                    c.image_uri_small, 
                    c.name, 
                    c.set_id, 
                    c.wishlist_quantity,
                    COUNT(m.card_id) AS library
                FROM sdk_cache.card c
                LEFT JOIN user_data.match m ON c.id = m.card_id
                WHERE c.set_id = %s
                GROUP BY 
                    c.id, 
                    c.name
            """,
                (set_id,),
            )
            cards = cur.fetchall()
            return [
                {
                    "id": card_id,
                    "image_url_large": image_large,
                    "image_url_small": image_small,
                    "name": name,
                    "set_id": set_id,
                    "wishlist": wishlist,
                    "library": library,
                }
                for card_id, image_large, image_small, name, set_id, wishlist, library in cards
            ]


def get_card_from_id(card_id: str):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # TODO update to send wishlist and library
            cur.execute(
                """
                select id, set_id, image_uri_large, image_uri_small, name 
                from sdk_cache.card 
                where id = %s
            """,
                (card_id,),
            )

            response = cur.fetchone()
            if response is None:
                return None

            card_id, set_id, image_uri_large, image_uri_small, name = response

            return {
                "id": card_id,
                "image_url_large": image_uri_large,
                "image_url_small": image_uri_small,
                "name": name,
                "set_id": set_id,
            }
