class MyDict(dict):
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, item):
        return self.get(item, None)


def date_us_ru(data):
    """
    Перевод US даты в RU
    :param data:
    :return:
    """
    data = str(data).strip()
    ret = data
    if len(data) == 10:
        try:
            ret = f"{int(data[8:10:1]):02}.{int(data[5:7:1]):02}.{int(data[0:4:1]):04}"
        except ValueError:
            pass
            # print('error in date_us_ru(data)')
    return ret


def date_ru_us(data):
    """
    Перевод RU даты в US
    :param data:
    :return:
    """
    tst = str(data).strip()
    ret = '1900-01-01'
    if len(tst) > 0:
        try:
            if len(tst) == 4:
                tst = f"01.01.{int(tst):04}"
            elif 0 < len(tst) < 3:
                tst = f"01.01.20{int(tst):02}"
            ret = f"{int(tst[6:10:1]):04}-{int(tst[3:5:1]):02}-{int(tst[0:2:1]):02}"
        except ValueError:
            pass
            # print('error in date_ru_us(data)')
    return ret


if __name__ == '__main__':
    d = MyDict(attr='32')

    print(str(d))
