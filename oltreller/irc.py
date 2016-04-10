############################################################
# FILENAME: irc.py
#
# AUTHOR(S): Brandon K. Miller <brandonkentmiller@gmail.com>
#
# DESCRIPTION: threaded IRC class for oltreller
############################################################

import ssl
import socket
import re
import threading
import time

class IrcClient:
    def __init__(self, host, port, ssl, nick, user):
        self._host     = host
        self._port     = port
        self._ssl      = ssl
        self._nick     = nick
        self._user     = user
        self._sock     = None
        self._thread   = None
        self._continue = False
        self._tlock    = False
        self._queue    = []

    def _send_msg(self, msg):
        '''
        Send message over socket (thread safe)
        '''
        while True:
            if self._tlock == True:
                time.sleep(1000)
                continue

            self._tlock = True
            self._sock.send(msg.encode('utf-8'))
            self._tlock = False
            break

    def _parse_sender(self, buf):
        '''
        Parses sender from buffer
        '''
        sender = ''
        for c in buf:
            if c == '!':
                break

            if c != ':':
                sender += c

        return sender

    def _recv_loop(self):
        '''
        IRC receive loop
        '''
        buf = ''
        while self._continue:
            try:
                buf = buf + self._sock.recv(1024).decode('utf-8')
            except socket.timeout:
                continue

            lines = str.split(buf, "\n")
            buf = lines.pop()

            for line in lines:
                # strip and split line
                line = str.rstrip(line)
                words = str.split(line)
                if len(words) == 0:
                    continue

                if words[0] == 'PING':
                    self.irc_pong(words[1])

                if words[1] == 'PRIVMSG':
                    # parse message sender
                    sender = self._parse_sender(words[0])
                    message = " ".join(words[3:])
                    message = message.lstrip(':')
                    self._queue.append([sender, message])

    def irc_pong(self, resp):
        '''
        Respond to ping request
        '''
        self._send_msg("PONG {0}\r\n".format(resp))

    def irc_join_chan(self, channel):
        '''
        Join channel
        '''
        self._send_msg("JOIN {0}\r\n".format(channel))

    def irc_nick(self):
        '''
        Request nickname from IRCd
        '''
        self._send_msg("NICK {0}\r\n".format(self._nick))

    def irc_user(self):
        '''
        Request user from IRCd
        '''
        self._send_msg("USER {0} 8 * :Ol Treller\r\n".format(self._user))

    def irc_connect(self):
        '''
        Connect to IRCd server
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((self._host, self._port))
        if self._ssl == True:
            self._sock = ssl.wrap_socket(sock)
        else:
            self._sock = sock

        # start reader thread
        self._continue = True
        self._thread = threading.Thread(target=self._recv_loop)
        self._thread.daemon = True
        self._thread.start()
        # request nick and user names
        self.irc_nick()
        self.irc_user()

    def irc_privmsg(self, channel, msg):
        '''
        Send private messages
        '''
        self._send_msg("PRIVMSG {0} :{1}\r\n".format(channel, msg))

    def irc_close(self):
        '''
        Exit cleanly
        '''
        self._continue = False
        self._thread.join()
        self._sock.close()

    def get_queue(self):
        '''
        Get and return message queue
        '''
        queue = self._queue
        self._queue = []
        return queue
