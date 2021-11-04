class MyDict(dict):
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, item):
        return self.get(item, None)

    # def __repr__(self):
    #     return f"{self.key()}: {self.values()}"
    #

if __name__ == '__main__':
    d = MyDict(attr='32')

    print(str(d))
