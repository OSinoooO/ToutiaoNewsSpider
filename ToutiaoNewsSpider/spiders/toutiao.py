# -*- coding: utf-8 -*-
import scrapy
import json
import logging
import re
from copy import deepcopy
from ..settings import TAG


class ToutiaoSpider(scrapy.Spider):
    name = 'toutiao'
    allowed_domains = ['toutiao.com']
    start_urls = ['https://www.toutiao.com/api/pc/feed/?category={}&min_behot_time=0']

    def start_requests(self):
        url = self.start_urls[0].format(TAG)
        yield scrapy.Request(
            url=url,
            callback=self.parse
        )

    def parse(self, response):  # 解析接口数据
        try:
            html = json.loads(response.body)
            message = html['message']
            if message == 'success':
                data_list = html['data']
                for data in data_list:
                    item = {}
                    item['group_id'] = data['group_id']
                    item['item_id'] = data['item_id']
                    item['title'] = data['title']
                    item['tag'] = data['tag']
                    try:
                        item['chinese_tag'] = data['chinese_tag']
                    except:
                        item['chinese_tag'] = None
                    try:
                        item['abstract'] = data['abstract']
                    except:
                        item['abstract'] = None
                    try:
                        item['comments_count'] = data['comments_count']
                    except:
                        item['comments_count'] = 0
                    try:
                        item['media_url'] = data['media_url']
                    except:
                        item['media_url'] = None
                    try:
                        item['source_url'] = data['source_url']
                    except:
                        item['source_url'] = None
                    try:
                        item['source'] = data['source']
                    except:
                        item['source'] = None
                    try:
                        item['label'] = data['label']
                    except:
                        item['label'] = []
                    detail_url = 'https://www.toutiao.com' + item['source_url']
                    # 详情页
                    yield scrapy.Request(
                        url=detail_url,
                        callback=self.parse_detail,
                        meta={'item': item}
                    )

                # 更多新闻
                max_behot_time = html['next']['max_behot_time']
                next_url = 'https://www.toutiao.com/api/pc/feed/?max_behot_time={}&category={}'.format(max_behot_time, TAG)
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse
                )
            else:
                logging.debug('没有数据返回:', response.url)
        except Exception as e:
            logging.error(e)

    def parse_detail(self, response):  # 解析详情页
        try:
            print(response.url)
            item = response.meta['item']
            item['content'] = re.findall(r'content: \'(.*?)\',', response.body.decode(), re.S)[0]
            item['time'] = re.findall(r'time: \'(.*?)\'', response.body.decode(), re.S)[0]

            # 热门评论
            comment_url = 'https://www.toutiao.com/api/comment/list/'
            comment_url += '?group_id={}&item_id={}&offset={}&count={}'.format(item['group_id'], item['item_id'], 0, 20, )
            yield scrapy.Request(
                url=comment_url,
                callback=self.parse_hot_comment,
                meta={'item': item}
            )
        except:
            logging.debug('页面可能出现错误:', response.url)

    def parse_hot_comment(self, response):  # 解析热门评论
        item = response.meta['item']
        html = json.loads(response.body)
        if html['message'] == 'success':
            item['comments'] = []
            comments_list = html['data']['comments']
            for com in comments_list:
                comment = {}
                comment['id'] = com['id']
                comment['text'] = com['text']
                comment['digg_count'] = com['digg_count']
                comment['reply_count'] = com['reply_count']
                comment['user'] = com['user']
                comment['create_time'] = com['create_time']
                item['comments'].append(comment)
                yield deepcopy(item)
        else:
            print('没有数据返回:', response.url)
