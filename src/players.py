from src.db import *
from src.forms import AddPlayer
from src.interface import Player
from flask_login import current_user


def getPlayerXml(player_id):
    with BaseIFace() as base:
        player = base.loadPlayerData(player_id)
        base.loadPlayingRecords(player)
        base.loadAdminPos(player)
        base.loadDirecting(player)
        base.loadOtherRecords(player)
        base.loadExternalIDs(player)
        base.loadRateStat(player)
    return player.xml


def findPlayer(name: str):
    with BaseIFace() as base:
        result = base.findPlayerByName(name)
    return result


def getPlayerInfoJSON(player_id: int):
    with BaseIFace() as base:
        player = base.loadPlayerData(player_id)
    return player.info


def addPlayer(player: AddPlayer) -> int:
    new_player = Player(firstname=player.firstname.data,
                        lastname=player.lastname.data,
                        fathername=player.fathername.data,
                        sex=player.sex.data,
                        birthdate=player.birthdate.data,
                        city=player.city.data,
                        is_sputnik=player.is_sputnik.data,
                        sputnik_first=player.sputnik_first.data)

    with BaseIFace() as base:
        plid = base.addNewPlayer(new_player, current_user.fsbr, player.notes.data)
    return plid


"""    
    players = base.loadPlayers()
    answer = ET.Element("players")
    for id, player in players.items():
        answer.append(player.xml() )
    ET.ElementTree(answer).write('d:\\test.xml', encoding='UTF-8', xml_declaration=True, pretty_print=True)
    return "done"
"""
