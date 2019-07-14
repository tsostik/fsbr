from src.db import *
import lxml.etree as et


def getFullList():
    with BaseIFace() as base:
        pl_list = base.loadFullList()
        result = et.Element('FullList')
        # TODO: Add date
        for player in pl_list:
            result.append(player.xmlFullList)
    return result
