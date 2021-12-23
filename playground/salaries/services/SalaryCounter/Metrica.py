class Metrica:
    def __init__(self, name, value, group = None, description = None, label = None, meta_params = {}):
        self.name = name
        self.value = value
        self.group = group
        self.description = description
        self.label = label
        self.meta_params = meta_params

    def get_meta_param(self, meta_param_name, default = None):
        return self.meta_params.get(meta_param_name, default)
