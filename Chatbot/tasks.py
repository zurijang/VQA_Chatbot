def is_json_key_present(json, key):
    try:
        buf = json[key]
    except KeyError:
        return False
    return True