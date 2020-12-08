import pandas as pd
import numpy as np
import os
cur_dir_path = os.path.dirname(os.path.realpath(__file__))
from itertools import product


def read_csv_into_df(file_name):
    df = pd.read_csv(file_name)
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


def create_visual_footprint_matrix(dataframe):
    all_events = list(dataframe.act_name.unique())
    all_events.sort()
    cases = dataframe.case_id.unique()
    foot_matrix = np.full((len(all_events), len(all_events)), '0')
    foot_matrix[:] = '0'
    for case in cases:
        df = dataframe[dataframe.case_id.eq(case)]
        last_act_name = ''
        for index, row in df.iterrows():
            if last_act_name != '':
                if foot_matrix[int(all_events.index(row['act_name'])), int(all_events.index(last_act_name))] == '0':
                    foot_matrix[int(all_events.index(last_act_name)), int(all_events.index(row['act_name']))] = '>'
                    foot_matrix[int(all_events.index(row['act_name'])), int(all_events.index(last_act_name))] = '<'
                elif foot_matrix[int(all_events.index(row['act_name'])), int(all_events.index(last_act_name))] != '0':
                    if foot_matrix[int(all_events.index(row['act_name'])), int(all_events.index(last_act_name))] == '<':
                        pass
                    elif foot_matrix[int(all_events.index(row['act_name'])), int(all_events.index(last_act_name))] == '>':
                        foot_matrix[int(all_events.index(row['act_name'])), int(all_events.index(last_act_name))] = '|'
                        foot_matrix[int(all_events.index(last_act_name)), int(all_events.index(row['act_name']))] = '|'
            last_act_name = row['act_name']
    foot_matrix[foot_matrix == '0'] = '#'
    return all_events, foot_matrix


def check_is_unrelated(parallel_relation, causal_relation, item_set_1, item_set_2):
    S = set(product(item_set_1, item_set_2)).union(set(product(item_set_2, item_set_1)))
    for pair in S:
        if pair in parallel_relation or pair in causal_relation:
            return True
    return False


def pair_maximizer(alpha_pairs, pair):
    for alt in alpha_pairs:
        if pair != alt and pair[0].issubset(alt[0]) and pair[1].issubset(alt[1]):
            return False
    return True


def find_more_sets_new(pairs, causals, parallels):
    for i in range(0, len(pairs)):
        t1 = pairs[i]
        for j in range(i, len(pairs)):
            t2 = pairs[j]
            if t1 != t2:
                if t1[0].issubset(t2[0]) or t1[1].issubset(t2[1]):
                    if not (check_is_unrelated(parallels, causals,
                                                 t1[0], t2[0]) or check_is_unrelated(parallels, causals, t1[1], t2[1])):
                        new_alpha_pair = (t1[0] | t2[0], t1[1] | t2[1])
                        if new_alpha_pair not in pairs:
                            pairs.append((t1[0] | t2[0], t1[1] | t2[1]))
    internal_places = filter(lambda p: pair_maximizer(pairs, p), pairs)
    #print(internal_places)
    final = []
    for pair in internal_places:
        final.append(tuple(pair))
    return final


def initial_filter(parallel_relation, pair):
    if (pair[0], pair[0]) in parallel_relation or (pair[1], pair[1]) in parallel_relation:
        return False
    return True


def create_footprint_matrix(dataframe):
    all_events = list(dataframe.act_name.unique())
    cases = dataframe.case_id.unique()
    causality = set()
    parallel = set()
    non_related = set()
    sequences = []
    for case in cases:
        df = dataframe[dataframe.case_id.eq(case)]
        task = list(df.act_name)
        for i in range(0, len(task) - 1):
            sequences.append((task[i], task[i + 1]))
        for activity in all_events:
            for second_activity in task:
                if (activity, second_activity) not in non_related and (second_activity, activity) not in non_related:
                    if (activity, second_activity) not in sequences and (second_activity, activity) not in sequences:
                        non_related.add((activity, second_activity))
    for sequence in sequences:
        if (sequence[0], sequence[1]) in sequences and (sequence[1], sequence[0]) not in sequences:
            causality.add(sequence)
        if (sequence[0], sequence[1]) in sequences and (sequence[1], sequence[0]) in sequences:
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
    pairs = list(map(lambda p: ({p[0]}, {p[1]}),
                     filter(lambda p: initial_filter(non_related_set, p),
                            causals_set)))
    yl = find_more_sets_new(pairs, causals_set, non_related_set)
    #print(yl)
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
            continue
            # transitions[i].append('t')
            # transitions[i].append('t'+str(i))
            # transitions[i].append('')
            # transitions[i].append(set[i])
        elif i == len(set) - 1:
            continue
            # transitions[i].append('t')
            # transitions[i].append('t' + str(i))
            # transitions[i].append(set[i])
            # transitions[i].append('')
        else:
            transitions[i].append('t')
            transitions[i].append('t' + str(i))
            temp = list(set[i])
            for j in range(len(temp)):
                string = ''
                if isinstance(temp[j], object) and temp[j] != 'START' and temp[j] != 'END':
                    list_of_strings = [str(s) for s in temp[j]]
                    string = ";".join(list_of_strings)
                elif isinstance(temp[j], str):
                    string = temp[j]
                if j == 0:
                    transitions[i].append(string)
                elif j == 1:
                    transitions[i].append(string)
    transitions.pop(0)
    transitions.pop(len(transitions)-1)
    return transitions


def activities(all_events, start_events, end_events):
    activities = []
    for i in range(len(all_events)):
        activities.append([])
        activities[i].append('n')
        activities[i].append(all_events[i])
    if len(start_events) > 1:
        activities.append(['n', 'START'])
    if len(end_events) > 1:
        activities.append(['n', 'END'])
    return activities


def write_to_csv(transitions, activities, name, path):
    print(transitions)
    dir_path = path
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


df = read_csv_into_df('tests/ex5-ap/example5.csv')
all_events, start_events, end_events = find_sets(df)
causality, parallel, non_related = create_footprint_matrix(df)
sets = find_possible_sets(causality, parallel)
final_set = insert_start_end(sets, start_events, end_events)
transitions = transitions(final_set)
activities = activities(all_events, start_events, end_events)
write_to_csv(transitions, activities, 'transition_result', cur_dir_path)
