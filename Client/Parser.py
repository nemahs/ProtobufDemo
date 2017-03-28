class Parser:
    def __init__(self):
        self.options = dict()
        self.help = dict()

    def add(self, command, func, help):
        self.options[command] = func
        self.help[command] = help

    def executeCommand(self, command, *arg):
        if command == 'help':
            print("Commands:")
            for comm, help in self.help.items():
                for message in help:
                    print('\t{}'.format(message))
        else:
            for comm, func in self.options.items():
                if command == comm:
                    func(*arg)
                    return
