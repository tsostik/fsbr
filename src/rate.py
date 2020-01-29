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
        dt_load = Helper.getDate(dt, base.loadRateDates())
        pl_list = base.loadRate(dt_load)
        result = et.Element('rate')
        result.set('date', dt_load.strftime('%Y-%m-%d'))
        for player in pl_list:
            result.append(player.xmlRate)
    return result


def getRateTourns(year):
    if year == 0:
        year = datetime.date.today().year
        if datetime.date.today().month == 1:
            year -= 1
    with BaseIFace() as base:
        result = base.loadRateTourns(year)
    return result.xml
