class Report:
    def __init__(self):
        self._metrics = []
        self._employee = None
        self._from = None
        self._to = None

    def add_metrica(self, metrica):
        if metrica:
            self._metrics.append(metrica)

    def add_metrics(self, metrics):
        self._metrics.extend(metrics)

    def get_grouped_metrics(self):
        groups = {}
        for metrica in self._metrics:
            if metrica.group not in groups:
                groups[metrica.group] = []
            groups[metrica.group].append(metrica)
        return groups

    def get_metrica_by_label(self, label):
        for metrica in self._metrics:
            if metrica.label == label:
                return metrica
        return None

    def get_metrics_by_meta_param(self, param_name, param_value):
        res = []
        for metrica in self._metrics:
            if metrica.get_meta_param(param_name) == param_value:
                res.append(metrica)
        return res
