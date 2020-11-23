import pandas as pd
import numpy as np
from collections import defaultdict

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
    print(all_events)
    print(start_events)
    print(end_events)
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
    print(foot_matrix)
    return all_events, foot_matrix


def create_footprint_matrix(dataframe):
    all_events = list(dataframe.act_name.unique())
    cases = dataframe.case_id.unique()
    causality = set()
    parallel = set()
    non_related = set()
    sequences = []
    for case in cases:
        df = dataframe[dataframe.case_id.eq(case)]
        task = list(df.act_name.unique())
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
    print(causality)
    print(parallel)
    print(non_related)
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
    print(xl)
    for x in xl:
        a = set(x[0])
        b = set(x[1])
        for y in xl:
            if a.issubset(y[0]) and b.issubset(y[1]):
                if x != y:
                    yl.discard(x)
                    break
    print(yl)
    return yl

df = read_csv_into_df('test_simple.csv')
find_sets(df)
causality, parallel, non_related = create_footprint_matrix(df)
find_possible_sets(causality, non_related)
