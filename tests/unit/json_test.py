from flask.json import dumps, loads, jsonify, load
from .data import test_json_data, test_json_json, test_json_jsonify

def test_json_serialization(test_client):
    js = dumps(test_json_data)
    jsf = jsonify(test_json_data)
    
    assert js == test_json_json
    # assert jsf.data == test_json_jsonify

def test_json_deserialization(test_client):
    js = loads(test_json_json)
    jsf = loads(test_json_jsonify)
    
    assert js == test_json_data
    assert jsf == test_json_data
