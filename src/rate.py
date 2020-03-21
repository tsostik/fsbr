from src.db import *
import lxml.etree as et
import datetime


def getFullList():
    with BaseIFace() as base:
        dt_load = Helper.getDate(datetime.date.today(), base.loadRateDates())
        pl_list = base.loadList(1)
        result = et.Element('FullList')
        result.set('date', dt_load.strftime('%Y-%m-%d'))
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


def getRateForecast():
    with BaseIFace() as base:
        result = et.Element('RateForecast')
        players = base.loadRateForecast()
        rk: int = 0
        for player in players:
            rk += 1
            pxml = player.xml
            pxml.set('rank', str(rk))
            result.append(pxml)
    return result
