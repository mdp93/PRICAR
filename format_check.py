import json

with open("format_test.json") as score_format:
    score_format = json.load(score_format)

print(score_format)


def check_format(format, values):
    if 'type' not in format or None is format['type']:
        return False

    # okay for any value to be null
    if None is values:
        return True
    elif 'object' == format['type']:
        if not isinstance(values, dict):
            return False
        # make sure the dict has everything format specified
        for k in format.keys():
            if 'type' == k:
                continue
            if k not in values:
                return False
        # make sure the dict has nothing the format doesn't specify
        for k in values.keys():
            if k not in format:
                return False
            # check the format of values in the object
            if not check_format(format[k], values[k]):
                return False
    elif 'bool' == format['type']:
        if not isinstance(values, bool):
            return False
    elif 'int' == format['type']:
        if not isinstance(values, int):
            return False
        if 'min' in format and values < format['min']:
            return False
        if 'max' in format and values > format['max']:
            return False
    elif 'float' == format['type']:
        if not (isinstance(values, float) or isinstance(values, int)):
            return False
        if 'min' in format and values < format['min']:
            return False
        if 'max' in format and values > format['max']:
            return False
        # TODO: truncate floating point numbers that have too much precision
    elif 'array' == format['type']:
        if not isinstance(values, list):
            return False
        if 'max_length' in format and len(values) > format['max_length']:
            return False
        for item in values:
            if not check_format(format['item'], item):
                return False
    else:  # unsupported type
        return False
    return True


correct_json = json.loads('''{
    "score": 12,
    "penalties": [-5, -4.4, -6],
    "working": true
}''')
print(correct_json)
print(check_format(score_format, correct_json))
print(check_format(score_format, json.loads('''{
    "score": -5,
    "penalties": [-5, -4.4, -6],
    "working": true
}''')))
print(check_format(score_format, json.loads('''{
    "score": 12,
    "penalties": [-5, -4.4, -6, 8, 7, 19],
    "working": true
}''')))

