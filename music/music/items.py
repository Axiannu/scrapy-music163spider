# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class AlbumItem(scrapy.Item):
    albumname = scrapy.Field()
    albumid = scrapy.Field()
    albumdate = scrapy.Field()
    albumdiscom = scrapy.Field()
    albumsharecount = scrapy.Field()
    albumcommentscount = scrapy.Field()
    artistid = scrapy.Field()
    artistname = scrapy.Field()
    songid = scrapy.Field()
    songurl = scrapy.Field()
    songname = scrapy.Field()
    songscore = scrapy.Field()



class SongItem(scrapy.Item):
    totalcomment = scrapy.Field()
    userID = scrapy.Field()
    username = scrapy.Field()
    userviptype = scrapy.Field()
    userpicurl = scrapy.Field()
    likedcount = scrapy.Field()
    commentId = scrapy.Field()
    commenttime = scrapy.Field()
    commentcontent = scrapy.Field()
    beReplieduserID = scrapy.Field()
    beRepliedusername = scrapy.Field()
    beRepliedcommentId = scrapy.Field()
    beRepliedcommentcontent = scrapy.Field()
    albumid = scrapy.Field()
    albumname = scrapy.Field()
    albumdate = scrapy.Field()
    albumdiscom = scrapy.Field()
    albumsharecount = scrapy.Field()
    artistid = scrapy.Field()
    artistname = scrapy.Field()
    songid = scrapy.Field()
    songname = scrapy.Field()
    songurl = scrapy.Field()
    songscore = scrapy.Field()


