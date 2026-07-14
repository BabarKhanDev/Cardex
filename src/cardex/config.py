import configparser


def __read_config(config_location: str = "config.ini") -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(config_location)
    return config


def load_tcg_api_key(config_location: str = "config.ini") -> str:
    parser = __read_config(config_location)
    if parser.has_section("pokemontcg"):
        return __read_config(config_location)["pokemontcg"]["API_key"]
    else:
        raise Exception(f'Section pokemontcg not found in the {config_location} file')


def load_database_config(config_location: str = "config.ini"):
    parser = __read_config(config_location)

    config = {}
    if parser.has_section('postgresql'):
        params = parser.items('postgresql')
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception(f'Section postgresql not found in the {config_location} file')

    return config


if __name__ == "__main__":
    config_loc = "../config.ini"
    print(load_database_config(config_loc))
    print(load_tcg_api_key(config_loc))