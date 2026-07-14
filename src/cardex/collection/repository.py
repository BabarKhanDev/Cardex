from cardex.db import pool


def get_wishlist():
    # Returns a map from card_id to wishlist quantity for all cards that are wish-listed
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select id, wishlist_quantity
                from sdk_cache.card 
                where wishlist_quantity > 0
            """
            )

            return {card_id: quantity for (card_id, quantity) in cur.fetchall()}


def remove_from_wishlist(card_id: str, quantity: int = 1):
    return add_to_wishlist(card_id, quantity * -1)


def add_to_wishlist(card_id: str, quantity: int):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                update sdk_cache.card
                set wishlist_quantity = greatest(0, wishlist_quantity + %s) 
                where id = %s;
            """,
                (
                    quantity,
                    card_id,
                ),
            )


def in_wishlist(card_id: str):
    wishlist = get_wishlist()
    return card_id in wishlist.keys()


def list_uploads(user_card_dir: str = "static/user_cards/"):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    upload.image_path AS upload_path,
                    upload.id as upload_id
                FROM user_data.upload
            """
            )

            return [
                {"imgsrc": f"{user_card_dir}{upload_path}", "upload_id": upload_id}
                for upload_path, upload_id in cur.fetchall()
            ]


def in_uploads(card_id: str):
    library = list_uploads()
    return card_id in {card["card_id"] for card in library}


def matches_for_upload(upload_id: str):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    match.card_id AS card_id,
                    card.image_uri_small AS image_url,
                    upload.image_path AS upload_path
                FROM user_data.match
                JOIN sdk_cache.card ON match.card_id = card.id
                JOIN user_data.upload ON match.upload_id = upload.id
                WHERE upload_id = %s
            """,
                (upload_id,),
            )

            return [
                {"card_id": card_id, "image_url": image_url, "upload_path": upload_path}
                for card_id, image_url, upload_path in cur.fetchall()
            ]


def match_count(card_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT count(card_id)
                FROM user_data.match
                WHERE card_id = %s
            """,
                (card_id,),
            )

            return cur.fetchone()[0]


def add_upload(image_path):
    # TODO
    pass


def add_match(upload_id, card_id):
    # TODO
    pass
