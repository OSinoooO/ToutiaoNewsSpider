# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import logging


class ToutiaonewsspiderPipeline(object):
    def __init__(self):
        self.client = MongoClient()
        self.collection = self.client['toutiao']['news']

    def process_item(self, item, spider):
        if not self.collection.find_one({'item_id': item['item_id']}):
            self.collection.insert_one(item)
        else:
            logging.debug('数据已存在')
        return item

