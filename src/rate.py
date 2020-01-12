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


def getRateDate(dt: datetime.date, base: BaseIFace) -> datetime:
    result = None
    if dt is None:
        result = datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
    else:
        dates_available = base.loadRateDates()
        if dt >= dates_available[0]:
            result = dates_available[0]
        elif dt <= dates_available[-1]:
            result = dates_available[-1]
        else:
            for day in dates_available:
                if day<= dt:
                    result = day
                    break
    return result


def getRate(dt: datetime.date):
    with BaseIFace() as base:
        dt_load = getRateDate(dt, base)
        pl_list = base.loadRate(dt_load)
        result = et.Element('rate')
        result.set('date', dt_load .strftime('%Y-%m-%d'))
        for player in pl_list:
            result.append(player.xmlRate)
    return result
