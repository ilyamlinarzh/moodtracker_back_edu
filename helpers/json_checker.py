import json


def isJson(string):
    try:
        r = json.loads(string)
        if type(r) is not dict:
            return False

        return True
    except:
        return False
