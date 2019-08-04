from src.db import *


def getPlayerXml(player_id):
    with BaseIFace() as base:
        player = base.loadPlayerData(player_id)
        base.loadPlayingRecords(player)
        base.loadAdminPos(player)
        base.loadDirecting(player)
        base.loadOtherRecords(player)
        base.loadExternalIDs(player)
    return player.xml


def findPlayer(name: str):
    with BaseIFace() as base:
        result = base.findPlayerByName(name)
    return result


"""    
    players = base.loadPlayers()
    answer = ET.Element("players")
    for id, player in players.items():
        answer.append(player.xml() )
    ET.ElementTree(answer).write('d:\\test.xml', encoding='UTF-8', xml_declaration=True, pretty_print=True)
    return "done"
"""
