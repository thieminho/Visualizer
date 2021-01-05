from datetime import datetime

import pandas as pd
import os
from json import loads, dumps
from itertools import product


    # TODO: Preprocessing logs to the form of case_id, act_name?
import xmltodict
from PyQt5.QtWidgets import QVBoxLayout


class Plugin:
    def __init__(self):
        print('Plugin init ("Alpha Plus"):')


    def fill_my_parameters(self, widget: QVBoxLayout):
        pass

    def execute(self, *args, **kwargs):
        if args[0].endswith(".csv"):
            self.df = self.read_csv_into_df(args[0])
        elif args[0].endswith(".xes"):
            logfile = self.open_log_and_parse(args[0])
            traces = self.parse_log(logfile)
            self.df = self.create_dataframe_from_parsed_log(traces)
        # JCHALASIAK
        # self.df = self.read_csv_into_df(args[0])
        #JCHALASIAK
        cur_dir_path = os.path.dirname(os.path.realpath(__file__))
        all_events, start_events, end_events = self.find_sets(self.df)
        # preprocessing
        df, one_loops = self.preprocess_for_one_loops(self.df)
        causality, parallel, non_related = self.create_footprint_matrix(df)
        sets = self.find_possible_sets(causality, parallel)
        final_set = self.insert_start_end(sets, start_events, end_events)
        transitions = self.transitions(final_set)
        # print("BEFORE ONE LOOPS: ", transitions)
        transitions = self.insert_one_loops_finally(transitions, one_loops)
        # print("AFTER ONE LOOPS: ", transitions)
        activities = self.activities(all_events, start_events, end_events)
        full_path = self.write_to_csv(transitions, activities, 'transition_result', cur_dir_path)
        return "success", full_path

    def parse_log(self, log):
        data_types = ['string', 0, 'date', 0.0, 'boolean', 'id']
        log = xmltodict.parse(log)
        log = loads(dumps(log))
        traces = []
        for trace in log['log']['trace']:
            attributes = list(trace.keys())
            attributes_dictionary = {}
            for data_type in data_types:
                if data_type in attributes:
                    if type(trace[data_type]) == list:
                        for dictionary in trace[data_type]:
                            attributes_dictionary[dictionary['@key']] = dictionary['@value']
                    else:
                        attributes_dictionary[trace[data_type]['@key']] = trace[data_type]['@value']

            trace_events = []
            if type(trace['event']) == dict:
                trace['event'] = [trace['event']]

            for event in trace['event']:
                event_attributes = list(event.keys())
                event_dict = {}
                for data_type in data_types:
                    if data_type in event_attributes:
                        if type(event[data_type]) == list:
                            for dictionary in event[data_type]:
                                event_dict[dictionary['@key']] = dictionary['@value']
                        else:
                            event_dict[event[data_type]['@key']] = event[data_type]['@value']
                event_dict['concept:name'] = event_dict['concept:name']

                trace_events.append(event_dict)
            traces.append(trace_events)
        # for trace in traces:
        #     print(trace)
        return traces

    def create_dataframe_from_parsed_log(self, traces):
        df = pd.DataFrame({'case_id': [], 'act_name': []})
        for trace in traces:
            for event in trace:
                df = df.append({'case_id': str(traces.index(trace)), 'act_name': event['concept:name']},
                               ignore_index=True)
        print(df)
        return df

    def open_log_and_parse(self, file_name):
        with open(file_name, 'r') as log_file:
            logfile = log_file.read()
        return logfile


    def read_csv_into_df(self, file_name):
        df = pd.read_csv(file_name)
        #print(df)
        return df


    def find_sets(self, dataframe):
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


    def preprocess_for_one_loops(self, dataframe):
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


    def insert_one_loops_finally(self, transitions, one_loops):
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


    def create_footprint_matrix(self, dataframe):
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


    def find_more_sets(self, sets, non_related):
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


    def check_is_unrelated(self, parallel_relation, causal_relation, item_set_1, item_set_2):
        S = set(product(item_set_1, item_set_2)).union(set(product(item_set_2, item_set_1)))
        for pair in S:
            if pair in parallel_relation or pair in causal_relation:
                return True
        return False


    def pair_maximizer(self, alpha_pairs, pair):
        for alt in alpha_pairs:
            if pair != alt and pair[0].issubset(alt[0]) and pair[1].issubset(alt[1]):
                return False
        return True


    def find_more_sets_new(self, pairs, causals, parallels):
        for i in range(0, len(pairs)):
            t1 = pairs[i]
            for j in range(i, len(pairs)):
                t2 = pairs[j]
                if t1 != t2:
                    if t1[0].issubset(t2[0]) or t1[1].issubset(t2[1]):
                        if not (self.check_is_unrelated(parallels, causals,
                                                        t1[0], t2[0]) or self.check_is_unrelated(parallels, causals, t1[1], t2[1])):
                            new_alpha_pair = (t1[0] | t2[0], t1[1] | t2[1])
                            if new_alpha_pair not in pairs:
                                pairs.append((t1[0] | t2[0], t1[1] | t2[1]))
        internal_places = filter(lambda p: self.pair_maximizer(pairs, p), pairs)
        #print(internal_places)
        final = []
        for pair in internal_places:
            final.append(tuple(pair))
        return final


    def initial_filter(self, parallel_relation, pair):
        if (pair[0], pair[0]) in parallel_relation or (pair[1], pair[1]) in parallel_relation:
            return False
        return True


    def find_possible_sets(self, causals_set, non_related_set):
        pairs = list(map(lambda p: ({p[0]}, {p[1]}),
                         filter(lambda p: self.initial_filter(non_related_set, p),
                                causals_set)))
        yl = self.find_more_sets_new(pairs, causals_set, non_related_set)
        #print(yl)
        return yl


    def insert_start_end(self, possible_sets, start, end):
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

    def transitions(self, set):
        transitions = []
        for i in range(len(set)):
            transitions.append([])
        for i in range(len(set)):
            if i == 0:
                transitions[i].append('p')
                transitions[i].append('p' + str(i))
                transitions[i].append('')
                transitions[i].append(set[i])
            elif i == len(set) - 1:
                transitions[i].append('p')
                transitions[i].append('p' + str(i))
                transitions[i].append(set[i])
                transitions[i].append('')
            else:
                transitions[i].append('p')
                transitions[i].append('p' + str(i))
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
        return transitions


    def activities(self, all_events, start_events, end_events):
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


    def write_to_csv(self, transitions, activities, name, path):
        dir_path = path.replace("\\", "/") + '/Results/Alpha_Plus/' + datetime.now().strftime(
            "%d_%m_%Y_%H_%M_%S") + "/"
        full_path = os.path.join(dir_path, f"{name}.csv")
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as file:
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
        return full_path


