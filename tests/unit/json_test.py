from flask.json import dumps, loads, jsonify, load
from .data import test_json_data, test_json_json, test_json_jsonify

def test_json_serialization(test_client, init_database):
    """
    GIVEN a Python dictionary
    WHEN the dictionary is serialized into a JSON string
    THEN check that the string is formed correctly.
    """
    
    js = dumps(test_json_data)
    jsf = jsonify(test_json_data)
    
    assert js == test_json_json
    # assert jsf.data == test_json_jsonify

def test_json_deserialization(test_client, init_database):
    """
    GIVEN a JSON string
    WHEN the string is deserialized into a Python dictionary
    THEN check that the dictionary is formed correctly.
    """

    js = loads(test_json_json)
    jsf = loads(test_json_jsonify)
    
    assert js == test_json_data
    assert jsf == test_json_data
