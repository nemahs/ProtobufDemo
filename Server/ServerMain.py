import socket

from Message.protoc_pb2 import Request, Response


class Server:

    def __init__(self):
        self.database = dict()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def error(message):
        response = Response()
        response.type = Response.ERROR
        response.error_message = message
        return response

    @staticmethod
    def sendMessage(socket, message):
        converted_message = message.SerializeToString()
        socket.send(len(converted_message).to_bytes(4,byteorder='big'))
        socket.send(converted_message)

    def getData(self, request):
        response = Response()
        if request.table == "all":  # Dump database
            response.type = Response.DATA
            for table, value in self.database.items():
                t = response.data.add()
                t.name = table
                for key, val in value.items():
                    t.values[key] = val
        elif request.table == 'tables':  # Return list of tables
            response.type = Response.LIST
            for name in self.database.keys():
                response.value.append(name)
        else:
            if not request.key:
                response.type = Response.DATA  # Get value from key
                t = response.data.add()
                t.name = request.table
                for key, value in self.database[t.name].items():
                    t.values[key] = value
            else:
                if request.key in self.database[request.table]:
                    response.type = Response.DATA
                    response.value.append(self.database[request.table][request.key])
        return response

    def updateData(self, request):
        response = Response()
        if request.key:
            if request.key in self.database[request.table]:
                self.database[request.table][request.key] = request.value
                response.type = Response.OK
                print('Updated {}.{} to {}'.format(request.table, request.key, request.value))
            else:
                response = self.error('Key does not exist!')
        else:
            response = self.error('Missing key!')
        return response

    def deleteData(self, request):
        response = Response()
        if request.key:
            if request.key in self.database[request.table]:
                self.database[request.table].pop(request.key)
                response.type = Response.OK
                print('Deleted {}.{} = {}'.format(request.table, request.key, request.value))
            else:
                response = self.error('Key does not exist!')
        else:
            if request.table in self.database:
                self.database.pop(request.table)
                response.type = Response.OK
                print('Deleted table {}'.format(request.table))
            else:
                response = self.error('Table does not exist!')
        return response

    def addData(self, request):
        response = Response()
        if request.key and request.table in self.database:
            if request.key not in self.database[request.table]:
                self.database[request.table][request.key] = request.value
                print('Added {}.{} to table {}'.format(request.key, request.value, request.table))
                response.type = Response.OK
            else:
                response = self.error('Key already exists! Use SET to update this value')
        else:
            if request.table not in self.database:
                self.database[request.table] = dict()
                print('Added new table {}'.format(request.table))
                response.type = Response.OK
            else:
                response = self.error('Table already exists!')
        return response

    def run(self):
        self.sock.bind(('', 12380))
        self.sock.listen(5)
        print("Listening for clients...")
        while True:
            client, address = self.sock.accept()
            print("Got new client")

            while True:
                try:
                    length = client.recv(4)
                    message = bytes()

                    if len(length) == 0:
                        break

                    length = int.from_bytes(length, byteorder='big')

                    bytes_read = 0
                    while len(message) < length:
                        chunk = client.recv(min(length - bytes_read, length))
                        message += chunk
                        bytes_read += len(chunk)
                except ConnectionResetError:
                    print("Client hung up! How rude!")
                    break

                request = Request.FromString(message)

                if request.type == Request.GET:
                    response = self.getData(request)
                elif request.type == Request.PUT:
                    response = self.updateData(request)
                elif request.type == Request.POST:
                    response = self.addData(request)
                elif request.type == Request.DELETE:
                    response = self.deleteData(request)

                self.sendMessage(client,response)

if __name__ == "__main__":
    server = Server()
    server.run()


