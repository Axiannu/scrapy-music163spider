# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#判定断点续传得功能
class CatIdItem(scrapy.Item):
    cat_id = scrapy.Field()

class ClassPageItem(scrapy.Item):
    class_page_url = scrapy.Field()


class ArtistItem(scrapy.Item):
    artistid = scrapy.Field()
    artistname = scrapy.Field()
    artisturl = scrapy.Field()

class ArtistAlbumItem(scrapy.Item):
    albumname = scrapy.Field()
    albumid = scrapy.Field()
    albumurl = scrapy.Field()

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


