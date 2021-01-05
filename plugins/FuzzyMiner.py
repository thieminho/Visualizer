import copy
import os
import sys
from datetime import datetime
from json import loads, dumps

import numpy as np
import xmltodict
from PyQt5.QtWidgets import QVBoxLayout


class Plugin:

    def __init__(self, *args, **kwargs):
        print('Plugin init ("Fuzzy Miner")')


    def fill_my_parameters(self, widget: QVBoxLayout):
        # vBox = QVBoxLayout()
        # hBox = QHBoxLayout()
        # first_label = QLabel('name')
        # vBox.addLayout(hBox, 0)
        # hBox.addWidget(first_label)
        # inverted = QCheckBox('Inverted', hBox)
        # hBox.addWidget(inverted)
        # active = QCheckBox('Active', hBox)
        # hBox.addWidget(active)
        # vBox.addLayout(hBox)
        # slider = QSlider(Qt.Horizontal)
        # slider.setRange(0, 1)
        # vBox.addWidget(slider)
        # # self.proximity_correlation_binary = self.add_metric( 'proximity_correlation_binary')
        # widget.addWidget(vBox)
        # self.endpoint_correlation_binary = self.add_metric( 'endpoint_correlation_binary')
        # widget.addLayout(self.endpoint_correlation_binary)
        pass



    def execute(self, *args, **kwargs):
        print(f'Executing algorithm with fullpath:{self.fullpath}')
        self.fullpath = args[0]
        with open(self.fullpath, 'r') as log_file:
            log = log_file.read()
        fm = FuzzyMiner()
        fm.___init___(log, self.fullpath)
        self.config = Configuration(FilterConfig(node_filter=NodeFilter(),
                                            edge_filter=EdgeFilter(),
                                            concurrency_filter=ConcurrencyFilter()),
                               [MetricConfig(name='proximity_correlation_binary',
                                             metric_type='binary'),
                                MetricConfig(name='endpoint_correlation_binary',
                                             metric_type='binary'),
                                MetricConfig(name='originator_correlation_binary',
                                             metric_type='binary'),
                                MetricConfig(name='datatype_correlation_binary',
                                             metric_type='binary'),
                                MetricConfig(name='datavalue_correlation_binary',
                                             metric_type='binary'),
                                MetricConfig(name='routing_significance_unary',
                                             metric_type='unary'),
                                MetricConfig(name='distance_significance_binary',
                                             metric_type='binary'),
                                MetricConfig(name='frequency_significance_unary',
                                             metric_type='unary'),
                                MetricConfig(name='frequency_significance_binary',
                                             metric_type='binary'),
                                ],
                               NRootAttenuation(buffer_size=5, num_of_echelons=2.7),
                               maximal_distance=5)

        fm.apply_config(self.config)
        return "success", fm.full_path

class FuzzyMiner:
    def ___init___(self, log, path):
        self.name = path[-1]
        self.path = path
        self.log = self.parse_log(log)
        self.nodes = None
        self.clusters = None
        self.edges = None
        self.node_indices = None
        self.num_of_nodes = None
        self.fm_message = ''
        self.extract_node_info()
        self.metric_settings = None
        self.unary_node_frequency_values = None
        self.unary_node_frequency_normalized_values = None
        self.binary_edge_frequency_values = None
        self.binary_edge_frequency_normalized_values = None

        self.binary_corr_divisors = None
        self.unary_simple_aggregate_normalized_values = None
        self.binary_simple_aggregate_normalized_values = None
        self.binary_multi_aggregate_normalized_values = None

        self.binary_corr_proximity_values = None
        self.binary_corr_proximity_normalized_values = None
        self.binary_corr_endpoint_values = None
        self.binary_corr_endpoint_normalized_values = None
        self.binary_corr_originator_values = None
        self.binary_corr_originator_normalized_values = None
        self.binary_corr_datatype_values = None
        self.binary_corr_datatype_normalized_values = None
        self.binary_corr_datavalue_values = None
        self.binary_corr_datavalue_normalized_values = None

        self.unary_derivative_routing_values = None
        self.unary_derivative_routing_normalized_values = None
        self.binary_derivative_distance_values = None
        self.binary_derivative_distance_normalized_values = None

        self.unary_weighted_values = None
        self.binary_sig_weighted_values = None
        self.binary_corr_weighted_values = None

        # Clustering
        self.node_cluster_mapping = list()
        self.cluster_dict = dict()
        self.fm_edges_dict = dict()
        self.fm_clusters = list()
        self.fm_edges = list()
        self.fm_nodes = list()

    def init_lists(self):
        s = self.num_of_nodes
        self.unary_node_frequency_values = [0 for _ in range(s)]
        self.unary_node_frequency_normalized_values = [0.0 for _ in range(s)]
        self.binary_edge_frequency_values = [[0 for _ in range(s)] for _ in range(s)]
        self.binary_edge_frequency_normalized_values = [[0.0 for _ in range(s)] for _ in range(s)]

        self.binary_corr_divisors = [[0.0 for _ in range(s)] for _ in range(s)]
        self.unary_simple_aggregate_normalized_values = [0.0 for _ in range(s)]
        self.binary_simple_aggregate_normalized_values = [[0.0 for _ in range(s)] for _ in range(s)]
        self.binary_multi_aggregate_normalized_values = [[0.0 for _ in range(s)] for _ in range(s)]

        if self.metric_settings["proximity_correlation_binary"][0]:
            self.binary_corr_proximity_values = [[0.0 for _ in range(s)] for _ in range(s)]
            self.binary_corr_proximity_normalized_values = [[0.0 for _ in range(s)] for _ in range(s)]
        if self.metric_settings["endpoint_correlation_binary"][0]:
            self.binary_corr_endpoint_values = [[0.0 for _ in range(s)] for _ in range(s)]
            self.binary_corr_endpoint_normalized_values = [[0.0 for _ in range(s)] for _ in range(s)]
        if self.metric_settings["originator_correlation_binary"][0]:
            self.binary_corr_originator_values = [[0.0 for _ in range(s)] for _ in range(s)]
            self.binary_corr_originator_normalized_values = [[0.0 for _ in range(s)] for _ in range(s)]
        if self.metric_settings["datatype_correlation_binary"][0]:
            self.binary_corr_datatype_values = [[0.0 for _ in range(s)] for _ in range(s)]
            self.binary_corr_datatype_normalized_values = [[0.0 for _ in range(s)] for _ in range(s)]
        if self.metric_settings["datavalue_correlation_binary"][0]:
            self.binary_corr_datavalue_values = [[0 for _ in range(s)] for _ in range(s)]
            self.binary_corr_datavalue_normalized_values = [[0.0 for _ in range(s)] for _ in range(s)]

        if self.metric_settings["routing_significance_unary"][0]:
            self.unary_derivative_routing_values = [0 for _ in range(s)]
            self.unary_derivative_routing_normalized_values = [0 for _ in range(s)]
        if self.metric_settings["distance_significance_binary"][0]:
            self.binary_derivative_distance_values = [([0 for _ in range(s)]) for _ in range(s)]
            self.binary_derivative_distance_normalized_values = [[0.0 for _ in range(s)] for _ in range(s)]

        self.unary_weighted_values = [0 for _ in range(s)]
        self.binary_sig_weighted_values = [[0 for _ in range(s)] for _ in range(s)]
        self.binary_corr_weighted_values = [[0 for _ in range(s)] for _ in range(s)]

    def apply_config(self, config):
        self.config = config
        metric_configs = self.config.metric_configs
        self.metric_settings = dict()
        for conf in metric_configs:
            self.metric_settings[conf.name] = (conf.include, conf.invert, conf.weight)
        self.init_lists()
        self.extract_primary_metrics()
        self.normalize_primary_metrics()
        self.extract_aggregates()
        self.extract_derivative_metrics()
        self.normalize_derivative_metrics()
        self.extract_weighted_metrics()
        return self.apply_filters()

    def apply_filters(self):
        return self.apply_concurrency_filter(self.config.filter_config.concurrency_filter)

    def apply_concurrency_filter(self, concurrency_filter):
        self.config.filter_config.concurrency_filter = concurrency_filter
        self.apply_concurrency_filter_helper(concurrency_filter)
        return self.apply_edge_filter(self.config.filter_config.edge_filter)

    def apply_concurrency_filter_helper(self, concurrency_filter):
        self.config.filter_config.concurrency_filter = concurrency_filter
        self.concurrency_filter_resultant_binary_values = copy.deepcopy(self.binary_sig_weighted_values)
        self.concurrency_filter_resultant_binary_corr_values = copy.deepcopy(
            self.binary_corr_weighted_values)
        if self.config.filter_config.concurrency_filter.filter_concurrency:
            sz = self.num_of_nodes
            for i in range(0, sz):
                for j in range(0, i):
                    self.process_relation_pair(i, j)

    def apply_edge_filter(self, edge_filter):
        self.config.filter_config.edge_filter = edge_filter
        self.apply_edge_filter_helper(edge_filter)
        return self.apply_node_filter(self.config.filter_config.node_filter)

    def apply_edge_filter_helper(self, edge_filter):
        self.config.filter_config.edge_filter = edge_filter
        self.edge_filter_resultant_binary_values = copy.deepcopy(self.concurrency_filter_resultant_binary_values)
        self.edge_filter_resultant_binary_corr_values = copy.deepcopy(
            self.concurrency_filter_resultant_binary_corr_values)
        sz = self.num_of_nodes

        self.preserve_mask = [[False for x in range(sz)] for y in range(sz)]

        if self.config.filter_config.edge_filter.edge_transform == 1:

            if self.config.filter_config.edge_filter.preserve == 0.0:
                self.config.filter_config.edge_filter.preserve = 0.001

            for i in range(0, sz):
                self.process_node_edges_fuzzy_filter(i)
        else:
            for i in range(0, sz):
                self.process_node_edges_best_filter(i)
        for i in range(0, sz):
            for j in range(0, sz):
                if not self.preserve_mask[i][j]:
                    self.edge_filter_resultant_binary_values[i][j] = 0.0
                    self.edge_filter_resultant_binary_corr_values[i][j] = 0.0

    def apply_node_filter(self, node_filter):
        self.config.filter_config.node_filter = node_filter
        self.apply_node_filter_helper(node_filter)

        self.finalize_graph_data()
        # Vizualization here since we have all graph data
        # graph_path = self.visualize(self.fm_nodes, self.fm_edges, self.fm_clusters)
        # self.fm_message.graph_path = graph_path
        return self.fm_message

    def apply_node_filter_helper(self, node_filter):
        self.config.filter_config.node_filter = node_filter
        self.node_filter_resultant_unary_values = copy.deepcopy(self.unary_weighted_values)
        self.node_filter_resultant_binary_values = copy.deepcopy(self.edge_filter_resultant_binary_values)
        self.node_filter_resultant_binary_corr_values = copy.deepcopy(self.edge_filter_resultant_binary_corr_values)
        self.clusterize()

    def finalize_graph_data(self):
        self.fm_nodes = self.fm_nodes
        self.fm_edges = self.fm_edges
        self.fm_clusters = self.fm_clusters

        # Debug block starts
        print("Nodes\n")
        for node in self.fm_nodes:
            print(node)
            # print()
        print("\nClusters\n")
        for cluster in self.fm_clusters:
            print(cluster)
            # print()
        print("\nEdges\n")
        for edge in self.fm_edges:
            print(edge)
            # print()
        print(self.unary_node_frequency_normalized_values)
        print(self.binary_edge_frequency_values)
        print(self.binary_edge_frequency_normalized_values)
        print(self.binary_corr_endpoint_normalized_values)
        # Debug block ends
        print(self.path)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = dir_path.replace("\\", "/") + '/Results/Fuzzy_Miner/' + datetime.now().strftime(
            "%d_%m_%Y_%H_%M_%S") + "/"
        self.filename = self.path.split('/')[-1]
        print(self.filename)

        print(dir_path)
        self.full_path = os.path.join(dir_path, f"{self.filename}.csv")
        print(self.full_path)
        os.makedirs(os.path.dirname(self.full_path), exist_ok=True)
        with open(self.full_path, 'w') as result:
            result.write('type,id,significance,from,to\n')
            for node in self.fm_nodes:
                result.write(f'n,{node.label.split("@")[0]},{node.significance:.2f}\n')
            for cluster in self.fm_clusters:
                result.write(f'c,{cluster.label.split("@")[0]}_{cluster.index},{cluster.significance:.2f}\n')
            for i, edge in enumerate(self.fm_edges):
                s = next(x for x in self.fm_nodes + self.fm_clusters if x.index == edge.source)
                t = next(x for x in self.fm_nodes + self.fm_clusters if x.index == edge.target)
                s_label = s.label.split("@")[0]
                t_label = t.label.split('@')[0]
                if s.node_type == 'cluster':
                    s_label += f'_{s.index}'
                if t.node_type == 'cluster':
                    t_label += f'_{t.index}'
                result.write(f'e,e{i},{edge.significance:.2f},{s_label},'
                             f'{t_label}\n')

    def process_node_edges_fuzzy_filter(self, idx):
        sz = self.num_of_nodes
        min_in_val = sys.float_info.max
        max_in_val = sys.float_info.min
        min_out_val = sys.float_info.max
        max_out_val = sys.float_info.min
        in_values = [0.0 for _ in range(self.num_of_nodes)]
        out_values = [0.0 for _ in range(self.num_of_nodes)]
        ignore_self_loops = self.config.filter_config.edge_filter.ignore_self_loops
        sc_ratio = self.config.filter_config.edge_filter.sc_ratio
        for i in range(0, sz):
            if ignore_self_loops and i == idx:
                continue

            significance = self.concurrency_filter_resultant_binary_values[i][idx]
            if significance > 0.0:
                correlation = self.concurrency_filter_resultant_binary_corr_values[i][idx]
                in_values[i] = significance * sc_ratio + correlation * (1.0 - sc_ratio)

                if in_values[i] > max_in_val:
                    max_in_val = in_values[i]
                if in_values[i] < min_in_val:
                    min_in_val = in_values[i]
            else:
                in_values[i] = 0.0

            significance = self.concurrency_filter_resultant_binary_values[idx][i]
            if significance > 0.0:
                correlation = self.concurrency_filter_resultant_binary_corr_values[idx][i]
                out_values[i] = significance * sc_ratio + correlation * (1.0 - sc_ratio)

                if out_values[i] > max_out_val:
                    max_out_val = out_values[i]
                if out_values[i] < min_out_val:
                    min_out_val = out_values[i]
            else:
                out_values[i] = 0.0

        if self.config.filter_config.edge_filter.interpret_abs:
            max_in_val = max(max_in_val, max_out_val)
            max_out_val = max_in_val
            min_in_val = min(min_in_val, min_out_val)
            min_out_val = min_in_val

        in_limit = max_in_val - (max_in_val - min_in_val) * self.config.filter_config.edge_filter.preserve
        out_limit = max_out_val - (max_out_val - min_out_val) * self.config.filter_config.edge_filter.preserve

        for i in range(0, sz):
            if ignore_self_loops and i == idx:
                continue
            if in_values[i] >= in_limit:
                self.preserve_mask[i][idx] = True
            if out_values[i] >= out_limit:
                self.preserve_mask[idx][i] = True

    def process_node_edges_best_filter(self, idx):
        best_pre = -1
        best_succ = -1
        best_pre_sig = 0.0
        best_succ_sig = 0.0

        sz = self.num_of_nodes

        for i in range(0, sz):
            if i == idx and self.config.filter_config.edge_filter.ignore_self_loops:
                continue
            pre_sig = self.concurrency_filter_resultant_binary_values[i][idx]
            if pre_sig > best_pre_sig:
                best_pre_sig = pre_sig
                best_pre = i
            succ_sig = self.concurrency_filter_resultant_binary_values[idx][i]
            if succ_sig > best_succ_sig:
                best_succ_sig = succ_sig
                best_succ = i

        if best_pre >= 0:
            self.preserve_mask[best_pre][idx] = True
        if best_succ >= 0:
            self.preserve_mask[idx][best_succ] = True

    def process_relation_pair(self, x, y):
        sig_fwd = self.binary_sig_weighted_values[x][y]
        sig_bwd = self.binary_sig_weighted_values[y][x]
        if sig_fwd > 0.0 and sig_bwd > 0.0:
            rel_imp_AB = self.get_relative_imp(x, y)
            rel_imp_BA = self.get_relative_imp(y, x)
            if rel_imp_AB > self.config.filter_config.concurrency_filter.preserve and rel_imp_BA > self.config.filter_config.concurrency_filter.preserve:
                return
            else:
                ratio = min(rel_imp_AB, rel_imp_BA) / max(rel_imp_AB, rel_imp_BA)
                if ratio < self.config.filter_config.concurrency_filter.offset:
                    if rel_imp_AB > rel_imp_BA:
                        self.concurrency_filter_resultant_binary_values[y][x] = 0.0
                        self.concurrency_filter_resultant_binary_corr_values[y][x] = 0.0
                    else:
                        self.concurrency_filter_resultant_binary_values[x][y] = 0.0
                        self.concurrency_filter_resultant_binary_corr_values[x][y] = 0.0
                else:
                    self.concurrency_filter_resultant_binary_values[x][y] = 0.0
                    self.concurrency_filter_resultant_binary_corr_values[x][y] = 0.0
                    self.concurrency_filter_resultant_binary_values[y][x] = 0.0
                    self.concurrency_filter_resultant_binary_corr_values[y][x] = 0.0

    def get_relative_imp(self, x, y):
        sig_ref = self.binary_sig_weighted_values[x][y]
        sig_source_out = 0.0
        sig_target_in = 0.0
        sz = self.num_of_nodes
        for i in range(0, sz):
            if i != x:
                sig_source_out += self.binary_sig_weighted_values[x][i]
            if i != y:
                sig_target_in += self.binary_sig_weighted_values[i][y]
        return (sig_ref / sig_source_out) + (sig_ref / sig_target_in)

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
        return traces

    def extract_node_info(self):
        idx = 0
        self.node_indices = dict()
        for trace in self.log:
            for event in trace:
                name = event['concept:name'] + "@" + event['lifecycle:transition']
                if name not in self.node_indices.keys():
                    self.node_indices[name] = idx
                    idx += 1
        self.num_of_nodes = idx
        self.nodes = list(self.node_indices.keys())

    def extract_aggregates(self):
        if self.metric_settings["distance_significance_binary"][0]:
            self.cal_unary_simple_aggregate()
            self.cal_binary_simple_aggregate()

        if self.metric_settings["routing_significance_unary"][0]:
            if self.metric_settings["distance_significance_binary"][0]:
                self.cal_binary_multi_aggregate()
            else:
                self.cal_binary_simple_aggregate()
                self.cal_binary_multi_aggregate()

    def extract_derivative_metrics(self):
        if self.metric_settings["routing_significance_unary"][0]:
            self.cal_unary_derivative()
        if self.metric_settings["distance_significance_binary"][0]:
            self.cal_binary_derivative()

    def extract_primary_metrics(self):
        max_look_back = self.config.maximal_distance
        # print(self.binary_edge_frequency_values)
        # self.binary_edge_frequency_values = [[0.0 for _ in range(self.num_of_nodes)] for _ in range(self.num_of_nodes)]
        for trace in self.log:
            # print(len(trace))
            look_back = list()
            look_back_indices = list()
            for event in trace:
                # print(len(event))
                follower_event = event
                follower_index = self.node_indices[
                    follower_event['concept:name'] + "@" + follower_event['lifecycle:transition']]
                look_back.insert(0, follower_event)
                look_back_indices.insert(0, follower_index)
                if len(look_back) > (max_look_back + 1):
                    look_back.pop(max_look_back + 1)
                    look_back_indices.pop(max_look_back + 1)

                self.unary_node_frequency_values[follower_index] += 1

                for k in range(1, len(look_back)):
                    # print(len(look_back), look_back, end=' ')
                    # print()
                    # (len(look_back))
                    ref_event = look_back[k]
                    ref_index = look_back_indices[k]
                    att_factor = self.config.attenuation.get_attenuation_factor(k)
                    # print(self.binary_edge_frequency_values)
                    print(self.binary_edge_frequency_values[ref_index][follower_index],ref_index,follower_index, att_factor)
                    self.binary_edge_frequency_values[ref_index][follower_index] += att_factor
                    # print(self.binary_edge_frequency_values[ref_index][follower_index], att_factor, end=' ')
                    if self.metric_settings["proximity_correlation_binary"][0]:
                        self.binary_corr_proximity_values[ref_index][follower_index] += self.cal_proximity_correlation(
                            ref_event, follower_event) * att_factor

                    if self.metric_settings["endpoint_correlation_binary"][0]:
                        self.binary_corr_endpoint_values[ref_index][follower_index] += self.cal_endpoint_correlation(
                            ref_event, follower_event) * att_factor

                    if self.metric_settings["originator_correlation_binary"][0]:
                        self.binary_corr_originator_values[ref_index][
                            follower_index] += self.cal_originator_correlation(
                            ref_event, follower_event) * att_factor

                    if self.metric_settings["datatype_correlation_binary"][0]:
                        self.binary_corr_datatype_values[ref_index][follower_index] += self.cal_datatype_correlation(
                            ref_event, follower_event) * att_factor

                    if self.metric_settings["datavalue_correlation_binary"][0]:
                        self.binary_corr_datavalue_values[ref_index][follower_index] += self.cal_datavalue_correlation(
                            ref_event,
                            follower_event) * att_factor

                    self.binary_corr_divisors[ref_index][follower_index] += att_factor
                # print(self.binary_edge_frequency_values)

    def extract_weighted_metrics(self):
        self.cal_weighted_unary_values()
        self.cal_weighted_binary_values()
        self.cal_weighted_binary_corr_values()

    def cal_weighted_unary_values(self):
        inc1 = self.metric_settings["frequency_significance_unary"][0]
        inc2 = self.metric_settings["routing_significance_unary"][0]
        w1 = self.metric_settings["frequency_significance_unary"][2]
        w2 = self.metric_settings["routing_significance_unary"][2]
        sz = self.num_of_nodes
        valid_matrices = list()
        if inc1 and (w1 > 0.0) and self.is_valid_matrix1D(self.unary_node_frequency_normalized_values):
            valid_matrices.append(self.unary_node_frequency_normalized_values)
        if inc2 and (w2 > 0.0) and self.is_valid_matrix1D(self.unary_derivative_routing_normalized_values):
            valid_matrices.append(self.unary_derivative_routing_normalized_values)
        for valid_matrix in valid_matrices:
            for i in range(sz):
                self.unary_weighted_values[i] += valid_matrix[i]
        self.unary_weighted_values = self.normalize_matrix1D(self.unary_weighted_values)

    def cal_weighted_binary_values(self):
        inc1 = self.metric_settings["frequency_significance_binary"][0]
        inc2 = self.metric_settings["distance_significance_binary"][0]
        w1 = self.metric_settings["frequency_significance_binary"][2]
        w2 = self.metric_settings["distance_significance_binary"][2]
        sz = self.num_of_nodes
        valid_matrices = list()
        if inc1 and (w1 > 0.0) and self.is_valid_matrix2D(self.binary_edge_frequency_normalized_values):
            valid_matrices.append(self.binary_edge_frequency_normalized_values)
        if inc2 and (w2 > 0.0) and self.is_valid_matrix2D(self.binary_derivative_distance_normalized_values):
            valid_matrices.append(self.binary_derivative_distance_normalized_values)

        for valid_matrix in valid_matrices:
            for i in range(0, sz):
                for j in range(0, sz):
                    self.binary_sig_weighted_values[i][j] += valid_matrix[i][j]
        self.binary_sig_weighted_values = self.normalize_matrix2D(self.binary_sig_weighted_values)

    def cal_weighted_binary_corr_values(self):
        inc1 = self.metric_settings["proximity_correlation_binary"][0]
        inc2 = self.metric_settings["originator_correlation_binary"][0]
        inc3 = self.metric_settings["endpoint_correlation_binary"][0]
        inc4 = self.metric_settings["datatype_correlation_binary"][0]
        inc5 = self.metric_settings["datavalue_correlation_binary"][0]
        w1 = self.metric_settings["proximity_correlation_binary"][2]
        w2 = self.metric_settings["originator_correlation_binary"][2]
        w3 = self.metric_settings["endpoint_correlation_binary"][2]
        w4 = self.metric_settings["datatype_correlation_binary"][2]
        w5 = self.metric_settings["datavalue_correlation_binary"][2]
        valid_matrices = list()
        if inc1 and (w1 > 0.0) and self.is_valid_matrix2D(self.binary_corr_proximity_normalized_values):
            valid_matrices.append(self.binary_corr_proximity_normalized_values)
        if inc2 and (w2 > 0.0) and self.is_valid_matrix2D(self.binary_corr_endpoint_normalized_values):
            valid_matrices.append(self.binary_corr_endpoint_normalized_values)
        if inc3 and (w3 > 0.0) and self.is_valid_matrix2D(self.binary_corr_originator_normalized_values):
            valid_matrices.append(self.binary_corr_originator_normalized_values)
        if inc4 and (w4 > 0.0) and self.is_valid_matrix2D(self.binary_corr_datatype_normalized_values):
            valid_matrices.append(self.binary_corr_datatype_normalized_values)
        if inc5 and (w5 > 0.0) and self.is_valid_matrix2D(self.binary_corr_datavalue_normalized_values):
            valid_matrices.append(self.binary_corr_datavalue_normalized_values)

        sz = self.num_of_nodes

        for valid_matrix in valid_matrices:
            for i in range(0, sz):
                for j in range(0, sz):
                    self.binary_corr_weighted_values[i][j] += valid_matrix[i][j]
        self.binary_corr_weighted_values = self.normalize_matrix2D(self.binary_corr_weighted_values)

    def normalize_primary_metrics(self):
        self.unary_node_frequency_normalized_values = self.weight_normalize1D(self.unary_node_frequency_values,
                                                                              self.metric_settings[
                                                                                  "frequency_significance_unary"][1],
                                                                              self.metric_settings[
                                                                                  "frequency_significance_unary"][2])
        self.binary_edge_frequency_normalized_values = self.weight_normalize2D(self.binary_edge_frequency_values,
                                                                               self.metric_settings[
                                                                                   "frequency_significance_binary"][1],
                                                                               self.metric_settings[
                                                                                   "frequency_significance_binary"][2])
        inc1 = self.metric_settings["proximity_correlation_binary"][0]
        inc2 = self.metric_settings["originator_correlation_binary"][0]
        inc3 = self.metric_settings["endpoint_correlation_binary"][0]
        inc4 = self.metric_settings["datatype_correlation_binary"][0]
        inc5 = self.metric_settings["datavalue_correlation_binary"][0]
        inv1 = self.metric_settings["proximity_correlation_binary"][1]
        inv2 = self.metric_settings["originator_correlation_binary"][1]
        inv3 = self.metric_settings["endpoint_correlation_binary"][1]
        inv4 = self.metric_settings["datatype_correlation_binary"][1]
        inv5 = self.metric_settings["datavalue_correlation_binary"][1]
        w1 = self.metric_settings["proximity_correlation_binary"][2]
        w2 = self.metric_settings["originator_correlation_binary"][2]
        w3 = self.metric_settings["endpoint_correlation_binary"][2]
        w4 = self.metric_settings["datatype_correlation_binary"][2]
        w5 = self.metric_settings["datavalue_correlation_binary"][2]
        if inc1:
            self.binary_corr_proximity_normalized_values = self.special_weight_normalize2D(
                self.binary_corr_proximity_values, self.binary_corr_divisors, inv1, w1)
        if inc2:
            self.binary_corr_endpoint_normalized_values = self.special_weight_normalize2D(
                self.binary_corr_endpoint_values, self.binary_corr_divisors, inv2, w2)
        if inc3:
            self.binary_corr_originator_normalized_values = self.special_weight_normalize2D(
                self.binary_corr_originator_values, self.binary_corr_divisors, inv3, w3)
        if inc4:
            self.binary_corr_datatype_normalized_values = self.special_weight_normalize2D(
                self.binary_corr_datatype_values, self.binary_corr_divisors, inv4, w4)
        if inc5:
            self.binary_corr_datavalue_normalized_values = self.special_weight_normalize2D(
                self.binary_corr_datavalue_values, self.binary_corr_divisors, inv5, w5)

    def normalize_derivative_metrics(self):
        if self.metric_settings["routing_significance_unary"][0]:
            self.unary_derivative_routing_normalized_values = self.weight_normalize1D(
                self.unary_derivative_routing_values,
                self.metric_settings["routing_significance_unary"][1],
                self.metric_settings["routing_significance_unary"][2])
        if self.metric_settings["distance_significance_binary"][0]:
            self.binary_derivative_distance_normalized_values = self.weight_normalize2D(
                self.binary_derivative_distance_values,
                self.metric_settings["distance_significance_binary"][1],
                self.metric_settings["distance_significance_binary"][2])

    def normalize_matrix1D(self, lst):
        max_val = max(lst)
        if max_val == 0:
            return lst
        else:
            norm_list = list()
            for val in lst:
                norm_list.append(val / max_val)
            return norm_list

    def normalize_matrix2D(self, lst):
        sz = len(lst[0])
        max_val = max(map(max, lst))
        if max_val == 0:
            return lst
        else:
            norm_list = list()
            for i in range(0, sz):
                temp_list = list()
                for j in range(0, sz):
                    temp_list.append(lst[i][j] / max_val)
                norm_list.append(temp_list)
            return norm_list

    def cal_unary_derivative(self):
        sz = self.num_of_nodes
        for i in range(0, sz):
            in_value = 0.0
            out_value = 0.0
            quotient = 0.0
            for x in range(0, sz):
                if x == i:
                    continue
                in_value += self.binary_simple_aggregate_normalized_values[x][i] * \
                            self.binary_multi_aggregate_normalized_values[x][i]
                out_value += self.binary_simple_aggregate_normalized_values[i][x] * \
                             self.binary_multi_aggregate_normalized_values[i][x]
            if in_value == 0.0 and out_value == 0.0:
                quotient = 0.0
            else:
                quotient = abs((in_value - out_value) / (in_value + out_value))
            self.unary_derivative_routing_values[i] = quotient

    def cal_binary_derivative(self):
        sz = self.num_of_nodes
        for i in range(0, sz):
            sig_source = self.unary_simple_aggregate_normalized_values[i]
            for j in range(0, sz):
                sig_target = self.unary_simple_aggregate_normalized_values[j]
                if sig_source + sig_target == 0:
                    continue
                sig_link = self.binary_simple_aggregate_normalized_values[i][j]
                self.binary_derivative_distance_values[i][j] = 1.0 - (
                        (sig_source - sig_link) + (sig_target - sig_link)) / (sig_source + sig_target)

    def cal_binary_multi_aggregate(self):
        inc1 = self.metric_settings["proximity_correlation_binary"][0]
        inc2 = self.metric_settings["endpoint_correlation_binary"][0]
        inc3 = self.metric_settings["originator_correlation_binary"][0]
        inc4 = self.metric_settings["datatype_correlation_binary"][0]
        inc5 = self.metric_settings["datavalue_correlation_binary"][0]
        valid_metrics = list()
        if inc1 and self.is_valid_matrix2D(self.binary_corr_proximity_normalized_values):
            valid_metrics.append(self.binary_corr_proximity_normalized_values)
        if inc2 and self.is_valid_matrix2D(self.binary_corr_endpoint_normalized_values):
            valid_metrics.append(self.binary_corr_endpoint_normalized_values)
        if inc3 and self.is_valid_matrix2D(self.binary_corr_originator_normalized_values):
            valid_metrics.append(self.binary_corr_originator_normalized_values)
        if inc4 and self.is_valid_matrix2D(self.binary_corr_datatype_normalized_values):
            valid_metrics.append(self.binary_corr_datatype_normalized_values)
        if inc5 and self.is_valid_matrix2D(self.binary_corr_datavalue_normalized_values):
            valid_metrics.append(self.binary_corr_datavalue_normalized_values)

        temp_max = 0
        if len(valid_metrics) > 0:
            sz = self.num_of_nodes
            for i in range(0, sz):
                for j in range(0, sz):
                    aggregated = 0.0
                    for k in range(0, len(valid_metrics)):
                        aggregated += valid_metrics[k][i][j]
                    self.binary_multi_aggregate_normalized_values[i][j] = aggregated
                    if aggregated > temp_max:
                        temp_max = aggregated
            if temp_max > 0:
                for i in range(0, sz):
                    for j in range(0, sz):
                        self.binary_multi_aggregate_normalized_values[i][j] *= (1 / temp_max)
            return

    def compensate_frequency(self, values, divisors):
        size = len(values[0])
        comp_list = list()
        for i in range(size):
            temp_list = list()
            for j in range(size):
                if divisors[i][j] > 0.0:
                    temp_list.append(values[i][j] / divisors[i][j])
                else:
                    temp_list.append(values[i][j])
            comp_list.append(temp_list)
        return comp_list

    def weight_normalize1D(self, lst, invert, normalize_max):
        size = len(lst)
        if normalize_max == 0:
            return [0.0 for i in range(size)]
        else:
            max_val = max(lst)
            if max_val > 0.0:
                norm_list = list()
                for i in range(size):
                    val = (lst[i] * normalize_max) / max_val
                    if invert:
                        val = normalize_max - val
                    norm_list.append(val)
                return norm_list
            else:
                if invert:
                    for i in range(size):
                        lst[i] = normalize_max - lst[i]
                return lst

    def weight_normalize2D(self, lst, invert, normalize_max):
        size = len(lst[0])
        if normalize_max == 0:
            return [[0.0 for i in range(size)] for j in range(size)]
        else:
            max_val = max(map(max, lst))
            if max_val > 0.0:
                norm_list = list()
                for i in range(size):
                    temp_list = list()
                    for j in range(size):
                        val = (lst[i][j] * normalize_max) / max_val
                        if invert:
                            val = normalize_max - val
                        temp_list.append(val)
                    norm_list.append(temp_list)
                return norm_list
            else:
                if invert:
                    for i in range(size):
                        for j in range(size):
                            lst[i][j] = normalize_max - lst[i][j]
                return lst

    def is_valid_matrix2D(self, lst):
        size = len(lst[0])
        for i in range(0, size):
            for j in range(0, size):
                if lst[i][j] > 0.0:
                    return True
        return False

    def is_valid_matrix1D(self, lst):
        for i in range(0, len(lst)):
            if lst[i] > 0.0:
                return True
        return False

    def special_weight_normalize2D(self, values, divisors, invert, normalize_max):
        size = len(values[0])
        if normalize_max == 0:
            norm_list = [[0.0 for i in range(size)] for j in range(size)]
            return norm_list
        else:
            comp_list = self.compensate_frequency(values, divisors)
            max_value = max(map(max, comp_list))
            if max_value > 0.0:
                norm_list = list()
                for i in range(size):
                    temp_list = list()
                    for j in range(size):
                        val = (comp_list[i][j] * normalize_max) / max_value
                        if invert:
                            val = normalize_max - val
                        temp_list.append(val)
                    norm_list.append(temp_list)
                return norm_list
            else:
                if invert:
                    for i in range(size):
                        for j in range(size):
                            comp_list[i][j] = normalize_max - comp_list[i][j]
                return comp_list

    def cal_proximity_correlation(self, evt1, evt2):
        if 'time:timestamp' not in evt1 or 'time:timestamp' not in evt2:
            return 0.0
        time1 = evt1['time:timestamp']
        time2 = evt2['time:timestamp']
        if time1 is not None and time2 is not None:
            time1 = time1.timestamp() * 1000
            time2 = time2.timestamp() * 1000
            if time1 != time2:
                return 1.0 / (time2 - time1)
            else:
                return 1.0
        else:
            return 0.0

    def cal_endpoint_correlation(self, evt1, evt2):
        first_name = evt1['concept:name'] if 'concept:name' in evt1 else "<no name>"
        second_name = evt2['concept:name'] if 'concept:name' in evt2 else "<no name>"
        dist = self.levenshtein_ratio_and_distance(str(first_name), str(second_name))
        big_str_len = max(len(str(first_name)), len(str(second_name)))
        if big_str_len == 0:
            return 1.0
        else:
            return (big_str_len - dist) / big_str_len

    def cal_originator_correlation(self, evt1, evt2):
        first_resource = evt1['org:resource'] if 'org:resource' in evt1 else "<no resource>"
        second_resource = evt2['org:resource'] if 'org:resource' in evt2 else "<no resource>"
        dist = self.levenshtein_ratio_and_distance(str(first_resource), str(second_resource))
        big_str_len = max(len(first_resource), len(second_resource))
        if big_str_len == 0:
            return 1.0
        else:
            return (big_str_len - dist) / big_str_len

    def cal_datatype_correlation(self, evt1, evt2):
        ref_data_keys = list()
        fol_data_keys = list()
        for key in evt1:
            if not self.is_standard_key(key):
                ref_data_keys.append(key)

        for key in evt2:
            if not self.is_standard_key(key):
                fol_data_keys.append(key)

        if (len(ref_data_keys) == 0) or (len(fol_data_keys) == 0):
            return 0
        overlap = 0
        for key in ref_data_keys:
            if key in fol_data_keys:
                overlap += 1

        return overlap / len(ref_data_keys)

    def cal_datavalue_correlation(self, evt1, evt2):
        ref_data_keys = list()
        fol_data_keys = list()
        for key in evt1:
            if not self.is_standard_key(key):
                ref_data_keys.append(key)

        for key in evt2:
            if not self.is_standard_key(key):
                fol_data_keys.append(key)

        if (len(ref_data_keys) == 0) or (len(fol_data_keys) == 0):
            return 0
        key_overlap = 0
        val_overlap = 0
        for key in ref_data_keys:
            if key in fol_data_keys:
                key_overlap += 1
                dist = self.levenshtein_ratio_and_distance(str(evt1[key]), str(evt2[key]))
                big_str_len = max(len(str(evt1[key])), len(str(evt2[key])))
                if big_str_len == 0:
                    val_overlap += 1.0
                else:
                    val_overlap += (big_str_len - dist) / big_str_len

        if key_overlap == 0:
            return 0.0
        else:
            return val_overlap / key_overlap

    def cal_unary_simple_aggregate(self):
        if self.is_valid_matrix1D(self.unary_node_frequency_normalized_values):
            temp_max = 0
            sz = len(self.unary_node_frequency_normalized_values)
            for i in range(sz):
                self.unary_simple_aggregate_normalized_values[i] = self.unary_node_frequency_normalized_values[i]
                if self.unary_node_frequency_normalized_values[i] > temp_max:
                    temp_max = self.unary_node_frequency_normalized_values[i]
            if temp_max > 0:
                for i in range(sz):
                    self.unary_simple_aggregate_normalized_values[i] *= (1 / temp_max)
            return

    def cal_binary_simple_aggregate(self):
        if self.is_valid_matrix2D(self.binary_edge_frequency_normalized_values):
            temp_max = 0
            sz = self.num_of_nodes
            for i in range(0, sz):
                for j in range(0, sz):
                    self.binary_simple_aggregate_normalized_values[i][j] = \
                        self.binary_edge_frequency_normalized_values[i][j]
                    if self.binary_edge_frequency_normalized_values[i][j] > temp_max:
                        temp_max = self.binary_edge_frequency_normalized_values[i][j]
            if temp_max > 0:
                for i in range(0, sz):
                    for j in range(0, sz):
                        self.binary_simple_aggregate_normalized_values[i][j] *= (1 / temp_max)
            return

    def is_standard_key(self, key):
        if key.find("concept") != -1 or key.find("lifecycle") != -1 or key.find("org") != -1 or key.find(
                "time") != -1 or key.find("semantic") != -1:
            return True
        else:
            return False

    def levenshtein_ratio_and_distance(self, s, t):
        rows = len(s) + 1
        cols = len(t) + 1
        distance = np.zeros((rows, cols), dtype=int)

        for i in range(1, rows):
            for k in range(1, cols):
                distance[i][0] = i
                distance[0][k] = k

        for col in range(1, cols):
            for row in range(1, rows):
                if s[row - 1] == t[col - 1]:
                    cost = 0
                else:
                    cost = 2
                distance[row][col] = min(distance[row - 1][col] + 1,
                                         distance[row][col - 1] + 1,
                                         distance[row - 1][col - 1] + cost)

        ratio = ((len(s) + len(t)) - distance[row][col]) / (len(s) + len(t))
        return ratio

    def clusterize(self):
        self.node_cluster_mapping = [i for i in range(0, self.num_of_nodes)]
        self.cluster_dict.clear()
        self.fm_edges_dict.clear()
        self.fm_clusters.clear()
        self.fm_nodes.clear()
        self.fm_edges.clear()

        victims = list()
        for i in range(0, self.num_of_nodes):
            if self.node_filter_resultant_unary_values[i] < self.config.filter_config.node_filter.cut_off:
                victims.append(i)
        cluster_idx = self.num_of_nodes + 1
        for i in range(0, len(victims)):
            if victims[i] == -1:
                continue
            neighbor = self.most_correlated_neighbor(victims[i])
            if neighbor >= self.num_of_nodes:
                self.cluster_dict[neighbor].add_node(victims[i])
                self.node_cluster_mapping[victims[i]] = neighbor
                victims[i] = -1
            else:
                cluster = Cluster(cluster_idx)
                self.cluster_dict[cluster_idx] = cluster
                cluster.add_node(victims[i])
                self.node_cluster_mapping[victims[i]] = cluster_idx
                victims[i] = -1
                if neighbor in victims:
                    cluster.add_node(neighbor)
                    self.node_cluster_mapping[neighbor] = cluster_idx
                    victims[victims.index(neighbor)] = -1
                cluster_idx += 1
                self.fm_clusters.append(cluster)

        cluster_size = len(self.fm_clusters)
        idx = 0
        while idx < cluster_size:
            target = self.get_preferred_merge_target(self.fm_clusters[idx].index)
            if target is not None:
                self.merge_with(target, self.fm_clusters[idx].index)
                self.cluster_dict.pop(self.fm_clusters[idx].index)
                self.fm_clusters.remove(self.fm_clusters[idx])
                cluster_size -= 1
            else:
                idx += 1

        cluster_size = len(self.fm_clusters)
        idx = 0
        while idx < cluster_size:
            cluster = self.fm_clusters[idx]
            pre_set = self.get_predecessors_of_cluster(cluster.index)
            succ_set = self.get_successors_of_cluster(cluster.index)
            if len(pre_set) == 0 and len(succ_set) == 0:
                for prim_index in cluster.get_primitives():
                    self.node_cluster_mapping[prim_index] = -1
                self.cluster_dict.pop(cluster.index)
                self.fm_clusters.remove(cluster)
                cluster_size -= 1
            else:
                idx += 1

        cls_sz = len(self.fm_clusters)
        idx = 0
        while idx < cls_sz:
            cluster = self.fm_clusters[idx]
            if len(cluster.get_primitives()) == 1:
                self.check_for_direct_connection(cluster)
                self.cluster_dict.pop(cluster.index)
                self.fm_clusters.remove(cluster)
                cls_sz -= 1
            else:
                idx += 1

        for cluster in self.fm_clusters:
            primitive_indices = cluster.get_primitives()
            primitive_significances = [self.node_filter_resultant_unary_values[idx] for idx in
                                       primitive_indices]
            cluster.significance = sum(primitive_significances) / len(primitive_significances)
        for i in range(0, self.num_of_nodes):
            if self.node_cluster_mapping[i] != -1 and self.node_cluster_mapping[i] < self.num_of_nodes:
                self.fm_nodes.append(Node(i, self.nodes[i],
                                          self.node_filter_resultant_unary_values[i]))
        for i in range(0, self.num_of_nodes):
            if self.node_cluster_mapping[i] != -1:
                for j in range(0, self.num_of_nodes):
                    significance = self.node_filter_resultant_binary_values[i][j]
                    correlation = self.node_filter_resultant_binary_corr_values[i][j]
                    if significance > 0.0:
                        if i == j:
                            mapped_idx = self.node_cluster_mapping[i]
                            if mapped_idx != -1:
                                if mapped_idx < self.num_of_nodes:
                                    if (i, j) in self.fm_edges_dict.keys():
                                        if self.fm_edges_dict[(i, j)].significance < significance:
                                            self.fm_edges_dict[(i, j)].significance = significance
                                            self.fm_edges_dict[(i, j)].correlation = correlation
                                    else:
                                        self.fm_edges_dict[(i, j)] = Edge(i, j, significance, correlation)
                        else:
                            mapped_i = self.node_cluster_mapping[i]
                            mapped_j = self.node_cluster_mapping[j]
                            if mapped_i == -1 or mapped_j == -1:
                                continue
                            else:
                                if mapped_i == mapped_j:
                                    continue
                                else:
                                    if (mapped_i, mapped_j) in self.fm_edges_dict.keys():
                                        if self.fm_edges_dict[(mapped_i, mapped_j)].significance < significance:
                                            self.fm_edges_dict[(mapped_i, mapped_j)].significance = significance
                                            self.fm_edges_dict[(mapped_i, mapped_j)].correlation = correlation
                                    else:
                                        self.fm_edges_dict[(mapped_i, mapped_j)] = Edge(mapped_i, mapped_j,
                                                                                        significance, correlation)
        for key, value in self.fm_edges_dict.items():
            self.fm_edges.append(value)

    def merge_with(self, winner_index, loser_index):
        loser_primitive_indices = self.cluster_dict[loser_index].get_primitives()
        for prim_idx in loser_primitive_indices:
            self.cluster_dict[winner_index].add_node(prim_idx)
            self.node_cluster_mapping[prim_idx] = winner_index

    def get_preferred_merge_target(self, index):
        pre_target = None
        succ_target = None
        max_pre_corr = 0.0
        max_succ_corr = 0.0
        predecessors = self.get_predecessors_of_cluster(index)
        for predecessor in predecessors:
            if predecessor in self.cluster_dict.keys():
                corr = self.get_aggregate_correlation(index, predecessor)
                if corr > max_pre_corr:
                    max_pre_corr = corr
                    pre_target = predecessor
            else:
                pre_target = None
                max_pre_corr = 0.0
                break

        successors = self.get_successors_of_cluster(index)
        for successor in successors:
            if successor in self.cluster_dict.keys():
                corr = self.get_aggregate_correlation(index, successor)
                if corr > max_succ_corr:
                    max_succ_corr = corr
                    succ_target = successor
            else:
                if pre_target != None:
                    return pre_target
                else:
                    return None

        if max_pre_corr > max_succ_corr:
            return pre_target
        else:
            return succ_target

    def get_successors_of_cluster(self, index):
        cluster = self.cluster_dict[index]
        successors = set()
        for prim_idx in cluster.get_primitives():
            successors = successors.union(self.get_successors_of_node(prim_idx))

        successors -= set(cluster.get_primitives())

        successors.discard(index)
        return successors

    def get_successors_of_node(self, index):
        successors = set()
        for i in range(0, self.num_of_nodes):
            if i == index:
                continue
            elif self.node_filter_resultant_binary_values[index][i] > 0.0:
                if self.node_cluster_mapping[i] != -1:
                    successors.add(self.node_cluster_mapping[i])
        return successors

    def get_aggregate_correlation(self, cluster1_idx, cluster2_idx):
        cluster1_primitive_indices = self.cluster_dict[cluster1_idx].get_primitives()
        cluster2_primitive_indices = self.cluster_dict[cluster2_idx].get_primitives()
        aggregate_corr = 0.0
        for prim1_idx in cluster1_primitive_indices:
            for prim2_idx in cluster2_primitive_indices:
                aggregate_corr += self.edge_filter_resultant_binary_corr_values[prim1_idx][
                    prim2_idx]
                aggregate_corr += self.edge_filter_resultant_binary_corr_values[prim2_idx][
                    prim1_idx]
        return aggregate_corr

    def get_predecessors_of_cluster(self, index):
        cluster = self.cluster_dict[index]
        predecessors = set()
        for prim_idx in cluster.get_primitives():
            predecessors = predecessors.union(self.get_predecessors_of_node(prim_idx))

        predecessors -= set(cluster.get_primitives())

        predecessors.discard(index)
        return predecessors

    def get_predecessors_of_node(self, index):
        predecessors = set()
        for i in range(0, self.num_of_nodes):
            if i == index:
                continue
            elif self.node_filter_resultant_binary_values[i][index] > 0.0:
                if self.node_cluster_mapping[i] != -1:
                    predecessors.add(self.node_cluster_mapping[i])
        return predecessors

    def most_correlated_neighbor(self, idx):
        max_corr = 0.0
        winner_idx = 0
        for i in range(0, self.num_of_nodes):
            if i == idx:
                continue
            curr_corr = self.concurrency_filter_resultant_binary_corr_values[idx][i]
            if curr_corr > max_corr:
                winner_idx = self.node_cluster_mapping[i]
                max_corr = curr_corr
            curr_corr = self.concurrency_filter_resultant_binary_corr_values[i][idx]
            if curr_corr > max_corr:
                winner_idx = self.node_cluster_mapping[i]
                max_corr = curr_corr
        return winner_idx

    def check_for_direct_connection(self, cluster):
        node_index = cluster.get_primitives()[0]
        own_idx = node_index
        pre_set = self.get_predecessors_of_node(own_idx)
        succ_set = self.get_successors_of_node(own_idx)
        for pre_idx in pre_set:
            if pre_idx in self.cluster_dict.keys():
                continue
            for succ_idx in succ_set:
                if succ_idx in self.cluster_dict.keys():
                    continue
                if self.edge_filter_resultant_binary_values[pre_idx][succ_idx] == 0.0:
                    from_sig = self.edge_filter_resultant_binary_values[pre_idx][own_idx]
                    to_sig = self.edge_filter_resultant_binary_values[own_idx][succ_idx]
                    from_corr = self.edge_filter_resultant_binary_corr_values[pre_idx][own_idx]
                    to_corr = self.edge_filter_resultant_binary_corr_values[own_idx][succ_idx]
                    self.node_filter_resultant_binary_values[pre_idx][succ_idx] = \
                        (from_sig + to_sig) / 2.0
                    self.node_filter_resultant_binary_corr_values[pre_idx][succ_idx] = \
                        (from_corr + to_corr) / 2.0
                self.node_filter_resultant_binary_values[pre_idx][own_idx] = 0.0
                self.node_filter_resultant_binary_values[own_idx][succ_idx] = 0.0
                self.node_filter_resultant_binary_corr_values[pre_idx][own_idx] = 0.0
                self.node_filter_resultant_binary_corr_values[own_idx][succ_idx] = 0.0
        self.node_cluster_mapping[own_idx] = -1




class Node:
    def __init__(self, index, label, significance, node_type="primitive"):
        self.index = index
        self.label = label
        self.significance = significance
        self.node_type = node_type

    def __str__(self):
        return self.label+" index: "+str(self.index)+" significance: "+str(self.significance)+" and type: "+self.node_type


class Edge:

    def __init__(self, source_index, target_index, significance, correlation):
        self.source = source_index
        self.target = target_index
        self.significance = significance
        self.correlation = correlation

    def __str__(self):
        return "source: "+ str(self.source)+" target: "+str(self.target)+" significance: "+str(self.significance)+" correlation: "+str(self.correlation)


class Cluster(Node):
    def __init__(self, index):
        super().__init__(index, "Cluster", 1.0, "cluster")
        self.primitives = list()

    def add_node(self, node_index):
        self.primitives.append(node_index)

    def get_primitives(self):
        return self.primitives

    def __str__(self):
        return self.label+" index: "+str(self.index)+" mean significance: "+str(self.significance)+" has primitives: "+str(self.get_primitives())


class Filter:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Filter name: " + self.name


class NodeFilter(Filter):
    def __init__(self, cut_off=0.0):
        super().__init__("node_filter")
        self.cut_off = cut_off

    def __str__(self):
        return super().__str__() + " Cut Off: " + str(self.cut_off)


class EdgeFilter(Filter):
    def __init__(self, edge_transform=1, sc_ratio=0.75, preserve=0.2,
                 interpret_abs=False, ignore_self_loops=True):
        super().__init__("edge_filter")
        self.edge_transform = edge_transform
        self.sc_ratio = sc_ratio
        self.preserve = preserve
        self.interpret_abs = interpret_abs
        self.ignore_self_loops = ignore_self_loops

    def __str__(self):
        if self.edge_transform == 1:
            return super().__str__() + " Edge Transform: " + str(self.edge_transform) + " sc_ratio: " + str(
                self.sc_ratio) + " Preserve: " + str(self.preserve) + " Ignore Self Loops: " + str(
                self.ignore_self_loops) + " Interpret Absolute: " + str(self.interpret_abs)
        else:
            return super().__str__() + "Edge Transform: " + str(self.edge_transform)+" Ignore Self Loops: " + str(self.ignore_self_loops)


class ConcurrencyFilter(Filter):
    def __init__(self, filter_concurrency=True, preserve=0.6, offset=0.7):
        super().__init__("concurrency_filter")
        self.filter_concurrency = filter_concurrency
        self.preserve = preserve
        self.offset = offset

    def __str__(self):
        if self.filter_concurrency:
            return super().__str__() + " Preserve: " + str(self.preserve) + " Offset: " + str(self.offset)
        else:
            return super().__str__() + "Filter is Disabled"


from abc import ABC, abstractmethod


class Configuration:
    def __init__(self, filter_config, metric_configs, attenuation, maximal_distance):
        self.filter_config = filter_config
        self.metric_configs = metric_configs
        self.attenuation = attenuation
        self.maximal_distance = maximal_distance

    def __str__(self):
        metric_info = ""
        for metric in self.metric_configs:
            metric_info += metric.__str__()
        return self.filter_config.__str__() + "\n" + metric_info + " Attenuation: " + str(
            self.attenuation) + " Maximum Distance: " + str(self.maximal_distance)


class FilterConfig:
    def __init__(self, node_filter, edge_filter, concurrency_filter):
        self.node_filter = node_filter
        self.edge_filter = edge_filter
        self.concurrency_filter = concurrency_filter

    def __str__(self):
        return self.node_filter.__str__() + "\n" + self.edge_filter.__str__() + "\n" + self.concurrency_filter.__str__()


class MetricConfig:
    def __init__(self, name, metric_type, include=True, invert=False, weight=1.0):
        self.name = name
        self.metric_type = metric_type
        self.include = include
        self.invert = invert
        self.weight = weight

    def __str__(self):
        return "Metric Name: " + self.name + " Metric Type: " + self.metric_type + " Included: " + str(
            self.include) + " Inverted: " + str(self.invert) + " Weight: " + str(self.weight)


class Attenuation(ABC):
    def __init__(self, buf_size=5, echelons=2.7, attenuation_factors=None):
        self.buf_size = buf_size
        self.echelons = echelons
        self.attenuation_factors = attenuation_factors

    def attenuate(self, value, distance):
        return value * self.get_attenuation_factor(distance)

    def get_attenuation_factor(self, distance):
        if distance < self.buf_size:
            if self.attenuation_factors is None:
                self.generate_buffer()
            return self.attenuation_factors[distance]
        else:
            return self.create_attenuation_factor(distance)

    def generate_buffer(self):
        self.attenuation_factors = []
        for i in range(self.buf_size):
            self.attenuation_factors.append(self.create_attenuation_factor(i))

    @abstractmethod
    def create_attenuation_factor(self, distance):
        pass

    @abstractmethod
    def get_name(self):
        pass

    def __str__(self):
        return "Buffer Size: " + str(self.buf_size) + " Attenuation Factor: " + self.attenuation_factors


class LinearAttenuation(Attenuation):
    def __init__(self, buffer_size, num_of_echelons):
        super().__init__(buffer_size, num_of_echelons)

    def create_attenuation_factor(self, distance):
        if distance == 1:
            return 1.0
        else:
            return float(self.echelons - distance + 1) / float(self.echelons)

    def get_name(self):
        return "Linear Attenuation"

    def __str__(self):
        return " Echelons Value: " + str(self.echelons)


class NRootAttenuation(Attenuation):

    def __init__(self, buffer_size, num_of_echelons):
        super().__init__(buffer_size, num_of_echelons)

    def create_attenuation_factor(self, distance):
        if distance == 1:
            return 1.0
        else:
            return 1.0 / pow(self.echelons, distance - 1)

    def get_name(self):
        if self.echelons == 2:
            return "Square root"
        elif self.echelons == 3:
            return "Cubic root"
        elif self.echelons == 4:
            return "Quadratic root"
        else:
            return str(self.echelons) + "th root"

    def __str__(self):
        return " Echelons Value: " + str(self.echelons)

#test = Plugin()
#test.execute()