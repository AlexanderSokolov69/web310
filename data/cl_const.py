
class Const:
#    DB: QSqlDatabase = None
    VERSION = '1.1'
    BASENAME = 'Кубышка'
    TEST_MODE = False
    IN_TRANSACTION = False
    YEAR = 2021
    DATE_FROM = '09-01'
    DATE_TO = '06-01'
    D_START = '2021-10-01'
    D_END = '2022-01-01'

    PRESENT_PRC = 0.8
    PRESENT_PRC_LOW = 0.2

# Access items
    ACC_PREPOD = '1%'
    ACC_CUBIST = '0%'

    AU_PREPOD = 0
    AU_FULLNAME = 1
    AU_ALLGRP = 2
    AU_EDITOR = 3

    # Users
    USR_ID = 0
    USR_NAME = 1
    USR_FAM = 2
    USR_IMA = 3
    USR_OTCH = 4
    USR_LOGIN = 5
    USR_PHONE = 6
    USR_EMAIL = 7
    USR_BIRTHDAY = 8
    USR_SERT = 9
    USR_ROLE = 10
    USR_PLACE = 11
    USR_DOP = 12
    USR_COMMENT = 13
    USR_PRIV = 14
    USR_IDPRIV = 14
    USR_NAVIGATOR = 15

    # groups
    GRP_ID = 0
    GRP_NAME = 1
    GRP_CNAME = 2
    GRP_VOL = 3
    GRP_LESS = 4
    GRP_YEAR = 5
    GRP_FIO = 6
    GRP_IDU = 7
    GRP_IDC = 8
    GRP_COMMENT = 7

    # rasp
    RSP_ID = 0
    RSP_NAME = 1
    RSP_WEEKNAME = 2
    RSP_KABNAME = 3
    RSP_START = 4
    RSP_END = 5
    RSP_ACCH = 6
    RSP_CNTLESS = 7
    RSP_COMMENT = 8
    RSP_IDG = 9
    RSP_IDD = 10
    RSP_YEAR = 11
    RSP_IDU = 12
    RSP_IDC = 13

    # group_tables
    GT_ID = 0
    GT_GNAME = 1
    GT_STUDNAME = 2
    GT_COMMENT = 3
    GT_IDG = 4
    GT_ACCH = 5
    GT_HDAY = 6
    GT_IDU = 7

    # QGT Group Tables
    QGT_ID = 0
    QGT_GNAME = 1
    QGT_STUDNAME = 2
    QGT_COMMENT = 3
    QGT_IDU = 4
    QGT_IDG = 5
    QGT_NAVIGATOR = 6

    # journals
    JRN_ID = 0
    JRN_DATE = 1
    JRN_THEME = 2
    JRN_START = 3
    JRN_END = 4
    JRN_PRESENT = 5
    JRN_ESTIM = 6
    JRN_SHTRAF = 7
    JRN_COMMENT = 8
    JRN_USRCOMM = 9
    JRN_IDG = 10

    # courses
    CRS_ID = 0
    CRS_NAME = 1
    CRS_TARGET = 2
    CRS_VOLUME = 3
    CRS_LESS = 4
    CRS_ACCH = 5
    CRS_HDAY = 6
    CRS_URL = 7
    CRS_YEAR = 8
    def __init__(self):
        pass

    def to_commit(self, con):
        con.commit()
        Const.IN_TRANSACTION = False




