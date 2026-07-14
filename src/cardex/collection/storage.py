from PIL import Image


def save_raw(image: Image.Image, image_name):
    image.save(f"../web/static/user_cards_raw/{image_name}", "PNG")


def save_warped(image: Image.Image, image_name):
    image.save(f"../web/static/user_cards/{image_name}", "PNG")
