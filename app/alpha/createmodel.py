example1 = ['a', (('c', 'a'), 'b'), ('b', ('c', 'd')), 'd']

example2 = ['s', ('s', ('a', 'b')), (('c', 'a'), 'b'), ('b', ('c', 'd')), (('c', 'd'), 'e'), 'e']


#for transitions [[number, name, from, to], [] ... ]


def transitions(set):
    transitions = []
    for i in range(len(set)):
        transitions.append([])
    for i in range(len(set)):
        if i == 0:
            transitions[i].append('t')
            transitions[i].append('t'+str(i))
            transitions[i].append('')
            transitions[i].append(set[i])
        elif i == len(set) - 1:
            transitions[i].append('t')
            transitions[i].append('t' + str(i))
            transitions[i].append(set[i])
            transitions[i].append('')
        else:
            transitions[i].append('t')
            transitions[i].append('t' + str(i))
            temp = list(set[i])
            for j in range(len(temp)):
                string = ''
                if isinstance(temp[j], tuple):
                    list_of_strings = [str(s) for s in temp[j]]
                    string = "".join(list_of_strings)
                elif isinstance(temp[j], str):
                    string = temp[j]
                if j == 0:
                    transitions[i].append(string)
                elif j == 1:
                    transitions[i].append(string)
    print(transitions)
    return

transitions(example2)
