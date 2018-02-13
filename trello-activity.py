import requests
import os
from dateutil.parser import parse
from constants import BOARDS_URL, BOARD_ACTIONS_URL, BOARD_LISTS_URL


def get_board_id_from_name(name):
    id = ''
    url = BOARDS_URL.format(
        key=os.environ.get('TRELLO_KEY'),
        token=os.environ.get('TRELLO_TOKEN')
    )
    r = requests.get(url)
    data = r.json()
    for entry in data:
        if entry['name'] == name:
            id = entry['id']
    return id


def get_list_id_from_name(board_name, list_name):
    id = ''
    board_id = get_board_id_from_name(board_name)
    url = BOARD_LISTS_URL.format(
        board_id=board_id,
        key=os.environ.get('TRELLO_KEY'),
        token=os.environ.get('TRELLO_TOKEN')
    )
    r = requests.get(url)
    data = r.json()
    for entry in data:
        if entry['name'] == list_name:
            id = entry['id']
    return id


def get_datetime_string_from_date_time(date, time):
    return '{} {}:00.000000+00:00'.format(date, time)


def format_match(board, member, date, card_name, before_name, after_name):
    header = '{} - {} ({})\n'.format(board, member, date)
    divider = '-----------------------------------------------\n'
    body = 'Task: ({}) moved from ({}) to ({})\n\n'.format(
        card_name,
        before_name,
        after_name
    )
    return header + divider + body


def get_response_from_matches(matches):
    response = ''

    for match in matches:
        response += format_match(
            match['board'],
            match['member'],
            match['timestamp'],
            match['card'],
            match['from_list'],
            match['to_list']
        )
    return response


def get_moves_to_lists(
    board_name,
    list_names,
    start_date,
    start_time,
    end_date,
    end_time
):
    board_id = get_board_id_from_name(board_name)
    list_ids = []
    matches = []

    for name in list_names:
        list_ids.append(
            get_list_id_from_name(board_name, name)
        )

    url = BOARD_ACTIONS_URL.format(
        board_id=board_id,
        key=os.environ.get('TRELLO_KEY'),
        token=os.environ.get('TRELLO_TOKEN')
    )

    start = get_datetime_string_from_date_time(start_date, start_time)
    end = get_datetime_string_from_date_time(end_date, end_time)
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
                if (
                    'listAfter' in entry['data'] and
                    'listBefore' in entry['data']
                ):
                    before_name = entry['data']['listBefore']['name']
                    after_name = entry['data']['listAfter']['name']
                    card_name = entry['data']['card']['name']
                    if entry['data']['listAfter']['id'] in list_ids:
                        matches.append(
                            {
                                'board': board,
                                'member': member,
                                'timestamp': date,
                                'card': card_name,
                                'from_list': before_name,
                                'to_list': after_name
                            }
                        )

    return matches


matches = get_moves_to_lists(
    'JasonsAppFinal',
    ['To Do For Next Week Done', 'Done'],
    '2015-02-12',
    '08:00',
    '2019-02-12',
    '23:59'
)

response = get_response_from_matches(matches)

print response
