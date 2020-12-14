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