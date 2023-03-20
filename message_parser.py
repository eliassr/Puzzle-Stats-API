import json 
import requests
import numpy as np
import pandas as pd

from util import game_dict, handler_dict

def get_tokens():
    """
    Collects Auth-token and channel id for discord channel. They must be saved in 
    local file "tokens.txt" on path. 
    
    To get channel ID: Toggle developer mode (discord->settings->advanced) and
    right click channel -> copy ID

    To get auth token: Open discord in browser -> Developer tools -> Network
    -> Locate entry that says "messages?limit=<some number> -> Request headers
    -> authorization -> copy

    Returns:
        - channel_id: Channel ID
        - h: Authorization string
    """
    with open('tokens.txt') as f: lines=f.readlines()
    auth = lines[0][:-1]
    channel_id = lines[1]
    return channel_id, auth


def get_message_contents_from_channel(channel_id, auth):
    """
    Collect messages from a discord channel, and pass to get_message_values for processing.

    Arguments:
        - channel_id: ID of channel
        - header: Authentication header for API request.
    Returns:
        - msgs: List of messages from channel
        - atrs: Authors of messages in msgs
        - dts:  Timestamps of messages in msgs
    """
    limit=10                            # Messages to collect at once
    last_msg_id = None                  # Set to none to pass 
    header = {'authorization': auth}    # Authorization header

    # Storage for desired values
    msgs,atrs,dts = [[] for i in range(3)]

    n = 0
    while True:
        query_params = f'limit={limit}'
        if last_msg_id is not None:
            query_params += f'&before={last_msg_id}'

        r = requests.get('https://discord.com/api/v9/channels/' + channel_id + '/messages?'+query_params, headers=header)
        j = json.loads(r.text)

        if not j or n>500:
            break

        m = [c['content'] for c in j]
        a = [c['author']['username'] for c in j]
        dt= [c['timestamp'] for c in j]

        msgs.extend(m)
        atrs.extend(a)
        dts.extend(dt)

        last_msg_id = j[-1]['id']
        n+=1
    return msgs,atrs,dts


def message_parser(msg, game_dict, handler_dict):
    """
    Take in a message from the chat and output data from it, such as the score. 
    Returns None placeholder for messages that do not adhere to defined games
    Some games may not be well-handled if the game failed. Might be fixed at some point

    Arguments:
        - msg. String with message content
    Returns:
        - Type of game
        - Score
        - Number for the game
    """
    
    # Dict with key being first word in a message, and value being corresponding game

    msg_words = msg.split()

    # Handle empty messages 
    try:
        first_word = msg_words[0]
    except IndexError:
        return ('N/A: Empty message',None,None)

    # Handle messages that are not about a specific game
    try: 
        game_type = game_dict[first_word]
    except KeyError:
        return ('N/A: Other message',None,None)
    
    for game,handler in handler_dict:
        if game == game_type:
            game_score, game_num = handler(msg_words)
            break 
    else:
        return ('N/A: No handler found',None,None)

    return game_type, game_score, game_num


def create_dataframe(msgs,atrs,dts):
    """
    Create pandas dataframe to store desired data from messages

    Arguments:
        - msgs: Messages from discord channel
        - atrs: Authors of messages
        - dts:  Timestamps of messages
    Returns:
        - df: Pandas dataframe with structured data
    """

    ts = [pd.to_datetime(d) for d in dts]
    dats = [d.date() for d in ts]

    lst = [message_parser(msg, game_dict, handler_dict) for msg in msgs]
    types,scores,nums  = [[x[i] for x in lst] for i in range(3)]

    dct = {'Timestamp':ts,
        'Date': dats,
        'Author':atrs,
        'Game_Type':types,
        'Score':scores,
        'Game_num':nums,
        'Full_Message':msgs}
    df = pd.DataFrame(dct)
    return df

def collect_data():
    """
    Master function to collect data and return dataframe

    """
    channel_id, auth = get_tokens()
    msgs, atrs, dts = get_message_contents_from_channel(channel_id=channel_id,auth=auth)
    df = create_dataframe(msgs,atrs,dts)
    return df