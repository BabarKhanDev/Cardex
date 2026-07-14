from uuid import uuid1

from cardex.catalogue.repository import find_closest_cards
from cardex.collection.repository import add_match, add_upload
from cardex.collection.storage import save_raw, save_warped
from cardex.vision.features import create_feature_vector
from cardex.vision.homography import create_homography


def process_upload(image) -> None:
    image_name = f"{uuid1()}.png"
    save_raw(image, image_name)

    warped = create_homography(image)
    save_warped(warped, image_name)

    features = create_feature_vector(warped)
    card_ids = find_closest_cards(features)
    upload_id = add_upload(image_name)
    add_match(upload_id, card_ids)
