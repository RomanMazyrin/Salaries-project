class Metrica:
    def __init__(self, name, value, group=None, description=None, label=None):
        self.name = name
        self.value = value
        self.group = group
        self.description = description
        self.label = label
