
import unittest
import json

def get_pair_dict(data):
    all_pairs = [d['pairs'] for d in data]
    pair_dict = {pair: [] for pair in set(all_pairs)}
    for pair in data:
        p = pair['pairs']
        d = pair['created_at']
        pair_dict[p].append(d)
    return pair_dict

def last_concurrent_days(days):
    pass

class TestHistory(unittest.TestCase):
    def test_histroy(self):
        with open('./app/tests/fixtures/pair_history.json') as f:
            data = json.loads(f.read())
        

        print('Pairs', get_pair_dict(data))






