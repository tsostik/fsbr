from src.db import *
import lxml.etree as et
import datetime


def getFullList():
    with BaseIFace() as base:
        pl_list = base.loadList(1)
        result = et.Element('FullList')
        result.set('date', datetime.date.today().strftime('%Y-%m-%d'))
        for player in pl_list:
            result.append(player.xmlFullList)
    return result


def getRate(dt: datetime.date):
    with BaseIFace() as base:
        pl_list = base.loadList()
        result = et.Element('rate')
        result.set('date', dt.strftime('%Y-%m-%d'))
        for player in pl_list:
            result.append(player.xmlRate)
    return result
