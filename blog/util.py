from fanteweb import FanteWeb
import json

def jsonify(**kwargs):
    content = json.dumps(kwargs)
    response = FanteWeb.Response()
    response.content_type = "application/json"
    # response.status_code = status
    response.body = "{}".format(content).encode()
    return response

def validate(d:dict, name:str, type_func, default, func):
    try:
        result = d.get(name, default)
        result = type_func(result)
        result = func(result, default) # (result, default) => result if result < 1 or result > 100 else default
    except:
        result = default
    return result