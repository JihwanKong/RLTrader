import time
import datetime
import json
import numpy as np
from configparser import ConfigParser

INIFILENAME = './config/RLTradercfg.ini'
FORMAT_DATE = '%Y%m%d'
FORMAT_DATETIME = '%Y%m%d%H%M%S'
INISECT = {'Log': 'LogInfo'}
INIKEY = {
    # Log info key
    'level': 'loglevel', 'path': 'logpath'
}


################################function################################
def get_today_str():
    today = datetime.datetime.combine(
        datetime.date.today(), datetime.datetime.min.time())
    today_str = today.strftime(FORMAT_DATE)
    return today_str


def get_time_str():

    return datetime.datetime.fromtimestamp(
        int(time.time())).strftime(FORMAT_DATETIME)


def sigmoid(x):
    return 1. / (1. + np.exp(-x))


def IniCfgRead(section, key):
    parser = ConfigParser()
    parser.read(INIFILENAME, encoding='utf-8')

    return parser[section][key]


def getjsonData(filename):
    with open(filename, 'r') as f:
        jsondata = json.load(f)
    return jsondata
################################function################################


##########################dict key type change##########################
dictdata = getjsonData('./config/errorcode.json')
dictmdf = {}
for k, v in dictdata.items():
    dictmdf[int(k)] = dictdata[k]
##########################dict key type change##########################

ERRCODEDICT = dictmdf  # errorcode.json 파일의 내용 받아옴
LOGLEVEL = int(IniCfgRead(INISECT['Log'], INIKEY['level']))
LOGPATH = IniCfgRead(INISECT['Log'], INIKEY['path'])