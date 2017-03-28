import argparse
import socket

from Client import Printer
from Client.Parser import Parser
from Message.protoc_pb2 import Request, Response


class Client:
    def __init__(self, args):
        self.cont = True
        # Setup parser
        self.parser = Parser()
        self.parser.add('add', self.addItem, ('ADD tablename : Add new table',
                                              'ADD tablename.key=value : Add new key,value pair'))
        self.parser.add('show', self.requestTable, ('SHOW ALL: Show the entire database',
                                                    'SHOW TABLES: Show all table names',
                                                    'SHOW tablename: Show all data in table',))
        self.parser.add('get', self.getValue, ('GET tablename.key: Get value from key',))
        self.parser.add('set', self.setValue, ('SET tablename.key=value: Set value to key',))
        self.parser.add('delete', self.deleteItem, ('DELETE tablename.key: Delete par from table',
                                                    'DELETE tablename: Delete table from db'))
        self.parser.add('exit', self.exit, ('EXIT: Closes client',))
        # Connect
        self.sock = socket.socket()
        self.sock.connect((args.address, 12380))
        print("Connected to " + args.address)

    def sendMessage(self, message):
        converted_message = message.SerializeToString()
        length = len(converted_message).to_bytes(4, byteorder='big')
        self.sock.send(length)
        self.sock.send(converted_message)
        self.receiveMessage()

    def receiveMessage(self):
        length = self.sock.recv(4)
        length = int.from_bytes(length, byteorder='big')
        message = bytes()
        bytes_read = 0
        while len(message) < length:
            chunk = self.sock.recv(min(length - bytes_read, length))
            message += chunk
            bytes_read += len(chunk)

        if length == 0:
            print("Socket closed, good bye") # TODO: Fix me!
            self.exit()
            return

        response = Response.FromString(message)
        Printer.printResponse(response)


    def exit(self):
        self.cont = False

    def requestTable(self, command):
        request = Request()
        table_name = command.lower()
        request.type = Request.GET
        request.table = table_name
        self.sendMessage(request)

    def addItem(self, subcommand):
        request = Request()
        subcommand = subcommand.split('.')
        request.type = Request.POST
        request.table = subcommand[0]
        if len(subcommand) > 1:
            kv = subcommand[1].split('=')
            request.key = kv[0]
            request.value = kv[1]
        self.sendMessage(request)

    def setValue(self, command):
        request = Request()
        request.type = Request.PUT
        command = command.split('.')
        request.table = command[0]
        subcommand = command[1].split('=')
        request.key = subcommand[0]
        request.value = subcommand[1]
        self.sendMessage(request)

    def getValue(self, command):
        request = Request()
        request.type = Request.GET
        command = command.split('.')
        request.table = command[0]
        request.key = command[1]
        self.sendMessage(request)

    def deleteItem(self, command):
        request = Request()
        request.type = Request.DELETE
        command = command.split('.')
        request.table = command[0]
        if len(command) > 1:
            request.key = command[1]

        self.sendMessage(request)

    def run(self):
        while self.cont:
            # Do stuff
            command = input('> ')
            command = command.lower().split(' ')
            self.parser.executeCommand(*command)
        self.sock.close()


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(description='Netcat like program for protocol buffers demonstration.')
    parser.add_argument('address', nargs="?", default="localhost", help="Address of remote server")
    args = parser.parse_args()
    c = Client(args)
    c.run()
