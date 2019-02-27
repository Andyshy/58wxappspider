# -*- coding:utf-8 -*-

import pymysql

class Mysql(object):
    def __init__(self):
        self.db = pymysql.connect(
            host='127.0.0.1',
            db='cd_58',
            user='root',
            password='',
            port=3306,
            charset='utf8')
        self.cur = self.db.cursor()

    def insert(self, data):
        table = "house_info"
        keys = ", ".join(data.keys())
        values = ", ".join(['%s'] * len(data))
        sql = "insert into {table}({keys}) values ({values})".format(table=table, keys=keys, values=values)
        try:
            if self.cur.execute(sql, tuple(data.values())):
                self.db.commit()
        except pymysql.MySQLError as e:
            print("储存出错", e)
            self.db.rollback()


