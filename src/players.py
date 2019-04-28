from src.db import *


def getPlayerXml(player_id):
    with BaseIFace() as base:
        player = base.loadPlayerData(player_id)
        base.loadPlayingRecords(player)
        base.loadAdminPos(player)
        base.loadDirecting(player)
    return player.xml


"""    
    players = base.loadPlayers()
    answer = ET.Element("players")
    for id, player in players.items():
        answer.append(player.xml() )
    ET.ElementTree(answer).write('d:\\test.xml', encoding='UTF-8', xml_declaration=True, pretty_print=True)
    return "done"
"""
