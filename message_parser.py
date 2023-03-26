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

    To get auth token: Open channel in browser -> Developer tools -> Network
    -> Locate entry that says "messages?limit=<some number>" -> Request headers
    -> authorization -> copy

    Returns:
        - channel_id: Channel ID
        - auth: Authorization string
    """
    with open('tokens.txt') as f: lines=f.readlines()
    auth = lines[0][:-1]
    channel_id = lines[1]
    return channel_id, auth


def get_message_contents_from_channel(channel_id, 
                                      auth, 
                                      limit_per_request=10,
                                      max_msgs=5000, 
                                      date_lim='1998-11-25'):
    """
    Collect messages from a discord channel, process them and return desired metadata.

    Allows to set a max amount of messages to process (default 5000) and a maximum
    number of messages per API request (default 10).

    It is also possible to select a date, and the process will halt once reaching this
    date (collection starts at most recent message). Note that since data is fetched in
    chunks, some messages from earlier dates might still be fetched. 

    Messages are collected in json format, see doc link:
    https://discord.com/developers/docs/resources/channel#message-object-message-structure

    Arguments:
        - channel_id: ID of channel
        - header: Authentication header for API request.
        - limit_per_request: Max amount of messages to fetch per API request. 
        - max_msgs: Maximum amount of messages to collect
        - date_lim: Pass 'YYYY-MM-DD' to only fetch messages after this date.
    
    Returns:
        - msgs: List of messages from channel
        - atrs: Authors of messages in msgs
        - dts:  Timestamps of messages in msgs
    """
    limit = limit_per_request           # Messages to collect in one API request
    last_msg_id = None                  # Set to none to pass 
    header = {'authorization': auth}    # Authorization header
    query_params = f'limit={limit}'     # Set initial query params
    
    # Turn date_lim to timestamp object
    date_lim = pd.to_datetime(date_lim).tz_localize('UTC') 

    # Storage for desired values
    msgs,atrs,dts = [[] for i in range(3)]

    for n in range(max_msgs//limit):
        r = requests.get('https://discord.com/api/v9/channels/' + channel_id + '/messages?'+query_params, headers=header)
        j = json.loads(r.text)

        if not j:
            break

        m = [c['content'] for c in j]
        a = [c['author']['username'] for c in j]
        dt= [c['timestamp'] for c in j]

        if pd.to_datetime(dt[-1]) < date_lim:
            break

        msgs.extend(m)
        atrs.extend(a)
        dts.extend(dt)

        last_msg_id = j[-1]['id']
        query_params = f'limit={limit}'
        query_params += f'&before={last_msg_id}'

    return msgs,atrs,dts


def message_parser(msg, game_dict, handler_dict):
    """
    Take in a message from the chat and output data from it, such as the puzzle score. 
    Returns fallback placeholder for messages that do not adhere to defined games.
    Some games may not be well-handled if the game failed. Might be fixed at some point

    Arguments:
        - msg: String with message content
        - game_dict: Dict that maps message content to game
        - handler_dict: Dict that maps game to its message handler
    
    Returns:
        - Type of game
        - Score
        - Number for the game
    """
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
    
    # Fallback to default message if handler not found
    fallback_func = lambda x: ('N/A: No handler found',None,None)
    handler = handler_dict.get(game_type, fallback_func)
    game_score, game_num = handler(msg_words)

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
    Master function to collect data and return dataframe.
    Collects all messages from channel, so might take a while.

    Function can be imported to notebook or other script for simple message parsing:

    import message_parser as MP
    df = MP.collect_data()

    Returns:
        - df: Dataframe of parsed puzzle game data
    """
    channel_id, auth = get_tokens()
    msgs, atrs, dts = get_message_contents_from_channel(channel_id=channel_id,auth=auth)
    df = create_dataframe(msgs,atrs,dts)
    return df


def update_df(pth='data.csv', save_new=False):
    """
    To save time on queries, save a local .csv file with the dataframe. 
    This function will update local copy of dataframe with only new data.
    Should save time by not running large query for every data refresh.  

    Arguments:
        - pth: Path to local file
        - save_new: Choose to save updated to local, will overwrite old file

    Returns:
        - df: Merged dataframe
    """
    try:
        df_old_data = pd.read_csv(pth,index_col=0,parse_dates=['Timestamp','Date'])
    except FileNotFoundError:
        raise Exception('File not found. Check that path is correct, or create file.')
    date_ser = df_old_data['Date']

    # Fetch messages after this date, added 3 days leeway to catch all messages
    latest_date_in_local = (date_ser.head(1).item()-pd.Timedelta(days=3)).strftime(format='%Y-%m-%d')

    channel_id, auth = get_tokens()
    msgs, atrs, dts, = get_message_contents_from_channel(channel_id,
                                                            auth,
                                                            date_lim=latest_date_in_local
                                                            )
    df_new_data = create_dataframe(msgs,atrs,dts)
    df_new_data['Date'] = pd.to_datetime(df_new_data['Date'])

    # Add new data, any overlap is only included once
    df = df_old_data.merge(df_new_data,how='outer')

    # Sort and reset index
    df.sort_values(by='Timestamp',inplace=True,ascending=False)
    df.reset_index(inplace=True,drop=True)

    # Save updated data, overwrites old
    if save_new:
        df.to_csv(pth) 
    return df