import lxml.etree as et
import datetime
from src.helper import Helper


# various classes for requests


class RazrChange:
    def __init__(self, **kwargs):
        self.player_id: int = kwargs['player_id']
        self.player_name: str = Helper.shortPlayerName(kwargs['lastname'], kwargs['firstname'], kwargs['fathername'])
        self.old: str = Helper.getRazrStr(kwargs['old_razr'], kwargs['coeff'])
        self.new: str = Helper.getRazrStr(kwargs['new_razr'], kwargs['coeff'])

    @property
    def xml(self) -> et.Element:
        result = et.Element('player')
        result.set('id', str(self.player_id))
        result.set('name', self.player_name)
        result.set('old', self.old)
        result.set('new', self.new)
        return result


class ClubStat:
    def __init__(self):
        self.clubs = []

    def add(self, club_id: int, club: str,date: datetime.date):
        self.clubs.append({'club_id': club_id, 'club': club, 'date': date})

    @property
    def xml(self) -> et.Element:
        result = et.Element('ClubStat')
        for record in self.clubs:
            club = et.SubElement(result, 'club')
            club.set('id', str(record['club_id']))
            club.set('name', record['club'])
            club.set('date', str(record['date']))
        return result
