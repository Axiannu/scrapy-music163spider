# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import re
import urllib.parse
import json
import time
import logging
import pymongo


from music.items import SongItem
from music.items import AlbumItem
from music.CommentPostParamsAES import get_params
from music.CommentPostParamsAES import get_encSecKey



class Music163Spider(scrapy.Spider):
    name = 'music163'
    allowed_domains = ['music.163.com']
    #catid_group = [1001,1002,1003,2001,2002,2003,6001,6002,6003,7001,7002,7003,4001,4002,4003]
    catid_group = [2002,2003,6001,6002,6003,7001,7002,7003,4001,4002,4003]




    def __init__(self, settings, *args, **kwargs):
        super(Music163Spider, self).__init__(*args, **kwargs)
        self.mongo_uri = settings.get('MONGO_URI')
        self.mongo_db = settings.get('MONGO_DB')
        self.myclient = pymongo.MongoClient(self.mongo_uri)
        self.mydb = self.myclient[self.mongo_db]



    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider


    def start_requests(self):  #建立初始url，此时start_urls已经无作
        for catid in self.catid_group:
            for pagenum in range(91):
                if 0<pagenum<65:
                    continue
                else:
                    url = 'https://music.163.com/discover/artist/cat?id=' + str(catid) + '&initial=' + str(pagenum)
                    yield scrapy.Request(url=url,callback=self.parse_artist)



    def parse_artist(self, response):
        artists = response.xpath('//*[@class="m-cvrlst m-cvrlst-5 f-cb"]/li').extract()
        print("#################开始解析解析页面：",response.url)
        for artist in artists:
            artist = Selector(text=artist)
            artisthref  = re.sub('\s', "",artist.xpath('//a[@class="nm nm-icn f-thide s-fc0"]/@href').extract_first())
            artistname = artist.xpath('//a[@class="nm nm-icn f-thide s-fc0"]/text()').extract_first()
            try:
                artistid = re.findall('[0-9]\d*', artisthref)[0]
            except Exception as e:
                print(e)
                input(" def parse_artist(self, response):  第38行有异常")
                artistid = ""
            artistalbum_url = 'https://music.163.com/artist/album?id=' + str(artistid) #类似于https://music.163.com/artist/album?id=12236125
            yield scrapy.Request(url=artistalbum_url,callback=self.parse_artist_album)


    def get_albumpage(self,response):
        page = response.xpath('//a[@class="zpgi"]').extract()
        if page:
            return len(page)+1
        else:
            return 1

    def parse_artist_album(self,response):  #获取艺术家主页专辑的页面并get
        albumpage = self.get_albumpage(response)
        for page in range(0,albumpage):
            params = {
                'limit':'12',
                'offset':page*12
            }
            url = response.url + '&' + urllib.parse.urlencode(params)
            yield scrapy.Request(url=url, callback=self.parse_album)


    def parse_album(self,response):
        albums = response.xpath('//ul[@class="m-cvrlst m-cvrlst-alb4 f-cb"]/li').extract()
        for album in albums:
            album = Selector(text=album)
            #albumname = album.xpath('//a[@class="tit s-fc0"]/text()').extract_first()
            albumhref = album.xpath('//a[@class="tit s-fc0"]/@href').extract_first()
            try:
                albumid = re.findall('[0-9]\d*',albumhref)[0]
            except:
                albumid = ""
            #albumdate = album.xpath('//span[@class="s-fc3"]/text()').extract_first()
            albumurl = 'https://music.163.com' + albumhref
            mycol = self.mydb["SongItem"]
            if mycol.find_one({'albumid': albumid}):  #断点续传放置在albumurl，颗粒度
                print("tiaoguo###################", albumurl)
                continue
            else:
                yield scrapy.Request(url=albumurl, callback=self.parse_album_song)


    def parse_album_song(self, response):    #获取专辑页歌曲页数及相关名称及歌曲链接的方法https://music.163.com/album?id=74268947
        item = AlbumItem()
        item['albumname'] = response.xpath('//div[@class="hd f-cb"]/div/h2/text()').extract_first()
        item['albumid'] = response.xpath('//div[@id="content-operation"]/@data-rid').extract_first()
        item['albumdate'] = response.xpath('//div[@class="topblk"]/p[2]/text()').extract_first()
        try:
            item['albumdiscom'] = re.sub('\s',"",response.xpath('//div[@class="topblk"]/p[3]/text()').extract_first())
        except:
            item['albumdiscom'] = ""
        try:
            item['albumsharecount'] = re.findall('[0-9]\d*',str(response.xpath('//a[@class="u-btni u-btni-share "]/i/text()').extract_first()))[0]
        except:
            item['albumsharecount'] = 0
        item['albumcommentscount'] = response.xpath('//span[@id="cnt_comment_count"]/text()').extract_first()
        try:#部分专辑时空的
            songlist = json.loads(response.xpath('//textarea[@id="song-list-pre-data"]/text()').extract_first())
        except:
            songlist = []
        for song in songlist:
            try:
                artistsss = song['artists']
                item['artistid'] = artistsss[0]['id']
                item['artistname'] = artistsss[0]['name']
            except:
                item['artistid'] = 0
                item['artistname'] = ""
            item['songid'] = song["id"]
            item['songname'] = song["name"]
            item['songurl'] = 'https://music.163.com/song?id=' + str(item['songid'])
            item['songscore'] = song["score"]
            commentrequesturl = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(item['songid']) + '?csrf_token='
            headers = {
                'referer': item['songurl'],
                'Host': 'music.163.com',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
            params = get_params(0)  #只爬取热门评论
            encSeckey=get_encSecKey()
            form_data= {
            'params': params,
            'encSecKey': encSeckey
            }
            yield scrapy.FormRequest(url=commentrequesturl,formdata=form_data, callback=self.parse_comment,meta={'item':item},headers=headers)



    def parse_comment(self, response):    #获取歌曲comments的方法
        resitem = response.meta['item']
        item = SongItem()
        item['albumid'] = resitem['albumid']
        item['albumname'] = resitem['albumname']
        item['albumdate'] = resitem['albumdate']
        item['albumdiscom'] = resitem['albumdiscom']
        item['albumsharecount'] = resitem['albumsharecount']
        item['artistid']= resitem['artistid']
        item['artistname'] = resitem['artistname']
        item['songid'] = resitem['songid']
        item['songname'] = resitem['songname']
        item['songurl'] = resitem['songurl']
        item['songscore'] = resitem['songscore']

        commentsdict = json.loads(response.body)
        item['totalcomment'] = commentsdict['total']
        for hotc in commentsdict['hotComments']:
            item['userID'] = (hotc['user'])['userId']
            item['username'] = (hotc['user'])['nickname']
            item['userviptype'] = (hotc['user'])['vipType']
            item['userpicurl'] = (hotc['user'])['avatarUrl']
            item['likedcount'] = hotc['likedCount']
            item['commentId'] = hotc['commentId']
            item['commenttime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(hotc['time'] / 1000)))
            item['commentcontent'] = hotc['content']
            if hotc['beReplied']:
                beReplied = hotc['beReplied'][0]  # 遍历beReplied这个list,不用遍历，只有1个回复，提取对应字典信息
                item['beReplieduserID'] = (beReplied['user'])['userId']
                item['beRepliedusername'] = (beReplied['user'])['nickname']
                item['beRepliedcommentId'] = beReplied['beRepliedCommentId']
                item['beRepliedcommentcontent'] = beReplied['content']
            else:
                item['beReplieduserID'] = ""
                item['beRepliedusername'] = ""
                item['beRepliedcommentId'] = ""
                item['beRepliedcommentcontent'] = ""
            yield item

