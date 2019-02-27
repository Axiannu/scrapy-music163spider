# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import re
import urllib.parse
import json
import time
import logging
import pymongo


from music.items import CatIdItem
from music.items import ClassPageItem
from music.items import ArtistItem
from music.items import AlbumItem
from music.items import SongItem
from music.items import ArtistAlbumItem

from music.CommentPostParamsAES import get_params
from music.CommentPostParamsAES import get_encSecKey






class Music163Spider(scrapy.Spider):

    name = 'music163'
    allowed_domains = ['music.163.com']
    catid_group = [1001,1002,1003,2001,2002,2003,6001,6002,6003,7001,7002,7003,4001,4002,4003]




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

    def breakpoint_crawl(self,item):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        if isinstance(item, CatIdItem):
            name = 'CatIdItem'
            self.db[name].insert(dict(item))
            #return item
        elif isinstance(item, ClassPageItem):
            name = 'ClassPageItem'
            self.db[name].insert(dict(item))
            #return item
        elif isinstance(item, ArtistItem):
            name = 'ArtistItem'
            self.db[name].insert(dict(item))
            #return item
        elif isinstance(item, ArtistAlbumItem):
            name = 'ArtistAlbumItem'
            self.db[name].insert(dict(item))
            #return item
        elif isinstance(item, SongItem):
            name = 'SongCollection'
            self.db[name].insert(dict(item))
            #return item
        self.client.close()



    def start_requests(self):  #建立初始url，此时start_urls已经无作用

        catiditem = CatIdItem()
        for catid in self.catid_group:
            mycol = self.mydb["CatIdItem"]
            if mycol.find_one({'cat_id': catid}):
                print("tiaoguo###########catid#", catid)
                # input("################yield url_item")
                pass
            else:
                for pagenum in range(91):
                    if 0<pagenum<65:
                        continue
                    else:
                        url = 'https://music.163.com/discover/artist/cat?id=' + str(catid) + '&initial=' + str(pagenum)
                        #print('next@@@@@@@@@@@',url)
                        #input('1111111111111111111111111111111111111')
                        yield scrapy.Request(url=url,callback=self.parse_artist)
                catiditem['cat_id'] = catid
                #yield catiditem
                self.breakpoint_crawl(catiditem)


    def parse_artist(self, response):
        mycol = self.mydb["ClassPageItem"]
        if mycol.find_one({'class_page_url': response.url}):
            print("tiaoguo###########class_page_url#", response.url)
            # input("################yield url_item")
            pass
        else:
            classpageitem = ClassPageItem()
            classpageitem['class_page_url'] = response.url
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
                print('########解析artist链接',artistname,artistalbum_url)
                #input('22222222222222222222222222222222')
                yield scrapy.Request(url=artistalbum_url,callback=self.parse_artist_album,meta={'artistid':artistid,'artistname':artistname})
            self.breakpoint_crawl(classpageitem)

    def get_albumpage(self,response):
        page = response.xpath('//a[@class="zpgi"]').extract()
        if page:
            return len(page)+1
        else:
            return 1

    def parse_artist_album(self,response):  #获取艺术家主页专辑的页面并get
        print('@@@@@@@@@解析parse_artist_album链接', response.url)
        mycol = self.mydb["ArtistItem"]
        if mycol.find_one({'artisturl': response.url}):
            print("tiaoguo###########artisturl#", response.url)
            # input("################yield url_item")
            pass
        else:
            artistitem = ArtistItem()
            artistitem['artisturl'] = response.url
            artistitem['artistname'] = response.meta['artistid']
            artistitem['artistname'] = response.meta['artistname']
            albumpage = self.get_albumpage(response)
            #print('albumpage',albumpage)
            for page in range(0,albumpage):
                params = {
                    'limit':'12',
                    'offset':page*12
                }
                url = response.url + '&' + urllib.parse.urlencode(params)
                #print('album的url为',url)
                #input('33333333333333333333333333333333')
                yield scrapy.Request(url=url, callback=self.parse_album)
            self.breakpoint_crawl(artistitem)



    def parse_album(self,response):
        print('%%%%%%%%%%解析parse_album', response.url)
        albums = response.xpath('//ul[@class="m-cvrlst m-cvrlst-alb4 f-cb"]/li').extract()
        for album in albums:
            album = Selector(text=album)
            #albumname = album.xpath('//a[@class="tit s-fc0"]/text()').extract_first()
            albumhref = album.xpath('//a[@class="tit s-fc0"]/@href').extract_first()
            #albumid = re.findall('[0-9]\d*', albumhref)[0]
            #albumdate = album.xpath('//span[@class="s-fc3"]/text()').extract_first()
            albumurl = 'https://music.163.com' + albumhref
            #print('解析albumurl',albumurl)
            #input('4444444444444444444444444444444')
            yield scrapy.Request(url=albumurl, callback=self.parse_album_song)


    def parse_album_song(self, response):    #获取专辑页歌曲页数及相关名称及歌曲链接的方法https://music.163.com/album?id=74268947
        print('%#$#$#$#@#$%%%解析parse_album_song', response.url)
        mycol = self.mydb["ArtistAlbumItem"]
        if mycol.find_one({'albumurl': response.url}):
            print("tiaoguo###################", response.url)
            #input("################yield url_item")
            pass
        else:
            #print("继续",response.url)
            item = AlbumItem()
            artistalbumitem = ArtistAlbumItem()
            artistalbumitem['albumurl'] = response.url

            item['albumname'] = response.xpath('//div[@class="hd f-cb"]/div/h2/text()').extract_first()
            item['albumid'] = response.xpath('//div[@id="content-operation"]/@data-rid').extract_first()
            item['albumdate'] = response.xpath('//div[@class="topblk"]/p[2]/text()').extract_first()

            artistalbumitem['albumname'] = item['albumname']
            artistalbumitem['albumid'] = item['albumid']

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
                    item['artistid'] = artistsss[0]['artistid']
                    item['artistname'] = artistsss[0]['artistname']
                except:
                    item['artistid'] = 0
                    item['artistname'] = ""
                item['songid'] = song["id"]
                item['songname'] = song["name"]
                item['songurl'] = 'https://music.163.com/song?id=' + str(item['songid'])
                item['songscore'] = song["score"]
                commentrequesturl = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(item['songid']) + '?csrf_token='
                #print(item, response.url)
                #input("55555555555555555555555555555")
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
            self.breakpoint_crawl(artistalbumitem)


    def parse_comment(self, response):    #获取歌曲comments的方法
        print("^^^^^^^^^parse_comment",response.url)
        mycol = self.mydb["SongCollection"]
        resitem = response.meta['item']
        if mycol.find_one({'songurl': resitem['songurl']}):
            print("tiaoguo###################歌曲名字")
           # print(mycol.find_one({'songurl': resitem['songurl']}))
            #input("################yield url_item")
            pass
        else:
            print("正常解析中@@@@@@@@@@@@")
            item = SongItem()
            #print("888888888888888888888888888",response.meta['item'])
            #resitem = response.meta['item']
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
                #print(item)
                #input('9999999999999999999999999999')
                yield item