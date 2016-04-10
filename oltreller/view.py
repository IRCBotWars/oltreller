############################################################
# FILENAME: view.py
#
# AUTHOR(S): Brandon K. Miller <brandonkentmiller@gmail.com>
#
# DESCRIPTION: formats Trello outputs for IRC command
#              responses
############################################################

def _status(closed):
    '''
    Returns status identifier from bool
    '''
    if closed == True:
        return '(C)'
    elif closed == False:
        return '(O)'

def view_board_list(boards):
    '''
    Style format list of boards
    '''
    view = []
    for b in boards:
        view.append("[B] {0} >> {1}".format(b.name.decode('utf-8'), b.id))
    return view

def view_board_lists(board, lists):
    '''
    Style format lists by board name
    '''
    view = ["------ {0} (Lists) ------".format(board)]
    for l in lists:
        view.append("[L] {0} {1} >> {2}\n".format(
                l.name.decode('utf-8'),
                _status(l.closed), l.id))
    return view

def view_board_cards(board, cards):
    '''
    Style format the cards
    '''
    view = ["------ {0} (Cards) ------\n".format(board)]
    for c in cards:
        view.append("[C] {0} {1} >> {2}\n".format(
                c.name.decode('utf-8')[0:40],
                _status(c.closed),
                c.id))
    return view
