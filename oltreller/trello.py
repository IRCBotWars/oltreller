############################################################
# FILENAME: trello.py
#
# AUTHOR(S): Brandon K. Miller <brandonkentmiller@gmail.com>
#
# DESCRIPTION: trello API handler logic
############################################################

from trello import TrelloClient

class TrelloCli:
    '''
    Class for handling Trello API calls
    '''
    def __init__(self, key, secret):
        self._client    = TrelloClient(api_key=key, token=secret)
        self._whitelist = []

    def _get_board_by_name(self, boards, board_name):
        '''
        Gets board from board list by name
        '''
        board = None
        for b in boards:
            if b.name.decode('utf-8') == board_name:
                board = b
        return board

    def set_board_whitelist(self, whitelist):
        '''
        Sets board whitelist - list of boards that IRC users are able to access
        '''
        self._whitelist = whitelist

    def get_board_list(self):
        '''
        Query boards from Trello and check them against the whitelist
        '''
        boards = self._client.list_boards()
        allowed_boards = []
        for b in boards:
            if b.name.decode('utf-8') in self._whitelist and b.closed == False:
                allowed_boards.append(b)
        
        return allowed_boards

    def get_board_cards(self, board_name, typ='open'):
        '''
        Query cards on specific trello board
        '''
        boards = self.get_board_list()
        board  = self._get_board_by_name(boards, board_name)
        if typ == 'all':
            return board.all_cards()
        elif typ == 'closed':
            return board.closed_cards()
        elif typ == 'open':
            return board.open_cards()

    def get_board_lists(self, board_name, typ='open'):
        '''
        Query lists on specific trello board
        '''
        boards = self.get_board_list()
        board = self._get_board_by_name(boards, board_name)
        if typ == 'all':
            return board.all_lists()
        elif typ == 'closed':
            return board.closed_lists()
        elif typ == 'open':
            return board.open_lists()
