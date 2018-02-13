import requests
import os
from dateutil.parser import parse

board_id = '59e1f9a6218e9f5353dd04d0'

url = 'https://api.trello.com/1/boards/{}/actions?key={}&token={}'.format(
    board_id,
    os.environ.get('TRELLO_KEY'),
    os.environ.get('TRELLO_TOKEN')
)

move_to_list_ids = ['59fc2909e5e658ab257cc042']

start = '2015-02-12 17:49:55.893000+00:00'
end = '2019-02-12 17:51:55.893000+00:00'

sdt = parse(start)
edt = parse(end)

r = requests.get(url)
data = r.json()



for entry in data:
    dt = parse(entry['date'])
    if dt < edt and dt > sdt:
        type = entry['type']
        date = entry['date']
        board = entry['data']['board']['name']
        member = entry['memberCreator']['fullName']
        if type == 'updateCard':
            if 'listAfter' in entry['data'] and 'listBefore' in entry['data']:
                before_name = entry['data']['listBefore']['name']
                after_name = entry['data']['listAfter']['name']
                card_name = entry['data']['card']['name']
                if entry['data']['listAfter']['id'] in move_to_list_ids:
                    print '{} - {} ({})'.format(board, member, date)
                    print '-----------------------------------------------------'
                    print 'Task: ({}) moved from ({}) to ({})'.format(card_name, before_name, after_name)
                    print
