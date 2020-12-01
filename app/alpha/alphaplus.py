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
    old_case_id = ''
    old_act_name = ''
    for index, row in df.iterrows():
        if row['case_id'] != old_case_id:
            start_events.append(row['act_name'])
            if old_case_id != '':
                end_events.append(old_act_name)
        old_case_id = row['case_id']
        old_act_name = row['act_name']
    start_set = set(start_events)
    end_set = set(end_events)
    start_events = list(start_set)
    end_events = list(end_set)
    #print(all_events)
    #print(start_events)
    #print(end_events)
    return all_events, start_events, end_events


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
    #print(causality)
    #print(parallel)
    #print(non_related)
    #print(trios)
    return causality, parallel, non_related


def find_possible_sets(causals_set, non_related_set):
    xl = causals_set.copy()
    for nr in non_related_set:
        for causals in causals_set:
            if (causals[0], nr[0]) in causals_set and (causals[0], nr[1]) in causals_set:
                xl.add((causals[0], nr))
            if (nr[0], causals[1]) in causals_set and (nr[1], causals[1]) in causals_set:
                xl.add((nr, causals[1]))
    yl = xl.copy()
    for x in xl:
        a = set(x[0])
        b = set(x[1])
        for y in xl:
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
    print(possible_sets)
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
    print(transitions)
    return transitions


def activities(all_events):
    activities = []
    for i in range(len(all_events)):
        activities.append([])
        activities[i].append('a')
        activities[i].append(all_events[i])
    print(activities)
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


df = read_csv_into_df('test_trios.csv')
all_events, start_events, end_events = find_sets(df)
causality, parallel, non_related = create_footprint_matrix(df)
sets = find_possible_sets(causality, non_related)
final_set = insert_start_end(sets, start_events, end_events)
transitions = transitions(final_set)
activities = activities(all_events)
write_to_csv(transitions, activities, 'test', cur_dir_path)


#insert_start_end(sets, ['a', 'b'], ['e', 'd'])