from FuzzyMiner import *
from Configuration import *
from Filters import *

if __name__ == '__main__':

    with open('test_log_june_1.xes', 'r') as log_file:
        log = log_file.read()
    fm = FuzzyMiner()
    fm.___init___(log)
    config = Configuration(FilterConfig(node_filter=NodeFilter(),
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

    fm.apply_config(config)
