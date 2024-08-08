from awk_plus_plus.actions import Actions


def set_dict(dictionary: dict, path: str, value: str):
    if isinstance(dictionary, str):
        return value
    keys = path.strip(".").split(".")
    root = dictionary
    for key in keys[:-1]:
        dictionary = dictionary.setdefault(key, {})
    dictionary[keys[-1]] = value
    return root


def walk(dictionary: dict, actions: Actions):
    def yielder(value, path=""):
        if isinstance(value, dict):
            for k, v in value.items():
                yield from yielder(v, path + f".{k}")
        elif isinstance(value, list):
            k = 0
            for v in value:
                yield from yielder(v, path + f".{k}")
                k += 1
        else:
            yield path, actions.parse(value)

    yield from yielder(dictionary)
