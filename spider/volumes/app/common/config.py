# -*- coding: utf-8 -*-

import os
import codecs
import configparser
import chardet

ini = configparser.ConfigParser()
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
file_path = os.path.join(path, 'config.ini')
with open(file_path, 'rb') as f:
    data = f.read()
    code = chardet.detect(data)

with codecs.open(file_path, 'r', encoding=code['encoding']) as f:
    ini.read_file(f)

mysql_config = dict(ini['mysql'])
spider_config = dict(ini['spider'])
work_time = dict(ini['work_time'])
heartbeat = 10
