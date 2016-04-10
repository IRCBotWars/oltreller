#!/usr/bin/python3
############################################################
# FILENAME: oltreller.py
#
# AUTHOR(S): Brandon K. Miller <brandonkentmiller@gmail.com>
#
# DESCRIPTION: oltreller IRC bot for agile teams
############################################################

import time
import argparse
import os
import re
import configparser
import oltreller.trello as trello
import oltreller.irc as irc
import oltreller.view as view

def process_msg(message, tre_cli):
    '''
    Process message and prepare response if it's a command
    '''
    try:
        mention = '!trello'
        if re.search("^{0}".format(mention), message) == None:
            return None

        fields = message[8:].split(" ")

        if fields[0] == "boards":
            boards = tre_cli.get_board_list()
            return view.view_board_list(boards)

        if fields[0] == "lists":
            if len(fields) < 2:
                return ['!trello lists <board name>']
            lists = tre_cli.get_board_lists(fields[1])
            return view.view_board_lists(fields[1], lists)

        if fields[0] == "cards":
            if len(fields) < 2:
                return ['!trello cards <board name>']
            cards = tre_cli.get_board_cards(fields[1])
            return view.view_board_cards(fields[1], cards)

        return ["!trello help"]
    except AttributeError:
        return ["I could not process your request. Please ensure that spelling and casing is correct."]

def trello_init(key, secret):
    '''
    Construct trello handler
    '''
    try:
        return trello.TrelloCli(key, secret)
    except KeyError:
        print("! set your TRELLO_API_KEY and TRELLO_API_TOKEN environment variables")
        False

def read_config(filename):
    '''
    Read configuration file and return handler
    '''
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def parse_args():
    '''
    Parses CLI arguments
    '''
    parser = argparse.ArgumentParser(description='CLI interface for Argon CPE scraper')
    parser.add_argument('--host', help='IRC server URL or IP address', required=True)
    parser.add_argument('--port', help='IRC server port', default=6697)
    parser.add_argument('--ssl', help='Use SSL for encrypted communications with IRC server', action='store_true') 
    parser.add_argument('--conf', help='Path to configuration file', default='.oltreller.conf')
    args = parser.parse_args()
    return args

def do_work():
    '''
    Main Function
    '''
    args = parse_args()
    
    # construct trello handler with key and OAuth token
    tre_cli = trello_init(os.environ['TRELLO_API_KEY'], os.environ['TRELLO_TOKEN'])
    if (tre_cli == False):
        return

    # read config and set trello board white list
    config = read_config(args.conf)
    tre_cli.set_board_whitelist(str.split(config.get('Trello', 'Whitelist'), ','))

    # setup IRC client handler
    irc_cli = irc.IrcClient(args.host,
                        args.port,
                        args.ssl,
                        config.get('IRC', 'Nickname'),
                        config.get('IRC', 'Login')
    )

    # connect to IRCd and query msg queue recursively
    try:
        print("* connecting to {0}...".format(args.host))
        irc_cli.irc_connect()
        while True:
            queue = irc_cli.get_queue()
            if len(queue) == 0:
                time.sleep(1)
                continue

            for q in queue:
                sender, message = q
                print("{0}: {1}".format(sender, message))
                resp = process_msg(message, tre_cli)
                if resp != None:
                    for m in resp:
                        irc_cli.irc_privmsg(sender, m)
                # handle command here!

            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        irc_cli.irc_close()
        print("! aborting...")

if __name__ == "__main__":
    do_work()
