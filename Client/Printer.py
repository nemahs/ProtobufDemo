from Message.protoc_pb2 import Response


def printError(response):
    print("ERROR: ", end='')
    print(response.error_message)


def printTableList(response):
    print("Tables:")
    for name in response.value:
        print('\t-{}'.format(name))


def printTable(table):
    print(table.name)
    for key,value in table.values.items():
        print('\t{}={}'.format(key, value))


def printResponse(response):
    if response.type == Response.ERROR:
        printError(response)
    elif response.type == Response.OK:
        print("Operation was successful")
    elif response.type == Response.DATA:
        if len(response.value) == 1:
            print("Value: {}".format(response.value[0]))
        elif len(response.data) == 1:
            printTable(response.data[0])
        elif len(response.data) > 1:
            print("-----TABLES-----")
            for table in response.data:
                printTable(table)
    elif response.type == Response.LIST:
        printTableList(response)