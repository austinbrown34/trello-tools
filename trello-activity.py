import requests
import os
import sys
import ast
import argparse
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
    date_pieces = date.split('-')
    new_date = '{}-{}-{}'.format(
        date_pieces[2],
        date_pieces[0],
        date_pieces[1]
    )
    return '{} {}:00.000000+00:00'.format(new_date, time)


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
            action_type = entry['type']
            date = entry['date']
            board = entry['data']['board']['name']
            member = entry['memberCreator']['fullName']
            if action_type == 'updateCard':
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


def show_response(
    board_name,
    list_names,
    start_date,
    start_time,
    end_date,
    end_time
):

    matches = get_moves_to_lists(
        board_name,
        list_names,
        start_date,
        start_time,
        end_date,
        end_time
    )

    response = get_response_from_matches(matches)

    print(response)


def main(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "board_name",
        help="Name of Trello Board"
    )

    parser.add_argument(
        "list_names",
        help="List of 'List Names'"
    )

    parser.add_argument(
        "start_date",
        help="Start Date (MM-DD-YYYY)",

    )

    parser.add_argument(
        "start_time",
        help="Start Time (HH:MM) Military",

    )

    parser.add_argument(
        "end_date",
        help="End Date (MM-DD-YYYY)",

    )

    parser.add_argument(
        "end_time",
        help="End Time (HH:MM) Military",
    )

    args = parser.parse_args()

    show_response(
        args.board_name,
        ast.literal_eval(args.list_names),
        args.start_date,
        args.start_time,
        args.end_date,
        args.end_time
    )


if __name__ == '__main__':
    main(sys.argv)
