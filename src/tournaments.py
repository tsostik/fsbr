from src.db import *


def getTornamentXml(tournament_id):
    with BaseIFace() as base:
        tournament = base.loadTournamentData(tournament_id)
        if tournament.type == 1:
            base.loadIndividualParticipants(tournament)
        elif tournament.type == 2:
            base.loadPairParticipants(tournament)
    return tournament.xml
