import os
from datetime import datetime

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QDialogButtonBox, QGridLayout, \
    QCheckBox, QSlider, QScrollArea, QWidget, QSizePolicy, QPushButton, QButtonGroup, QHBoxLayout


class Plugin:
    def __init__(self, *args, **kwargs):
        print('Plugin init ("Heuristic Miner"):', args, kwargs)
        # PARAM BEGIN
        self.dependency_threshold = None  # 0.9 (0;1)
        self.positive_observations_threshold = None  # 1 (int >=1)
        self.relative_to_best_threshold = None  # 0.05 (0;1)
        self.len1_loop_threshold = None  # 0.9 (0;1)
        self.len2_loop_threshold = None  # 0.9 (0;1)
        self.long_distance_threshold = None  # 0.9 (0;1)
        self.AND_threshold = None  # 0.1 (0;1)
        # PARAM END

        self.initial_activity = None
        self.end_activity = None
        self.hasParameters = True
        self.myDialog = self.CustomDialog()

    class CustomDialog(QDialog):
        def __init__(self, *args, **kwargs):
            """ TODO: add all metrics and parameters, then merge it into fill_my_params function to set all parameters """
            super(Plugin.CustomDialog, self).__init__(*args, **kwargs)
            self.resize(300, 300)
            self.layout = QVBoxLayout()
            self.setWindowTitle("Parameters")
            self.acc_button = QPushButton('OK')
            self.acc_button.clicked.connect(self.close_window)
            self.buttonBox = QHBoxLayout()
            self.buttonBox.addWidget(self.acc_button)
            self.cancel = QPushButton('Cancel')
            self.buttonBox.addWidget(self.cancel)
            self.cancel.clicked.connect(self.close_)
            self.scrollArea = QScrollArea(self)
            self.scrollArea.setWidgetResizable(True)
            self.scrollAreaWidgetContents = QDialog()
            self.vlayout = QVBoxLayout(self.scrollAreaWidgetContents)
            self.vlayout.setSpacing(0)
            self.vlayout.setContentsMargins(0, 0, 0, 0)
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            self.layout.addWidget(self.scrollArea)
            self.layout.addLayout(self.buttonBox)
            self.setLayout(self.layout)

            self.dependency_threshold = self.Dependence("Dependency treshold")  # 0.9 (0;1)
            self.positive_observations_threshold = None  # 1 (int >=1) ????
            self.relative_to_best_threshold = self.Dependence('Relative to best threshold')  # 0.05 (0;1)
            self.len1_loop_threshold = self.Dependence('len1_loop_threshold')  # 0.9 (0;1)
            self.len2_loop_threshold = self.Dependence('len2_loop_threshold')  # 0.9 (0;1)
            self.long_distance_threshold = self.Dependence('long_distance_threshold')  # 0.9 (0;1)
            self.AND_threshold = self.Dependence('AND_threshold')  # 0.1 (0;1)
            self.vlayout.addWidget(self.dependency_threshold)
            self.vlayout.addWidget(self.relative_to_best_threshold)
            self.vlayout.addWidget(self.len1_loop_threshold)
            self.vlayout.addWidget(self.len2_loop_threshold)
            self.vlayout.addWidget(self.long_distance_threshold)
            self.vlayout.addWidget(self.AND_threshold)

        def close_window(self):
            with open('param_file_hm.txt', 'w') as file:
                list_to_send = [self.dependency_threshold.slider.value() / 100,
                                self.relative_to_best_threshold.slider.value() / 100,
                                self.len1_loop_threshold.slider.value() / 100,
                                self.len2_loop_threshold.slider.value() / 100,
                                self.long_distance_threshold.slider.value() / 100,
                                self.AND_threshold.slider.value() / 100]
                [file.write(str(param) + '\n') for param in list_to_send]
            self.close()

        def close_(self):
            self.close()

        class Dependence(QDialog):
            def __init__(self, name):
                super().__init__()
                grid = QGridLayout()
                self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
                grid.setSpacing(5)
                self.label = QLabel(name)
                self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                self.slider = QSlider(QtCore.Qt.Horizontal)
                self.slider.setRange(0, 100)
                self.slider.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
                self.acc_val = QLabel('0')
                self.acc_val.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                self.slider.valueChanged.connect(lambda val: self.acc_val.setText(str(val / 100)))
                grid.addWidget(self.label, 0, 0)
                grid.addWidget(self.acc_val, 0, 1)
                grid.addWidget(self.slider, 1, 0, 1, 2)
                self.setLayout(grid)

    def fill_my_parameters(self):
        with open('param_file_hm.txt', 'r') as file:
            params = file.read().split()
            [print(p) for p in params]
            self.dependency_threshold = float(params[0])
            self.relative_to_best_threshold = float(params[1])
            self.len1_loop_threshold = float(params[2])
            self.len2_loop_threshold = float(params[3])
            self.long_distance_threshold = float(params[4])
            self.AND_threshold = float(params[5])
        if os.path.exists('../param_file_hm.txt'):
            try:
                os.remove('../params_file_hm.txt')
            except OSError as e:
                print(f'Failed with: {e.strerror}')
        else:
            print('Did not find path')


    # Assumes fill_my_parameters was already called, if not add it in the first line
    def execute(self, *args, **kwargs):
        self.dependency_threshold = 0.9  # 0.9 (0;1]
        self.positive_observations_threshold = 1  # 1 (int >=1)
        self.relative_to_best_threshold = 0.05  # 0.05 (0;1]
        self.len1_loop_threshold = 0.9  # 0.9 (0;1]
        self.len2_loop_threshold = 0.9  # 0.9 (0;1]
        self.long_distance_threshold = 0.9  # 0.9 (0;1]
        self.AND_threshold = 0.1  # 0.1 (0;1)
        self.fill_my_parameters()
        print('===================\n')
        print(self.dependency_threshold, self.relative_to_best_threshold,
              self.len1_loop_threshold, self.len2_loop_threshold,
              self.long_distance_threshold, self.AND_threshold)
        print(args)
        self.fullpath = args[0]
        self.df = pd.read_csv(args[0])
        self.traces = self.get_traces()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = dir_path.replace("\\", "/") + '/Results/Heuristic_Miner/' + datetime.now().strftime(
            "%d_%m_%Y_%H_%M_%S") + "/"
        self.filename = self.fullpath.split('/')[-1]
        print(self.filename)
        self.out_name = self.filename[:-4] + '_HMresult'
        print(dir_path)
        self.full_path = os.path.join(dir_path, f"{self.out_name}.csv")
        print(self.full_path)
        os.makedirs(os.path.dirname(self.full_path), exist_ok=True)

        # parameters for now
        # self.fill_my_parameters(None)
        print(f'Executing algorithm with fullpath:{self.fullpath}')
        self.fullpath = args[0]
        self.df = pd.read_csv(args[0])
        traces = self.get_traces()
        events = self.all_events()
        followage_occurrences = self.cal_foll_occ(traces, events)
        followage_occurrences_len2 = self.cal_foll_occ_len2(traces, events)
        print(followage_occurrences)
        dependency_matrix = self.cal_depend_matrix(followage_occurrences, events)
        len1_loops = self.cal_len1_loops(dependency_matrix)
        len2_loop_matrix = self.cal_len2_loop_matrix(followage_occurrences_len2, len1_loops, events)
        len2_loops = self.cal_len2_loops(len2_loop_matrix)
        print(dependency_matrix)
        dependency_graph = self.connect_loops_in_dependancy_graph(len1_loops, len2_loops, events)
        dependency_graph = self.all_activities_connected_heuristic(dependency_matrix, len2_loops,
                                                                   events, dependency_graph)
        dependency_graph = self.add_connections_from_meta_parameters(followage_occurrences, dependency_matrix,
                                                                     dependency_graph, events)
        print(dependency_graph)
        causal_matrix = self.construct_causal_matrix(dependency_graph, followage_occurrences)
        print(causal_matrix)

        #long distance dependance
        followage_occurrences_long = self.cal_foll_occ_long(traces, events)
        frequencies = self.cal_frequencies(traces)
        dependency_graph = self.long_ditance_depend(events, frequencies, followage_occurrences_long,
                                                    causal_matrix, dependency_graph)
        causal_matrix = self.construct_causal_matrix(dependency_graph, followage_occurrences)

        # So called "more sophisticated mapping", only works for work-flow nets from [7]
        petri_net = self.causal_matrix_to_petri_net(causal_matrix, events)
        print(petri_net)
        file_name = self.petri_net_to_csv(petri_net)

        # causal_matrix = self.long_distance(...)
        # petri_net_in_csv = self.to_petri_net(causal_matrix)
        # with open(full_path, 'w') etc.
        return "success", self.full_path

    # assumes simple .csv [case_id, act_name], at most I can add using time to determine order
    def get_traces(self):
        return self.df.groupby('case_id')['act_name'].apply(list)

    def all_events(self):
        return self.df.act_name.unique()

    def dependency(self, a_into_b, b_into_a):
        return (a_into_b - b_into_a) / (a_into_b + b_into_a + 1)

    def dependency_loop_len1(self, a_into_a):
        return a_into_a / (a_into_a + 1)

    def dependency_loop_len2(self, a_into_b, b_into_a):
        return (a_into_b + b_into_a) / (a_into_b + b_into_a + 1)

    def cal_foll_occ(self, traces, events):
        occ_matrix = {}
        for event_a in events:
            occ_matrix[event_a] = {}
            for event_b in events:
                occ_matrix[event_a][event_b] = 0.0
        for trace in traces:
            for prev_index, activity in enumerate(trace[1:]):
                occ_matrix[trace[prev_index]][activity] += 1
        return occ_matrix

    def cal_foll_occ_len2(self, traces, events):
        occ_matrix = {}
        for event_a in events:
            occ_matrix[event_a] = {}
            for event_b in events:
                occ_matrix[event_a][event_b] = 0
        for trace in traces:
            for index, activity in enumerate(trace[2:], start=2):
                if trace[index - 2] == activity:
                    occ_matrix[activity][trace[index - 1]] += 1
        return occ_matrix

    def cal_foll_occ_long(self, traces, events):
        occ_matrix = {}
        for event_a in events:
            occ_matrix[event_a] = {}
            for event_b in events:
                occ_matrix[event_a][event_b] = 0

        for trace in traces:
            for offset in range(1, len(trace)-1, 1):
                for index, activity in enumerate(trace[offset:], start=offset):
                    if trace[index - offset] == activity:
                        occ_matrix[activity][trace[index - 1]] += 1
        return occ_matrix

    def cal_depend_matrix(self, foll_occs, events):
        depend_matrix = {}
        for event_a in events:
            depend_matrix[event_a] = {}
            for event_b in events:
                if event_a == event_b:
                    depend_matrix[event_a][event_b] = self.dependency_loop_len1(foll_occs[event_a][event_b])
                else:
                    depend_matrix[event_a][event_b] = self.dependency(foll_occs[event_a][event_b],
                                                                      foll_occs[event_b][event_a])
        return depend_matrix

    def cal_len2_loop_matrix(self, foll_occs_len2, len1_loops, events):
        depend_matrix = {}
        for event_a in events:
            depend_matrix[event_a] = {}
            for event_b in events:
                if (event_a == event_b) or event_a in len1_loops or event_b in len1_loops:
                    depend_matrix[event_a][event_b] = 0
                else:
                    depend_matrix[event_a][event_b] = self.dependency_loop_len2(foll_occs_len2[event_a][event_b],
                                                                                foll_occs_len2[event_b][event_a])
        return depend_matrix

    def cal_len1_loops(self, dependency_matrix):
        loops = []
        for event in dependency_matrix.keys():
            if dependency_matrix[event][event] > self.len1_loop_threshold:
                loops.append(event)
        return loops

    def cal_len2_loops(self, len2_loop_matrix):
        loops = []
        for event_a, dependencies in len2_loop_matrix.items():
            for event_b in dependencies.keys():
                if len2_loop_matrix[event_a][event_b] > self.len2_loop_threshold:
                    loops.append((event_a, event_b))
        return loops

    def connect_loops_in_dependancy_graph(self, loops1, loops2, events):
        depend_graph = {}
        for event in events:
            depend_graph.setdefault(event, set())
        for event in loops1:
            depend_graph[event].add(event)
        for event_a, event_b in loops2:
            depend_graph[event_a].add(event_b)
            # not actually necessary to do both since they repeat in loops2 array
            depend_graph[event_b].add(event_a)
        return depend_graph

    def all_activities_connected_heuristic(self, depend_matrix, loops2, events, depend_graph):

        initial_activity = self.find_inital_activity(depend_matrix)
        self.initial_activity = initial_activity
        end_activity = self.find_end_activity(depend_matrix)
        self.end_activity = end_activity
        depend_graph[end_activity] = set()
        for event in events:
            if initial_activity in depend_graph[event]:
                depend_graph[event].remove(initial_activity)
        for event in events:
            if event != end_activity and not (event, end_activity) in loops2:
                if self.in_2loop(event, loops2):
                    s = self.find_best_successor_for2loop(event, depend_matrix, loops2)
                    depend_graph[event].add(s)
                else:
                    s = self.find_best_successor(event, depend_matrix)
                    depend_graph[event].add(s)
            if event != initial_activity and not (event, initial_activity) in loops2:
                if self.in_2loop(event, loops2):
                    s = self.find_best_predecessor_for2loop(event, depend_matrix, loops2)
                    depend_graph[s].add(event)
                else:
                    s = self.find_best_predecessor(event, depend_matrix)
                    depend_graph[s].add(event)
        depend_graph[end_activity] = set()
        for event in events:
            if initial_activity in depend_graph[event]:
                depend_graph[event].remove(initial_activity)
        return depend_graph

    def find_inital_activity(self, depend_matrix):
        maxs = [(-2, key) for key in depend_matrix.keys()]
        for dependencies in depend_matrix.values():
            for index, (event_b, dependency) in enumerate(dependencies.items()):
                if maxs[index][0] < dependency:
                    maxs[index] = (dependency, event_b)
        min_max = min([i[0] for i in maxs])
        for m in maxs:
            if m[0] == min_max:
                initial = m[1]
                break
        # noinspection PyUnboundLocalVariable
        return initial

    def find_end_activity(self, depend_matrix):
        mins = [(2, key) for key in depend_matrix.keys()]
        for dependencies in depend_matrix.values():
            for index, (event_b, dependency) in enumerate(dependencies.items()):
                if mins[index][0] > dependency:
                    mins[index] = (dependency, event_b)
        max_min = max([i[0] for i in mins])
        for m in mins:
            if m[0] == max_min:
                end = m[1]
                break
        # noinspection PyUnboundLocalVariable
        return end

    def in_2loop(self, event, loops2):
        for _, event_a in loops2:
            if event == event_a:
                return True
        return False

    def find_best_successor(self, event, depend_matrix):
        maximium = -2
        for event_a, dependency_value in depend_matrix[event].items():
            if event_a == event or event_a == self.initial_activity:
                continue
            if maximium < dependency_value:
                maximium = dependency_value
                successor = event_a
        # noinspection PyUnboundLocalVariable
        return successor

    def find_best_successor_for2loop(self, event_a, depend_matrix, loops2):
        maximium = -2
        event_b = None
        for event_1, event_2 in loops2:
            if event_1 == event_a:
                event_b = event_2
        for event, dependency_value_a, _, dependency_value_b \
                in zip(depend_matrix[event_a].items(), depend_matrix[event_b].items()):
            if event_a == event or event_b == event or event == self.initial_activity:
                continue
            dependency_value = (dependency_value_a + dependency_value_b) / 2
            if maximium < dependency_value:
                maximium = dependency_value
                successor = event
        # noinspection PyUnboundLocalVariable
        return successor

    def find_best_predecessor(self, event, depend_matrix):
        maximum = -2
        for event_a, dependecies in depend_matrix.items():
            dependency_value = dependecies[event]
            if event_a == event or event_a == self.end_activity:
                continue
            if maximum < dependency_value:
                maximum = dependency_value
                predecessor = event_a
        # noinspection PyUnboundLocalVariable
        return predecessor

    def find_best_predecessor_for2loop(self, event_a, depend_matrix, loops2):
        maximum = -2
        event_b = None
        for event_1, event_2 in loops2:
            if event_1 == event_a:
                event_b = event_2
        for event, dependecies in depend_matrix.items():
            if event_a == event or event_b == event or event == self.end_activity:
                continue
            dependency_value = (dependecies[event_a] + dependecies[event_b]) / 2
            if maximum < dependency_value:
                maximum = dependency_value
                predecessor = event
        # noinspection PyUnboundLocalVariable
        return predecessor

    def add_connections_from_meta_parameters(self, followage_occurrences, dependency_matrix, dependency_graph, events):
        for event_a in events:
            if event_a == self.end_activity:
                continue
            for event_b in events:
                if event_b == self.initial_activity:
                    continue
                positive_observations = followage_occurrences[event_a][event_b] > self.positive_observations_threshold
                dependency = dependency_matrix[event_a][event_b] > self.dependency_threshold
                s = self.find_best_successor(event_a, dependency_matrix)
                relative_to_best = dependency_matrix[event_a][s] - dependency_matrix[event_a][event_b]
                relative_to_best = relative_to_best > self.relative_to_best_threshold
                if positive_observations and dependency and relative_to_best:
                    dependency_graph[event_a].add(event_b)
        return dependency_graph

    def construct_causal_matrix(self, dependency_graph, follow_occs):
        causal_matrix = {}
        for event, successors in dependency_graph.items():
            causal_matrix.setdefault(event, {'input': [], 'output': []})
            for successor in successors:
                causal_matrix[event]['output'].append([successor])
                causal_matrix.setdefault(successor, {'input': [], 'output': []})
                causal_matrix[successor]['input'].append([event])
        for event, dictionary in causal_matrix.items():
            if len(dictionary['input']) > 1:
                base = list([list(x) for x in dictionary['output']])
                expression = [dictionary['input'][0]]
                for [event_a] in dictionary['input'][1:]:
                    xor_joined_flag = False
                    for index, xor_expression in enumerate(expression):
                        to_xor_join_flag = True
                        for event_b in list(xor_expression):
                            relation = self.cal_and_relation_predecessor(event, event_a, event_b, follow_occs)
                            if relation > self.AND_threshold:
                                to_xor_join_flag = False
                        if to_xor_join_flag:
                            xor_joined_flag = True
                            expression[index].append(event_a)
                    if not xor_joined_flag:
                        expression.append([event_a])
                for index, xor_expression in enumerate(expression):
                    to_xor_join_flag = True
                    for [event_b] in base:
                        if event_b in xor_expression:
                            continue
                        for event_a in list(xor_expression):
                            relation = self.cal_and_relation_predecessor(event, event_a, event_b, follow_occs)
                            if relation > self.AND_threshold:
                                to_xor_join_flag = False
                        if to_xor_join_flag:
                            expression[index].append(event_b)
                causal_matrix[event]['input'] = expression

            if len(dictionary['output']) > 1:
                base = list([list(x) for x in dictionary['output']])
                expression = [dictionary['output'][0]]
                for [event_a] in dictionary['output'][1:]:
                    xor_joined_flag = False
                    for index, xor_expression in enumerate(expression):
                        to_xor_join_flag = True
                        for event_b in list(xor_expression):
                            relation = self.cal_and_relation_successor(event, event_a, event_b, follow_occs)
                            if relation > self.AND_threshold:
                                to_xor_join_flag = False
                        if to_xor_join_flag:
                            xor_joined_flag = True
                            expression[index].append(event_a)
                    if not xor_joined_flag:
                        expression.append([event_a])
                for index, xor_expression in enumerate(expression):
                    to_xor_join_flag = True
                    for [event_b] in base:
                        if event_b in xor_expression:
                            continue
                        for event_a in list(xor_expression):
                            relation = self.cal_and_relation_successor(event, event_a, event_b, follow_occs)
                            if relation > self.AND_threshold:
                                to_xor_join_flag = False
                        if to_xor_join_flag:
                            expression[index].append(event_b)
                causal_matrix[event]['output'] = expression
        return causal_matrix

    def cal_and_relation_successor(self, event_a, event_b, event_c, follow_occs):
        return (follow_occs[event_b][event_c] + follow_occs[event_c][event_b]) / \
               (follow_occs[event_a][event_b] + follow_occs[event_a][event_c] + 1)

    def cal_and_relation_predecessor(self, event_a, event_b, event_c, follow_occs):
        return (follow_occs[event_b][event_c] + follow_occs[event_c][event_b]) / \
               (follow_occs[event_b][event_a] + follow_occs[event_c][event_a] + 1)

    def cal_frequencies(self, traces):
        frequencies = {}
        for trace in traces:
            for event in trace:
                frequencies.setdefault(event, 0)
                frequencies[event] += 1
        return frequencies

    def long_ditance_depend(self, events, frequencies, foll_occs_long, causal_matrix, dependency_graph):
        for event_a in events:
            for event_b in events:
                a_b = foll_occs_long[event_a][event_b]
                a = frequencies[event_a]
                long_distance_dependency = (a_b/a+1) - (a_b/a)
                observations = a_b >= self.positive_observations_threshold
                threshold = long_distance_dependency >= self.long_distance_threshold
                if observations and threshold:
                    if self.escape_to_end_possible(event_a, event_b, set(), events, causal_matrix):
                        dependency_graph[event_a].add(event_b)
        return dependency_graph

    def escape_to_end_possible(self, event_x, event_y, visited_s, events, causal_matrix):
        if (event_x in visited_s) or (event_x == event_y) or (event_y == self.end_activity):
            return False
        if event_x == self.end_activity:
            return True
        for ors_i in causal_matrix:
            or_set_escape_possible = False
            for e_j in events:
                if e_j in ors_i:
                    visited_s.add(event_x)
                    if self.escape_to_end_possible(e_j, event_y, visited_s, events, causal_matrix):
                        or_set_escape_possible = True
                    visited_s.remove(event_x)
            if not or_set_escape_possible:
                return False
        return True
    def causal_matrix_to_petri_net(self, causal_matrix, events):
        X = set()
        for name, event in causal_matrix.items():
            for name_b, event_b in causal_matrix.items():
                for xors_i in event['input']:
                    for xors_o in event_b['output']:
                        if name in xors_o and name_b in xors_i:
                            X.add((tuple(xors_i), tuple(xors_o)))
        places = set(X)
        places.add("start_place")
        places.add("end_place")
        transitions = set(events)
        arcs = set()
        for event in events:
            if len(causal_matrix[event]['input']) == 0:
                arcs.add(("start_place", event))
            if len(causal_matrix[event]['output']) == 0:
                arcs.add((event, "end_place"))
            for input_output_pair in X:
                if event in input_output_pair[1]:
                    arcs.add((input_output_pair, event))
                if event in input_output_pair[0]:
                    arcs.add((event, input_output_pair))
        petri_net = (places, transitions, arcs)
        print(places)
        print(transitions)
        print(arcs)
        return petri_net

    def petri_net_to_csv(self, petri_net):
        with open(self.full_path, 'w') as result:
            result.write('type;id;from;to\n')
            for place in petri_net[0]:
                result.write(f'p;{place};;\n')
            for transition in petri_net[1]:
                result.write(f't;{transition};;\n')
            for edge in petri_net[2]:
                result.write(f'e;{edge};{edge[0]};{edge[1]}\n')
        pass
