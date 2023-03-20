"""
Utilities for Puzzle parser.

Contains miscellaneous function definitions, variable declarations, and
handlers for all the different puzzle types.
"""

def timestr_to_seconds(tstr):
    """
    Convert a str on the form "xmys" to a number of seconds (e.g. 1m20s --> 80) 
    """
    try:
        lst = tstr.split('m')
        lst[1] = lst[1].split('s')
        min = int(lst[0])
        sec = int(lst[1][0])
        return 60*min + sec
    except:
        return None


def mini_handler(words):
    """
    Return score and None-type game_num for Mini Crossword, given message
    """
    return words[1], None


def wordle_handler(words):
    """
    Return score and game number for wordle, given message
    """
    return words[2], words[1]


def nerdle_handler(words):
    """
    Return score and game number for nerdle, given message
    """
    return words[2], words[1]


def mini_nerdle_handler(words):
    """
    Return score and game number for mini nerdle, given message
    """
    return words[3], words[2]


def micro_nerdle_handler(words):
    """
    Return score and game number for micro nerdle, given message
    """
    return words[3], words[2]

def instant_nerdle_handler(words):
    """
    Return score and game number for instant nerdle, given message
    """
    return words[-2]+words[-1][:-1], words[5]


def quordle_handler(words):
    """
    Parser for quordle score because it's output weirdly. 

    Not working quite as intended, so keeping a try-except here until issue is resolved. 
    I suspect the format of the message is inconsistent historically.
    Should always output correctly if the game is completely won (all 4 words guessed within attempt 9)

    Arguments:
        - words: List of words in message
    Returns:
        - game_num: Game number for the day
        - score: Sorted score, e.g. 4567. Any failed words will be zeros at the end, e.g. 7800
    """
    game_num = words[2]
    line1 = [x for x in words[3]]
    line2 = [x for x in words[4]]

    try:
        # Check if first entry is fail
        s1 = 0 if line1[0] == '🟥' else line1[0]

        # If any other entries than first is fail, second score is 0. Set according to if first was fail
        if '🟥' in line1[1:]:
            s2 = 0
        elif s1 == 0:
            s2 = line1[1]
        else:
            s2 = line1[3]

        s3 = 0 if line2[0] == '🟥' else line2[0]
        if '🟥' in line2[1:]:
            s4 = 0
        elif s3 == 0:
            s4 = line2[1]
        else:
            s4 = line2[3]

        lst = [int(s) for s in [s1,s2,s3,s4]]
        lst.sort()
        lst_str = [str(x) for x in lst]
        score = "".join(lst_str)
    except:
        score = '0000'
    finally:
        return score, game_num
    

def flagle_game_handler(words):
    """
    Return score and game number for flagle-game, given message
    """
    return words[3], words[1][1:]


def flagle_io_handler(words):
    """
    Return score and game number for flagle.io, given message
    """
    return words[2], words[1][1:]


def angle_io_handler(words):
    """
    Return score and game number for angle.io, given message
    """
    return words[2], words[1][1:]


def countryle_handler(words):
    """
    Return score and game number for countryle, given message
    """
    return words[4], words[1]


def capitale_handler(words):
    """
    Return score and game number for capitale, given message
    """
    return words[4], words[1]



# Dict with key being first word in a message, and value being corresponding game
game_dict = {
    'Mini1:': 'Mini',
    'Wordle': 'Wordle',
    'nerdlegame': 'Nerdle',
    'mini': 'Mini nerdle',
    'micro': 'Micro nerdle',
    '🟩': 'Instant nerdle',
    'Daily': 'Quordle',
    'Flagle': 'Flagle-game',
    '#Flagle': 'Flagle.io',
    '#Angle': 'Angle.io',
    '#Countryle': 'Countryle',
    '#Capitale': 'Capitale'
}

# List of puzzle names
puzzle_list = list(game_dict.values())

# All handler functions. Keep in same order as puzzle_list!
handler_functions = [mini_handler,
                     wordle_handler,
                     nerdle_handler,
                     mini_nerdle_handler,
                     micro_nerdle_handler,
                     instant_nerdle_handler,
                     quordle_handler,
                     flagle_game_handler,
                     flagle_io_handler,
                     angle_io_handler,
                     countryle_handler,
                     capitale_handler]

# Zipper 
handler_dict = list(zip(puzzle_list,handler_functions))