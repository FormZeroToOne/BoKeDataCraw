# -*- coding: utf-8 -*-
import scrapy
import  json
from scrapy.contrib.loader import ItemLoader
from scrapy.selector import Selector
import re
import random
import requests
import time
from lxml import etree

from boke.items import BokeItem


class BokesSpider(scrapy.Spider):
    name = 'bokes'
    # allowed_domains = ['top.baidu.com']
    start_urls = ['http://top.baidu.com/boards?fr=topbuzz_b338']

    def parse(self, response):
        r = list()
        jsonstr = list(response.xpath("//*[@id='main']/div/div/div/a/text()").extract())

        urls = response.css("#main > div > div.bd a::attr('href')").extract()
        for url in urls:
            url="http://top.baidu.com/"+url
            yield  response.follow(url,self.detail)

    def detail(self,response):
        bk = BokeItem()
        lis = response.css("#flist > div.hblock > ul > li > a::attr('title')").extract()
        # #print("打开详情页:"+response.url)
        lisr = r'(.+)榜单首页'

        b = re.findall(lisr,lis[0])
        bangdan = response.css("#main > div.mainBody > div > div > h2::text").extract()
        if '岛屿' in bangdan[0] or '国内热门景点' in bangdan[0] or '国外热门景点' in bangdan[0] or '古镇' in bangdan[0] or '中国名山' in bangdan[0]:
            b.append('旅游')
        if b:
            print("=========b"+b[0])
        # print("=======bd"+bangdan[0])

        typ = r'今日(.+)排行榜'
        typ1 = r'(.+)排行榜'
        if '今日' in bangdan[0] and '排行榜' in bangdan[0] and '今日热点' not  in bangdan[0]:
            type2 = re.findall(typ,bangdan[0])
        elif '热点' in b[0]:
            type2 = re.findall(typ1,bangdan[0])
        if '电影' in b[0] and str(b[0]) in str(type2[0]) or  '动漫' in b[0] and str(b[0]) in str(type2[0]):
            tr = type2[0]
            type2[0] = tr[0:len(b[0])]
                # print(tr)
        if str(b[0]) in '偶像电视剧' or  str(b[0]) in  '言情电视剧' or str(b[0]) in '古装电视剧':
            tr = type2[0]
            type2[0] = tr[0:len(b[0])-1]
        if '奇幻小说' in bangdan[0]  or '言情小说' in bangdan[0] or '仙侠小说' in bangdan[0] or '悬疑小说' in bangdan[0] or '军事小说' in bangdan[0] :
            tr = type2[0]
            type2[0] = tr[0:len(b[0])+2]

        if '游戏竞技' == bangdan[0] and '小说' in b[0] or '青春校园' == bangdan[0] and '小说' in b[0] or '穿越架空' == bangdan[0] and '小说' in b[0]  or '文学经典' == bangdan[0] and '小说' in b[0] or '耽美同人' == bangdan[0] and '小说' in b[0] :
            type2 = ['']
            type2[0] = bangdan[0]
        if '动漫卡通' in bangdan[0] or '今日电视剧排行榜' == bangdan[0] or '今日电影排行榜' == bangdan[0] or '今日综艺排行榜' == bangdan[0] or '今日小说排行榜' == bangdan[0]:
            type2[0] = '全部'
        if '电动汽车' == bangdan[0] and '汽车' in b[0] or '汽车月度榜单' == bangdan[0] and '汽车' in b[0]:
            type2 = [' ']
            type2[0] = bangdan[0]
        if '生活' in b[0] and '小吃排行' in bangdan[0]:
            type2 = [' ']
            type2[0] = '小吃'
        if '生活' in b[0] and '化妆品月度榜单' in bangdan[0]:
            type2 = [' ']
            type2[0] = '化妆品月度榜单'
        if '科技' in b[0] and '手机月度榜单' in bangdan[0]:
            type2 = [' ']
            type2[0] = '手机月度榜单'
        if '科技' in b[0] and '热门软件' in bangdan[0]:
            type2 = [' ']
            type2[0] = '软件'
        if '热点' in b[0] and '今日热点事件' in bangdan[0]:
            type2 = [' ']
            type2[0] = '今日热点'
        if '旅游' in b[0] and '今日热门岛屿排行榜' in bangdan[0]:
            type2 = [' ']
            type2[0] = '岛屿'
        if '旅游' in b[0] and '今日国内热门景点' in bangdan[0]:
            type2 = [' ']
            type2[0] = '国内景点'
        if '旅游' in b[0] and '今日国外热门景点' in bangdan[0]:
            type2 = [' ']
            type2[0] = '国外景点'
        if '人物' in b[0] and '今日热点人物' in bangdan[0]:
            type2 = [' ']
            type2[0] = '热点人物'
        print("===========t"+type2[0])
        # 电影/电视剧/综艺/动漫 +
        dianying = ['好看吗','评分','哪里可以看','下载地址','吐槽','在线观看','上映时间','谁是主演','全集','磁力','迅雷下载地址','bt']
        # 小说 +
        xiaoshuo = ['在线阅读网站推荐','哪里可以看','如何评价','作者是谁','的结局怎么样','大结局','最新章节是第几章','最好看的情节是哪里','哪里可以无弹窗观看','哪里可以看免费']
        # 游戏 +
        youxi = ['哪里可以玩到','好玩吗','活动怎么做','谁最厉害','怎么刷金币','怎么解封','什么配置可以玩','重置失败怎么办','是什么意思','的介绍','出来多久了','维护时间','怎么升级','怎么充值','怎么退款','小技巧']
        # 人物 +
        renwu = ['是谁','怎么样','的评价','的介绍','是哪里人','现在在哪','多大','经典语录','的资料','的成就','的故事','如何评价','为什么出名','是做什么的']

        # 汽车 +
        qiche = ['怎么样','值得买吗','有什么毛病','是什么配置','哪一款最经典','的参数','性能怎么样','好不好','性价比怎么样','什么时候上市的','是哪一年的车','油耗多少','首付多少钱','是自动档还是手动挡']

        # 生活

        ## '旅游城市' 和 风景名胜 +
        lvfeng = ['好玩吗','怎么样','旅游路线','的小吃排名','哪里有美食','怎么玩才省钱']

        ## 博物馆+
        bowuguan = ['收费吗','在哪里','开放时间','院长是谁','是什么类型的','里面都展览什么','的简介','的电话多少','的资料','哪里能找到','的导游']

        ## 宠物+
        chongwu = ['吃什么','怎么养','的优点','的缺点','多少钱','好不好养','有多大','可爱吗','行情怎么养','生病了怎么办','的资料','的性格怎么样']

        ## 小吃+
        xiaochi = ['好吃吗','多少钱','哪里可以吃到','营养吗','的好处','的坏处','的功效','是哪里的','宠物可不可以吃','怎么吃','哪里能吃到正宗的','怎么做']

        # +畅销书
        changxiaoshu = ['的作者是谁','的评价怎么样','的结局是什么','一共有几部','主要讲什么内容','好看吗','值得买吗','有什么含义','最精彩的部分']

        # 高校 +
        gaoxiao = ['在哪里','怎么样','排第几','有什么专业','哪个专业最好','分数线','的地址','的电话','的名人事迹','的校训是什么','在哪个省','建立多久了']

        # 化妆品/奢侈品
        huashe = ['是什么意思','多少钱','有哪些系列','哪个系列的最好','怎么看是不是正品','的介绍','这个品牌的由来','是哪个国家产的','会过期吗','专卖店在哪','的历史','能退换吗','最经典的一款']

        # 公益组织  +  怎么给加献爱心
        gongyi = ['怎么申请','是真的还是假的','有用嘛','是官方的还是民间的','的公益活动','的联系电话','的地址','是什么意思','的口号']

        # 科技
        ## 手机  + [二手 + 手机名称 + 多少钱]
        shouji = ['值得买吗','最经典的一款','尺寸多大','分辨率多大','摄像头怎么样','有美颜吗','怎么添加联系人','怎么下载软件','什么时候上市的','配置怎么样','为什么这么贵','越来越卡怎么办','变砖了怎么办','怎么刷机','怎么越狱','怎么root','怎么导入导出数据','怎么备份数据','哪种颜色好看']

        # 软件  +
        ruanjian = ['软件名称','是谁开发的','怎么下载','怎么卸载','怎么连不上网','是什么','是干嘛的','的账号怎么注册','的等级怎么升级','是什么类型的软件']

        # 热点
        redian = ['']

        # 旅游
        lvyou = ['好玩吗','怎么样','旅游路线','的小吃排名','哪里有美食','怎么玩才省钱']


        newsSelector = Selector(response=response).xpath('//table[@class="list-table"]/tr')
        for baiduitem in newsSelector:
            # 获取百度新闻每一条的title
            if(len(baiduitem.xpath('td[@class="first"]')) > 0):
                text = baiduitem.xpath('td[@class="keyword"]/a[@class="list-title"]/text()')
                t = str(text)
                wz = r"data='(.+)'"
                p = re.findall(wz,t)
                # print(p[0])

                question = list()
                if b[0]  == '电影' or b[0] == '电视剧' or b[0] == '动漫' or b[0] == '综艺':
                    # dianying.append(p[0])
                    for i in random.sample(dianying, 3):
                        question.append(p[0]+i)
                if b[0] == '小说':
                    # xiaoshuo.append(p[0])
                    for i in random.sample(xiaoshuo, 3):
                        question.append(p[0] + i)
                if b[0] == '游戏':
                    # youxi.append(p[0])
                    for i in random.sample(youxi, 3):
                        question.append(p[0] + i)
                if b[0] == '人物':
                    # renwu.append(p[0])
                    for i in random.sample(renwu, 3):
                        question.append(p[0] + i)

                if b[0] == '汽车':
                    # qiche.append(p[0])
                    for i in random.sample(qiche, 3):
                        question.append(p[0] + i)
                if b[0] == '生活' and  '旅游城市' in type2[0] or b[0] == '生活' and '风景名胜' in type2[0]:
                    # lvfeng.append(p[0])
                    for i in random.sample(lvfeng, 3):
                        question.append(p[0] + i)
                if b[0] == '生活' and  '博物馆' in type2[0]:
                    # bowuguan.append(p[0])
                    for i in random.sample(bowuguan, 3):
                        question.append(p[0] + i)
                if b[0] == '生活' and  '宠物' in type2[0]:
                    # chongwu.append(p[0])
                    for i in random.sample(chongwu, 3):
                        question.append(p[0] + i)

                if b[0] == '生活' and '小吃' in type2[0]:
                    # xiaochi.append(p[0])
                    for i in random.sample(xiaochi, 3):
                        question.append(p[0] + i)

                if b[0] == '生活' and  '畅销书' in type2[0]:
                    # changxiaoshu.append(p[0])
                    for i in random.sample(changxiaoshu, 3):
                        question.append(i+p[0])
                if b[0] == '生活' and  '高校' in type2[0]:
                    # gaoxiao.append(p[0])
                    for i in random.sample(gaoxiao, 3):
                        question.append(p[0] + i)
                if b[0] == '生活' and  '慈善' in type2[0]:
                    # gongyi.append(p[0])
                    for i in random.sample(gongyi, 3):
                        question.append(p[0] + i)

                if b[0] == '生活' and  '化妆' in type2[0] or b[0] == '生活' and '奢侈' in type2[0]:
                    # huashe.append(p[0])
                    for i in random.sample(huashe, 3):
                        question.append(p[0] + i)

                if b[0] == '科技' and '手机' in type2[0]:
                    # shouji.append(p[0])
                    for i in random.sample(shouji, 3):
                        question.append(p[0] + i)
                if b[0] == '科技' and '软件' in type2[0]:
                    # ruanjian.append(p[0])
                    for i in random.sample(ruanjian, 3):
                        question.append(p[0] + i)

                if b[0] == '热点':
                    question.append(p[0])
                    question.append(p[0])
                    question.append(p[0])
                if b[0] == '旅游':
                    # lvyou.append(p[0])
                    for i in random.sample(lvyou, 3):
                        question.append(p[0] + i)


                q1 = question[0]
                q2 = question[1]
                q3 = question[2]

                s = requests.Session()
                f = q1
                c = str(f.encode('gbk')).split("'")[1]
                v = c.replace('\\x', '%')
                h = "https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&ie=gbk&word={0}".format(v)
                se = s.get(h)
                print(h)
                se.encoding = 'utf-8'
                root = etree.HTML(se.content)
                urlxin1 = root.xpath('//*[@class="dt mb-4 line"]/a/@href')
                # se = s.get(urlxin1[1])
                # se.encoding = 'utf-8'
                # root = etree.HTML(se.content)
                # a = root.xpath('//*[@class="best-text mb-10"]')
                for i in range(0, len(urlxin1)):
                    se = s.get(urlxin1[i])
                    se.encoding = 'utf-8'
                    # print(se.text)
                    root = etree.HTML(se.content)
                    a = root.xpath('//*[@class="best-text mb-10"]')
                    if a != ' ' or len(a) > 0:
                        break
                answer_text = root.xpath('//*[@class="answer-text mb-10 line"]/text()[2]')
                if a:
                    ba = a[0].xpath('string(.)').split('\n\n\n展开全部\n\n\n')
                if len(answer_text) >= 1:
                    for i in answer_text:
                        bk['answer2'] = answer_text[0]
                else:
                    bk['answer2'] = ' '

                    print("===============b1" + ba[1])
                if ba[1]:
                    bk['answer1'] = ba[1]
                else:
                    bk['answer1'] = '此问题没有人关注'
                s = requests.Session()
                ######
                f = q2
                c = str(f.encode('gbk')).split("'")[1]
                v = c.replace('\\x', '%')
                h = "https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&ie=gbk&word={0}".format(v)
                se = s.get(h)
                print(h)
                se.encoding = 'utf-8'
                root = etree.HTML(se.content)
                urlxin1 = root.xpath('//*[@class="dt mb-4 line"]/a/@href')
                # se = s.get(urlxin1[1])
                # se.encoding = 'utf-8'
                # root = etree.HTML(se.content)
                # a = root.xpath('//*[@class="best-text mb-10"]')
                for i in range(0, len(urlxin1)):
                    se = s.get(urlxin1[i])
                    se.encoding = 'utf-8'
                    # print(se.text)
                    root = etree.HTML(se.content)
                    a = root.xpath('//*[@class="best-text mb-10"]')
                    if a != ' ' or len(a) > 0:
                        break
                answer_text = root.xpath('//*[@class="answer-text mb-10 line"]/text()[2]')
                if a:
                    ba2 = a[0].xpath('string(.)').split('\n\n\n展开全部\n\n\n')
                if len(answer_text) >= 1:
                    for i in answer_text:
                        bk['answer22'] = answer_text[0]
                else:
                    bk['answer22'] = ' '

                    print("===============ba2" + ba[1])
                if ba2[1]:
                    bk['answer11'] = ba2[1]
                else:
                    bk['answer11'] = '此问题没有人关注'

                s = requests.Session()
                f = q3
                c = str(f.encode('gbk')).split("'")[1]
                v = c.replace('\\x', '%')
                h = "https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&ie=gbk&word={0}".format(v)
                se = s.get(h)
                print(h)
                se.encoding = 'utf-8'
                root = etree.HTML(se.content)
                urlxin1 = root.xpath('//*[@class="dt mb-4 line"]/a/@href')
                # se = s.get(urlxin1[1])
                # se.encoding = 'utf-8'
                # root = etree.HTML(se.content)
                # a = root.xpath('//*[@class="best-text mb-10"]')
                for i in range(0, len(urlxin1)):
                    se = s.get(urlxin1[i])
                    se.encoding = 'utf-8'
                    # print(se.text)
                    root = etree.HTML(se.content)
                    a = root.xpath('//*[@class="best-text mb-10"]')
                    if a != ' ' or len(a) > 0:
                        break
                answer_text = root.xpath('//*[@class="answer-text mb-10 line"]/text()[2]')
                if a:
                    ba3 = a[0].xpath('string(.)').split('\n\n\n展开全部\n\n\n')
                if len(answer_text) >= 1:
                    for i in answer_text:
                        bk['answer222'] = answer_text[0]
                else:
                    bk['answer222'] = ' '

                    print("===============ba3" + ba3[1])
                if ba3[1]:
                    bk['answer111'] = ba3[1]
                else:
                    bk['answer111'] = '此问题没有人关注'
                bk['answer3'] = ' '
                bk['answer33'] = ' '
                bk['answer333'] = ' '
                bk['type1'] = b[0]
                bk['type2'] = type2[0]
                bk['name'] = p[0]
                bk['question1'] ="<h1>"+q1+"</h1>"
                bk['question2'] = "<h2>"+q2+"</h2>"
                bk['question3'] = "<h2>"+q3+"</h2>"
                yield bk




