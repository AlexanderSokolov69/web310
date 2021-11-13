class MyDict(dict):
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, item):
        return self.get(item, None)

    def __getitem__(self, item):
        return self.get(item, None)

    def __repr__(self):
        res = []
        for k in self.keys():
            res.append(f"{k}: {self[k]}")
        return f"<MyDict({' | '.join(res)})"


month = MyDict()
month[9] = 'Сентябрь'
month[10] = "Октябрь"
month[11] = "Ноябрь"
month[12] = "Декабрь"

spis = MyDict()
for n in range(9, 13):
    s = [month[n], n * 100, n * 10, n * 5, n]
    spis[n] = s

for mnt in spis.keys():
    prc = round(spis[mnt][2] / spis[mnt][1], 1)
    spis[mnt].append(prc)

for i, s in enumerate(['Заг1', 'Заг2', 'Заг3', 'Заг4', 'Заг5', '%']):
    print(s, end='\t')
    for key in spis.values():
        print(key[i], end='\t')
    print()
