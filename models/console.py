
def read():
    line = input()
    if line == '':
        return 'default', None

    tokens = line.split(' ')
    command = tokens[0]
    if command == 'train':
        parameter = None
    elif command == 'exit':
        parameter = None
    elif command == 'get_moves' or command == 'evaluate':
        is_red = int(tokens[1]) == 1
        board = tokens[2].replace('#', ' ')
        parameter = is_red, board

    return command, parameter
