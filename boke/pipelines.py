# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class BokePipeline(object):
    def process_item(self, item, spider):
        cur = self.conn.cursor()
        sql = "INSERT into type(onetype,twotype,name,question1,question2,question3,answer1,answer2,answer3,answer21,answer22,answer23,answer31,answer32,answer33) VALUE('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
            item["type1"], item["type2"], item["name"],item["question1"],item["question2"],item["question3"],item['answer1'],item['answer2'],item['answer3'],item['answer11'],item['answer22'],item['answer33'],item['answer111'],item['answer222'],item['answer333'])
        cur.execute(sql)
        cur.close()
        return item

    def open_spider(self, spider):
        # 建立数据库的链接
        try:
            self.conn = pymysql.connect(
                host="localhost",
                port=3306,
                user="root",
                passwd="accp",
                db="boke",
                charset="utf8"
            )
            self.conn.autocommit(True)
        except Exception as e:
            print("链接数据库失败:" + e)

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()

