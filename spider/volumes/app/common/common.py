# -*- encoding: utf-8 -*-
from common.config import mysql_config
from common.mysql_conn import MysqlConnect


def get_mysql_conn():
    mysql_conn = MysqlConnect(mysql_config)
    mysql_conn.create_connect()
    return mysql_conn
