import multiprocessing as mp

from cardex.catalogue.repository import (
    get_card_from_id,
    get_cards,
    get_set_details,
    get_sets,
)
from cardex.collection.repository import (
    add_to_wishlist,
    get_wishlist,
    list_uploads,
    match_count,
    matches_for_upload,
)
from cardex.collection.service import process_upload
from cardex.web.responses import (
    AllCardsResponse,
    AllSetsResponse,
    CardDetailsResponse,
    LibraryResponse,
    WishlistResponse,
)
from flask import Blueprint, Response, redirect, render_template, request
from PIL import Image, ImageOps

bp = Blueprint("main", __name__)
image_processing_count = mp.Value("i", 0)


# JSON Delivery


@bp.get("/status")
def status():
    return {"cards_processing": image_processing_count.value}


# Return a list containing details for every set
# When we start the bp.we cache all sets in the database
# Each set contains:
#   id           - str,
#   image_url    - str, logo of the set
#   name         - str, display name for the set
#   series       - str, the series that the set belongs to, e.g. diamond and pearl
#   release_date - str, day, dd Mmm YYYY 00:00:00 GMT # TODO maybe I should trim the time
@bp.get("/all_sets")
def get_all_sets():
    return AllSetsResponse(get_sets())


# Return a list of details for each card in a given set
# First we check if we have cached the cards in our database
# Each card contains:
#   id              - str
#   image_url_large - str, high-res image of card
#   image_url_small - str, low-res image of card
#   name            - str, display name of card
#   set_id          - str, the set that owns this card
@bp.get("/set/<set_id>")
def get_set(set_id):
    return AllCardsResponse(get_cards(set_id))


# Return a dictionary with the details of our card
# These are the same as described above
@bp.get("/card/<card_id>")
def get_card(card_id):
    details = get_card_from_id(card_id)
    if details is not None:
        return CardDetailsResponse(details)

    return Response("Card not found", status=404, mimetype="bp.ication/json")


# Return a dictionary of card_id : quantity wishlisted
# POST request allows you to adjust the quantity of wishlisted cards by a quantity
# POST parameters:
#   card_id - str, the card to adjust
#   amount  - int, the amount the adjust quantity by
@bp.route("/wishlist_id", methods=["GET", "POST"])
def wishlist():
    # GET - Send the wishlist
    if request.method == "GET":
        return WishlistResponse(get_wishlist())

    # POST - Add/Remove cards from the wishlist
    card_id = request.form["card_id"]
    amount = int(request.form["amount"])
    add_to_wishlist(card_id, amount)

    return WishlistResponse(get_wishlist())


# Return a list of library objects
# Each library object looks like:
#   card_id: string
#   image_url: string <- sdk image
#   upload_path: string <- user image
@bp.route("/uploads")
def uploads():
    return LibraryResponse(list_uploads())


@bp.route("/matches/<upload_id>")
def matches(upload_id):
    return matches_for_upload(upload_id)


# Get the number of matches of a card in a users library
@bp.route("/upload_count/<card_id>")
def upload_count(card_id):
    return {card_id: match_count(card_id)}


# Return the details of a set
@bp.get("/set_details/<set_id>")
def set_details(set_id):
    details = get_set_details(set_id)
    if details is not None:
        return details

    return Response("Set not found", status=404, mimetype="bp.ication/json")


@bp.route("/upload_cards", methods=["POST"])
def upload_cards():
    if "file" not in request.files:
        return Response({"error": "No image file in request"}, status=400)

    files = request.files.getlist("file")
    image_processing_count.value += len(files)
    for file in files:

        image = Image.open(file)
        image = ImageOps.exif_transpose(image)  # fix rotation issue
        process = mp.Process(
            target=process_upload, args=(image, image_processing_count)
        )
        process.start()
        process.join()

    return "Success"


#################
# HTML DELIVERY #
#################


@bp.get("/")
def default():
    return redirect("/library")


# This will allow you to explore a given set
@bp.get("/explore/<set_id>")
def explore_set(set_id):
    set_name = get_set_details(set_id)["id"]
    return render_template("set.html", set_name=set_name)


# This will allow you to explore all sets
@bp.get("/explore")
def explore_sets():
    return render_template("explore.html")


# This will allow you to explore the library
@bp.get("/library")
def explore_library():
    return render_template("library.html")


@bp.get("/wishlist")
def explore_wishlist():
    return render_template("wishlist.html")
