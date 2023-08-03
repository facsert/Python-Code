
from json import dumps

class FlatDict(dict): 
    """扁平化字典"""   
    def __init__(self, dict_depth):
        super().__init__(dict_depth)
        self.flat = {}
        self.separator = '.'

    def update_dict(self, key, value):
        dic = self
        keys = key.split(self.separator)
        for k in keys[:-1]:
            dic.setdefault(k, {})
            if not isinstance(dic[k], dict):
                dic.update({k: {}})
            dic = dic[k]

        dic[keys[-1]] = value
        self.flat_dict(self)

    def flat_dict(self, dic, parent_key=''):
        for key, value in dic.items():
            new_key = f"{parent_key}{self.separator}{key}" if parent_key else key
            self.flat[new_key] = value
            if isinstance(value, dict):
                self.flat_dict(value, new_key)

    def __setitem__(self, key, value):
        if self.separator in key:
            self.update_dict(key, value)
        else:
            super().__setitem__(key, value)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.flat[key]

    def __delitem__(self, key):
        super().__delitem__(key)
        self.flat = {}
        self.flat_dict(self)

    def __len__(self):
        return super().__len__()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.flat = {}
        self.flat_dict(self)

    def __str__(self):
        return dumps(self, indent=4)


