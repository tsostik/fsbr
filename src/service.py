import datetime
import lxml.etree as et
from src.db import BaseIFace
from src.helper import Helper


def getRateTourns(year) -> et.Element:
    if year == 0:
        year = datetime.date.today().year
        if datetime.date.today().month == 1:
            year -= 1
    with BaseIFace() as base:
        result = base.loadRateTourns(year)
    return result.xml


def getRazrChange(date: datetime.date) -> et.Element:
    result: et.Element = et.Element('RazrChange')
    result.set('date', date.strftime('%Y-%m-%d'))
    with BaseIFace() as base:
        dt_load = Helper.getDate(date, base.loadRateDates())
        rch = base.loadRazrChange(dt_load)
        for player in rch:
            result.append(player.xml)
    return result
