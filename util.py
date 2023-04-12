"""
Utilities for Puzzle parser.

Contains miscellaneous function definitions, variable declarations, and
handlers for all the different puzzle types.
"""
import re


def timestr_to_seconds(tstr: str) -> int | None:
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


def get_fractional_score(score_str: str) -> int | None:
    """
    Many games give score on the form "./.", e.g. wordle's 2/6, 3/6 etc.
    This function takes a score string and returns the first number. 
    Alternatively if it says "X/6" for instance, return 0. 
    If the string does not match the regex "[1-6X]\/[4-6]", return None.

    Arguments:
        - score_str: Score string from parser
    Returns: 
        - Score, cast as int. 
    """
    if re.match(r'[1-6X]\/[4-6]',score_str):
        return 0 if score_str[0]=='X' else int(score_str[0])
    else:
        return None


def get_int_score(score_str: str) -> int | None:
    """
    Get single-number score, e.g. from Countryle which has integer scoring.
    Return None if score_str is not a number. 

    Arguments:
        - score_str: Score string from parser

    Returns:
        - Numeric score
    """
    try:
        s = int(score_str)
    except ValueError:
        s = None 
    finally:
        return s


def get_quordle_score(score_str: str) -> int | None:
    """
    Get score from quordle game. Returns number of attemps (max digit in score_str).
    If game failed (score_str contains at least one 0), return 0
    If score_str does not conform to regex of four digits, return None. 

    Arguments:
        - score_str: Score string from parser

    Returns:
        - Numeric score
    """
    if re.match(r'^\d{4}$',score_str):
        lst = [int(x) for x in score_str]
        return 0 if 0 in lst else max(lst)
    else:
        return None


def score_converter(score_str: str) -> int | None:
    """
    Master function to convert any score str in dataset to a numeric value. 
    Since results from different puzzles come in different forms, we would like them
    to be cast to numeric forms for statistical purposes. 
    To convert scores from undefined forms, a new converter must be added here.
    If the input does not adhere to defined forms, returns None

    Arguments:
        - score_str: A score string from some puzzle, e.g. "3/6" from wordle

    Returns:
        - s: Numeric score, should always be numeric type (int, float etc.) 
    """
    if (s:=get_fractional_score(score_str)) is not None:
        return s
    elif (s:=timestr_to_seconds(score_str)) is not None:
        return s
    elif (s:= get_quordle_score(score_str)) is not None:
        return s
    elif (s:= get_int_score(score_str)) is not None:
        return s
    else:
        return None


def mini_handler(words: list[str]) -> tuple[str,None]:
    """
    Return score and None-type game_num for Mini Crossword, given message
    """
    return words[1], None


def wordle_handler(words: list[str]) -> tuple[str,str]:
    """
    Return score and game number for wordle, given message
    """
    return words[2], words[1]


def nerdle_handler(words: list[str]) -> tuple[str,str]:
    """
    Return score and game number for nerdle, given message
    """
    return words[2], words[1]


def mini_nerdle_handler(words: list[str]) -> tuple[str,str]:
    """
    Return score and game number for mini nerdle, given message
    """
    return words[3], words[2]


def micro_nerdle_handler(words: list[str]) -> tuple[str,str]:
    """
    Return score and game number for micro nerdle, given message
    """
    return words[3], words[2]


def instant_nerdle_handler(words: list[str]) -> tuple[str,str]:
    """
    Return score and game number for instant nerdle, given message
    """
    return words[-2]+words[-1][:-1], words[5]


def quordle_handler(words: list[str]) -> tuple[str,str,str]:
    """
    Parser for quordle score because it's output weirdly. 
    Handles regular quordle and Sequence-variant.

    Arguments:
        - words: List of words in message

    Returns:
        - game_num: Game number for the day
        - score: Sorted score, e.g. 4567. Any failed words will be zeros at the start, e.g. 0078
    """
    # Handle Sequence-Quordle variant
    if (game_type := words[1]) == 'Sequence': words = words[1:]

    # Some early games had hashtags in the message, so clear this out
    game_num = words[2] if '#' not in words[2] else words[2][1:]

    line1 = [x for x in words[3]]
    line2 = [x for x in words[4]]

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

    return game_type, score, game_num
    

def flagle_game_handler(words: list[str]) -> tuple[str,str]:
    """
    Return score and game number for flagle-game, given message
    """
    return words[3], words[1][1:]


def flagle_io_handler(words: list[str]) -> tuple[str,str]:
    """
    Return score and game number for flagle.io, given message
    """
    return words[2], words[1][1:]


def angle_wtf_handler(words: list[str]) -> tuple[str,str]:
    """
    Return score and game number for angle.wtf, given message
    """
    return words[2], words[1][1:]


def countryle_handler(words: list[str]) -> tuple[str,str]:
    """
    Return score and game number for countryle, given message
    No loss-condition, but you may give up, in which case score is 0
    """
    if "Gave" in words: 
        return 0, words[1]
    else:
        return words[4], words[1]


def capitale_handler(words: list[str]) -> tuple[str,str]:
    """
    Return score and game number for capitale, given message
    No loss-condition, but you may give up, in which case score is 0
    """
    if "Gave" in words: 
        return 0, words[1]
    else:
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
    '#Angle': 'Angle.wtf',
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
                     angle_wtf_handler,
                     countryle_handler,
                     capitale_handler]

# Zipper 
handler_dict = dict(zip(puzzle_list,handler_functions))