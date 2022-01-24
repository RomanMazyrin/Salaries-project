class Metrica:
    def __init__(self, name, value,
                 group=None, description=None, label=None, meta_params={}, class_name=''):
        self.name = name
        self.value = value
        self.group = group
        self.description = description
        self.label = label
        self.meta_params = meta_params
        self.class_name = class_name

    def get_meta_param(self, meta_param_name, default=None):
        return self.meta_params.get(meta_param_name, default)

    def set_class(self, class_name):
        self.class_name = class_name

    def get_class(self):
        return self.class_name
