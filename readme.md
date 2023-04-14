# Puzzle Stats Parser

Collect messages from discord channel to log statistics on daily puzzles games, e.g. Wordle. 

## Currently supported games

The games currently supported are:

- [Mini crossword](https://www.nytimes.com/crosswords/game/mini) (see notes below)
- [Wordle](https://www.nytimes.com/games/wordle/index.html)
- [Nerdle](https://nerdlegame.com/)
- [Mini Nerdle](https://mini.nerdlegame.com/game)
- [Micro Nerdle](https://micro.nerdlegame.com/game)
- [Instant Nerdle](https://instant.nerdlegame.com/game)
- [Quordle](https://www.merriam-webster.com/games/quordle/#/)
- [Sequence](https://www.merriam-webster.com/games/quordle/#/sequence)
- [Flagle](https://flagle-game.com/)
- [Flagle.io](https://www.flagle.io/)
- [Angle](https://angle.wtf/)
- [Countryle](https://countryle.com/) 
- [Capitale](https://capitale.countryle.com/) 

More games might be added in the future. 

### Notes on mini crossword

Mini crossword does not have a useable share-function. To correctly parse Mini crossword, results (the time spent solving) must be manually written to discord channel on the form:

```
Mini1: 1m23s
```

## Python installation & required modules

Code is tested with Python version `3.11.2`. A python installation later than `3.8` is required, but not guaranteed to be stable. 

Required modules:
- `numpy` `>1.24.2`
- `pandas` `>1.5.3`
- `requests` `>2.28.2`

### Virtual environment

It is always good practice to run the code in a [virtual environment](https://docs.python.org/3/library/venv.html). With your venv active, run 

```
$ pip install -r requirements.txt
```

to install the necessary dependencies. 

## How to use

Below follows a rough guide on how to use the included functionality.

Firstly, clone the repository. Make sure to use the most recent stable release (use dev branches at your own risk!). 

1. The result text for each game (e.g. from share button) should be posted in your favorite discord channel. See notes below on some caveats. 
2. Collect [authentication token](https://discordhelp.net/discord-token) and [channel id](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) for your discord channel of choice. 
3. Save token and channel id in a local file `tokens.txt` on a path accessible to the python module (such as the root directory of the repository). 
4.  The `message_parser` module can be imported in a python environment of your choice, such as 
    - Regular python script
    - Jupyter notebook
    - The python environment for your own discord bot
    
    by running the import statement
    ```
    import message_parser as MP
    ```
5. Use the internal functions, such as `MP.collect_data()` or `MP.update_df()` to get a pandas dataframe with your game data. 
6. Some additional functionality and utilities can be found in `util.py`, such as numerical parsing of scores. Refer to docstrings in the scripts for more info. 


### Notes on discord channel

It is recommended to have a dedicated text-channel for posting scores. While the parser will handle (most) other messages fine, they will add extra time to the query process, and might clutter the final dataset with unneccesary messages. In particular, do avoid posting messages where the first word corresponds to the individual game-keywords, as this might cause errors (particularly in the case of Quordle, whose identifier is the word "Daily"). 

## License

Project is licensed under the MIT License. See [LICENSE.md](/LICENSE.md) for more info. 