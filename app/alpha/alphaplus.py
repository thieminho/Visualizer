import pandas as pd
import os
cur_dir_path = os.path.dirname(os.path.realpath(__file__))

# TODO: Preprocessing logs to the form of case_id, act_name?


def read_csv_into_df(file_name):
    df = pd.read_csv(file_name)
    print(df)
    return df


def find_sets(dataframe):
    all_events = dataframe.act_name.unique()
    start_events = []
    end_events = []
    cases = dataframe.case_id.unique()
    for case in cases:
        tasks = []
        df = dataframe[dataframe.case_id.eq(case)]
        task = list(df.act_name)
        if task[0] not in start_events:
            start_events.append(task[0])
        if task[int(len(task)-1)] not in end_events:
            end_events.append(task[int(len(task)-1)])
    return all_events, start_events, end_events


def preprocess_for_one_loops(dataframe):
    #[from, to, node]
    cases = dataframe.case_id.unique()
    one_loops = []
    a = 0
    for case in cases:
        df = dataframe[dataframe.case_id.eq(case)]
        task = list(df.act_name)
        start = True
        for i in range(len(task) - 1):
            a += 1
            if task[i] == task[i+1] and start:
                from_act = task[i-1]
                item = task[i]
                start = False
                continue
            elif task[i] == task[i+1]:
                continue
            elif task[i] != task[i+1] and not start:
                to_act = task[i+1]
                a += 1
                if [from_act, to_act, item] not in one_loops:
                    one_loop = [from_act, to_act, item]
                    one_loops.append(one_loop)
                start = True
                dataframe.drop(dataframe[dataframe['act_name'] == item].index, inplace=True)
    return dataframe, one_loops


def insert_one_loops_finally(transitions, one_loops):
    if len(one_loops) > 0:
        for loop in one_loops:
            for transition in transitions:
                if loop[0] in list(transition[2]) and loop[1] in list(transition[3]):
                    transition[2] += f';{loop[2]}'
                    transition[3] += f';{loop[2]}'
                    break
                else:
                    continue
    return transitions


def create_footprint_matrix(dataframe):
    all_events = list(dataframe.act_name.unique())
    cases = dataframe.case_id.unique()
    causality = set()
    parallel = set()
    non_related = set()
    sequences = []
    trios = []
    for case in cases:
        df = dataframe[dataframe.case_id.eq(case)]
        task = list(df.act_name)
        for i in range(0, len(task) - 2):
            if task[i + 2] == task[i]:
                trios.append((task[i], task[i + 1], task[i + 2]))
        for i in range(0, len(task) - 1):
            sequences.append((task[i], task[i + 1]))
        for activity in all_events:
            for second_activity in task:
                if (activity, second_activity) not in non_related and (second_activity, activity) not in non_related:
                    if (activity, second_activity) not in sequences and (second_activity, activity) not in sequences:
                        non_related.add((activity, second_activity))
    for sequence in sequences:
        if (sequence[0], sequence[1]) in sequences and \
                ((sequence[1], sequence[0]) not in sequences or
                 ((sequence[1], sequence[0], sequence[1]) in trios or
                  (sequence[0], sequence[1], sequence[0]) in trios)):
            causality.add(sequence)
        if (sequence[0], sequence[1]) in sequences and (sequence[1], sequence[0]) in sequences and \
                ((sequence[1], sequence[0], sequence[1]) not in trios and
                 (sequence[0], sequence[1], sequence[0]) not in trios):
            if (sequence[0], sequence[1]) not in parallel and (sequence[1], sequence[0]) not in parallel:
                parallel.add(sequence)
    return causality, parallel, non_related


def find_more_sets(sets, non_related):
    fin = []
    sets = list(sets)
    for i in range(len(sets)):
        trans_after = []
        trans_before = []
        for j in range(len(sets)):
            if sets[i] == sets[j]:
                continue
            elif sets[i][0] == sets[j][0]:
                if (sets[i][1], sets[j][1]) in non_related:
                    if sets[i][1] not in trans_after:
                        trans_after.append(sets[i][1])
                    if sets[j][1] not in trans_after:
                        trans_after.append(sets[j][1])

                    fin.append((sets[i][0], tuple(trans_after)))
            elif sets[i][1] == sets[j][1]:
                if (sets[i][0], sets[j][0]) in non_related:
                    if sets[i][0] not in trans_before:
                        trans_before.append(sets[i][0])
                    if sets[j][0] not in trans_before:
                        trans_before.append(sets[j][0])
                    fin.append((tuple(trans_before), sets[i][1]))
        if trans_before == [] or trans_after == []:
            continue
    return fin


def find_possible_sets(causals_set, non_related_set):
    print(non_related)
    non_related_set_copy = non_related_set.copy()
    for nr in non_related_set_copy:
        if nr[0] == nr[1]:
            non_related_set.remove(nr)
        else:
            continue
    xl = causals_set.copy()
    for nr in non_related_set:
        for causals in causals_set:
            print(causals)
            print(nr)
            if (causals[0], nr[0]) in causals_set and (causals[0], nr[1]) in causals_set:
                xl.add((causals[0], (nr)))
            if (nr[0], causals[1]) in causals_set and (nr[1], causals[1]) in causals_set:
                xl.add(((nr), causals[1]))

    yl = xl.copy()
    print(xl)
    for x in xl:
        a = set(x[0])
        b = set(x[1])
        for y in xl:
            if a.issubset(y[0]) and b.issubset(y[1]):
                if x != y:
                    yl.discard(x)
                    break
    to = yl.copy()
    for t in to:
        for x in xl:
            if t == x[0]:
                yl.discard(t)

    ql = list(yl)
    fin = find_more_sets(yl, non_related)
    while True:
        last = fin
        fin = find_more_sets(fin, non_related)
        if fin == []:
            break
    fin = last
    for set1 in ql:
        fin.append(set1)
    fin = set(fin)
    yl = fin.copy()
    print(xl)
    for x in fin:
        a = set(x[0])
        b = set(x[1])
        for y in fin:
            if a.issubset(y[0]) and b.issubset(y[1]):
                if x != y:
                    yl.discard(x)
                    break
    yl = list(yl)
    return yl


def insert_start_end(possible_sets, start, end):
    if (len(start)) > 1:
        possible_sets.insert(0, ('START', tuple(start)))
        possible_sets.insert(0, 'START')
    else:
        possible_sets.insert(0, start[0])
    if (len(end)) > 1:
        possible_sets.append((tuple(end), 'END'))
        possible_sets.append('END')
    else:
        possible_sets.append(end[0])
    return possible_sets


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
                    string = ";".join(list_of_strings)
                elif isinstance(temp[j], str):
                    string = temp[j]
                if j == 0:
                    transitions[i].append(string)
                elif j == 1:
                    transitions[i].append(string)
    return transitions


def activities(all_events):
    activities = []
    for i in range(len(all_events)):
        activities.append([])
        activities[i].append('a')
        activities[i].append(all_events[i])
    return activities


def write_to_csv(transitions, activities, name, path):
    dir_path = path
    result = []
    with open(os.path.join(dir_path, f"{name}.csv"), "w") as file:
        file.write("%s\n" % 'type,id,from,to')
        for activity in activities:
            activity = str(activity)
            activity = activity.replace('[', '')
            activity = activity.replace(']', '')
            activity = activity.replace('\'', '')
            activity = activity.replace(' ', '')
            file.write("%s\n" % activity)
        for transition in transitions:
            transition = str(transition)
            transition = transition.replace('[', '')
            transition = transition.replace(']', '')
            transition = transition.replace('\'', '')
            transition = transition.replace(' ', '')
            file.write("%s\n" % transition)
    return


df = read_csv_into_df('example4.csv')
all_events, start_events, end_events = find_sets(df)
#preprocessing
df, one_loops = preprocess_for_one_loops(df)

causality, parallel, non_related = create_footprint_matrix(df)
sets = find_possible_sets(causality, parallel)
final_set = insert_start_end(sets, start_events, end_events)
transitions = transitions(final_set)
print("BEFORE ONE LOOPS: ", transitions)
transitions = insert_one_loops_finally(transitions, one_loops)
print("AFTER ONE LOOPS: ", transitions)
activities = activities(all_events)
write_to_csv(transitions, activities, 'test', cur_dir_path)


#insert_start_end(sets, ['a', 'b'], ['e', 'd'])
#example1 - easy with one one-loop