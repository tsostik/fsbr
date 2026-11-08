from src.db import BaseIFace
import lxml.etree as et


#XML представление одного турнира
def getTournamentXml(tournament_id):
    with BaseIFace() as base:
        tournament = base.loadTournamentData(tournament_id)
        if tournament.type == 1 or tournament.type == 5:
            base.loadIndividualParticipants(tournament)
        elif tournament.type == 2:
            base.loadPairParticipants(tournament)
        elif tournament.type == 3:
            base.loadTeamParticipants(tournament)
        elif tournament.type == 4:
            base.loadSessionParticipants(tournament)
    return tournament.xml


#Список всех турниров в базе
def getTournamentList():
    with BaseIFace() as base:
        result = et.Element('tournament_list')
        for tourn in base.loadTournList():
            result.append(tourn.xmlShort)
    return result

#Список существующих семей
def getFamiliesList(family_id):
    with BaseIFace() as base:
        result = et.Element('families')
        for family in base.loadFamilies(family_id):
            result.append(family.xml)
    return result
