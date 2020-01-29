from typing import List
import lxml.etree as et


class RateRecord:
    # Represent a single player record in one tournament
    def __init__(self, player_id: int, name: str, placeh: int, placel: int, pb: int, ro: int):
        self.player_id: int = player_id
        self.name: str = name
        self.placeh: int = placeh
        self.placel: int = placel
        self.pb: int = pb
        self.ro: int = ro

    @property
    def placeStr(self) -> str:
        if self.placeh == self.placel:
            return str(self.placeh)
        return "{0}-{1}".format(self.placeh, self.placel)

    @property
    def xml(self) -> et.Element:
        record: et.Element = et.Element('record')
        record.set('place', self.placeStr)
        record.set('id', str(self.player_id))
        record.set('name', self.name)
        if self.pb > 0:
            record.set('pb', str(self.pb))
        if self.ro > 0:
            record.set('ro', str(self.ro))
        return record


class RateTourn:
    # Represent a single tournament in "rate tournaments" request
    def __init__(self, tourn_id: int, name: str):
        self.tourn_id: int = tourn_id
        self.name: str = name
        self.participants: List[RateRecord] = list()

    def addParticipant(self, player_id: int, name: str, placeh: int, placel: int, pb: int, ro: int):
        self.participants.append(RateRecord(player_id, name, placeh, placel, pb, ro))

    @property
    def xml(self) -> et.Element:
        tourn: et.Element = et.Element('tournament')
        tourn.set('id', str(self.tourn_id))
        tourn.set('name', self.name)
        for rec in self.participants:
            tourn.append(rec.xml)
        return tourn


class RateTournaments:
    # Full data for "rate tournaments request"
    def __init__(self, year: int):
        self.year: int = year
        self.tournaments: List[RateTourn] = list()

    def addRecord(self, tour_id: int, tourn_name: str,
                  player_id: int, name: str, placeh: int, placel: int, pb: int, ro: int):
        if len(self.tournaments) == 0 or self.tournaments[-1].tourn_id != tour_id:
            self.tournaments.append(RateTourn(tour_id, tourn_name))
        self.tournaments[-1].addParticipant(player_id, name, placeh, placel, pb, ro)

    @property
    def xml(self) -> et.Element:
        tournaments: et.Element = et.Element('Tournaments')
        tournaments.set('year', str(self.year))
        for rec in self.tournaments:
            tournaments.append(rec.xml)
        return tournaments
