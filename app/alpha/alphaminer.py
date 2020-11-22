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


def create_footprint_matrix(dataframe):
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


def find_possible_sets(all_events, footprint_matrix):
    possible_sets = []
    possible_sets_dict = defaultdict(list)
    for i in range(len(footprint_matrix)):
        for j in range(len(footprint_matrix)):
            if footprint_matrix[i, j] == '>':
                possible_sets.append([all_events[i], all_events[j]])
                possible_sets_dict[all_events[i]].append(all_events[j])
    print(possible_sets)
    print(possible_sets_dict)
    return possible_sets


df = read_csv_into_df('test_simple.csv')
find_sets(df)
events, matrix = create_footprint_matrix(df)
find_possible_sets(events, matrix)
