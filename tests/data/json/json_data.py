from datetime import datetime, date, time

test_json_data = {
    'a': 1,
    'b': 1.1,
    'c': True,
    'd': 'string',
    'e': {
        'aa': 11,
        'bb': 'bigger string'
    },
    'f': [1, 2, 3, 4, 5],
    'g': "1977-04-05",
    'h': time(14, 21, 39, 123456).isoformat(),
    'i': datetime(2020, 6, 7, 12, 39, 46, 123456).isoformat(),
    'j': {
        'ja': {
            'jja': [time(13, 0, 0).isoformat(), time(14, 0, 0).isoformat(), time(15, 0, 0).isoformat()],
        }
    },
    'k': '17a3bee0-42db-4416-8b84-3990b1c6397e',
}

test_json_json = '{"a": 1, "b": 1.1, "c": true, "d": "string", "e": {"aa": 11, "bb": "bigger string"}, "f": [1, 2, 3, 4, 5], "g": "1977-04-05", "h": "14:21:39.123456", "i": "2020-06-07T12:39:46.123456", "j": {"ja": {"jja": ["13:00:00", "14:00:00", "15:00:00"]}}, "k": "17a3bee0-42db-4416-8b84-3990b1c6397e"}'

# This will be run in test, so JSONIFY_PRETTYPRINT_REGULAR is True by default.
# It affects spaces and indentation in jsonify output.
test_json_jsonify = b'{\n  "a": 1, \n  "b": 1.1, \n  "c": true, \n  "d": "string", \n  "e": {\n    "aa": 11, \n    "bb": "bigger string"\n  }, \n  "f": [\n    1, \n    2, \n    3, \n    4, \n    5\n  ], \n  "g": "1977-04-05", \n  "h": "14:21:39.123456", \n  "i": "2020-06-07T12:39:46.123456", \n  "j": {\n    "ja": {\n      "jja": [\n        "13:00:00", \n        "14:00:00", \n        "15:00:00"\n      ]\n    }\n  }, \n  "k": "17a3bee0-42db-4416-8b84-3990b1c6397e"\n}\n'
