from cardex.catalogue.sync import setup_database
from cardex.config import load_tcg_api_key
from cardex.vision.features import calculate_features_of_all_cards

tcg_api_key = load_tcg_api_key("config.ini")
setup_database(tcg_api_key)
calculate_features_of_all_cards()
