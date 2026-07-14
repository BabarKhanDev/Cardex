class CardId(str):
    pass


class CardDetails(dict):
    id: CardId
    image_uri_large: str
    image_uri_small: str
    name: str
    set_id: str
    wishlist: int
    library: int


class SetId(str):
    pass


class Quantity(int):
    pass


class SetDetails:
    id: SetId
    image_url: str
    name: str
    series: str
    release_date: str


class WishlistResponse(dict[CardId, Quantity]):
    pass


class AllSetsResponse(list[SetDetails]):
    pass


class AllCardsResponse(list[CardDetails]):
    pass


class CardDetailsResponse(CardDetails):
    pass


class LibraryResponse(list[dict]):
    pass
