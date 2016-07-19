from token_and_api_key import *
import pymongo
from .parser import Parser

conn = pymongo.MongoClient()
db = conn['dota2-db']


def get_recent_matches(player_id):
    p = 0

    custom_args = {'players.account_id': player_id}
    cursor = db['matches_all'].find(custom_args)
    cursor.sort('start_time', -1)
    hist = list(cursor)
    match_ids = []

    data = Parser.get_match_history(player_id)

    if data:
        k = 0
        while True:
            if hist[0]['match_id'] != data['matches'][k]['match_id']:
                match_ids.append(data['matches'][k]['match_id'])
                print("{}".format(k))
                k += 1
            else:
                break
    else:
        return "Dota 2 api is down"
    if len(match_ids) != 0:
        for i in match_ids:
            data2 = Parser.get_match_details(i)
            if data2:
                db['matches_all'].insert_one(data2)
                p += 1
            else:
                return "Dota 2 api is down"
    else:
        print('No new matches to parse')
    return p

#if __name__ == '__main__':
#    get_recent_matches()
