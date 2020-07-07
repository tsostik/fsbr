import lxml.etree as et
import datetime
import os
from src.helper import Helper
from typing import List, Optional
from collections import OrderedDict


class PlayingRecord:
    allowed_fields = ['id', 'year', 'name', 'partner', 'placel', 'placeh', 'pb', 'ro', 'mb', 'champ_t', 'type']

    def __init__(self, **kwargs):
        self.id = None
        self.year = None
        self.name = None
        self.partner = None
        self.placel = None
        self.placeh = None
        self.pb = None
        self.ro = None
        self.mb = None
        self.champ_t = None
        self.type = 0
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)

    @property
    def achievement(self):
        """
        :rtype: Bool
        """
        result = False
        if self.champ_t == 3 and self.placeh <= 3:  # "Прочий" чемпионат, призовое место
            result = True
        elif self.champ_t <= 10:
            pass
        elif self.champ_t > 1000 and self.placeh <= 3:  # Региональный чемпионат, призовое место
            result = True
        elif (20 <= self.champ_t <= 29) and self.placeh <= 3:  # Малый чемпионат России, призовое место
            result = True
        elif self.champ_t == 31 and self.placeh <= 3:  # КЧР, места 1 - 5
            result = True
        elif (self.champ_t == 32 or self.champ_t == 33) and self.placeh <= 3:  # ПЧР или ПЧР-ИМП, места 1-10
            result = True
        elif (90 <= self.champ_t < 100) and self.placeh <= 3:  # Неквалифицируемые чемпионаты Европы и Мира
            result = True
        elif (40 <= self.champ_t < 100) and self.type == 2 and self.placeh <= 3:
            # Парный чемпионат Европы или Мира, места 1-10
            result = True
        elif (40 <= self.champ_t < 100) and self.type == 3 and self.placeh <= 3:
            # Командный чемпионат Европы или Мира, места 1-8
            result = True
        return result

    @property
    def xml(self) -> et.Element:
        tournament = et.Element('tournament')
        tournament.set('id', str(self.id))
        if self.achievement:
            tournament.set('achievement', '1')

        for field in ['id', 'year', 'name']:
            locals()[field] = et.SubElement(tournament, field)
            locals()[field].text = str(self.__dict__[field])
        for field in ['pb', 'ro', 'mb']:
            if self.__dict__[field]:
                locals()[field] = et.SubElement(tournament, field)
                locals()[field].text = str(self.__dict__[field])

        place_str = str(self.placeh) if self.placeh == self.placel else str(self.placeh) + ' - ' + str(self.placel)
        place = et.SubElement(tournament, 'place')
        place.text = place_str
        partner = et.SubElement(tournament, 'partner')
        if self.partner is None:
            partner.text = ""
        elif type(self.partner) is tuple:
            player = et.SubElement(partner, 'player')
            player.text = self.partner[0]
            player.set('id', str(self.partner[1]))
        else:
            team = et.SubElement(partner, 'team')
            team.set('name', str(self.partner[0]))
            for pl in self.partner[1]:
                player = et.SubElement(team, 'player')
                player.text = pl[0]
                player.set('id', str(pl[1]))
        return tournament


class OtherPos:
    # "Other event" position for one player
    allowed_fields = ['id', 'year', 'event', 'title']

    def __init__(self, **kwargs):
        self.id = None
        self.year = None
        self.event = None
        self.title = None
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)

    @property
    def xml(self) -> et.Element:
        record = et.Element('record')
        for field in ['year', 'event', 'title']:
            locals()[field] = et.SubElement(record, field)
            locals()[field].text = str(self.__dict__[field])
        locals()['event'].set('id', str(self.id))
        return record


class TdPos:
    # Directing position for one player
    allowed_fields = ['id', 'tournament', 'date', 'title']

    def __init__(self, **kwargs):
        self.id = None
        self.tournament = None
        self.date = None
        self.title = None
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)

    @property
    def xml(self) -> et.Element:
        position = et.Element('position')
        for field in ['tournament', 'date', 'title']:
            locals()[field] = et.SubElement(position, field)
            locals()[field].text = str(self.__dict__[field])
        locals()['tournament'].set('id', str(self.id))
        return position


class AdminPos:
    # Administrative position for one player
    allowed_fields = ['since', 'till', 'committee', 'title']

    def __init__(self, **kwargs):
        self.since = None
        self.till = None
        self.comitee = None
        self.title = None
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)

    @property
    def xml(self) -> et.Element:
        position = et.Element('position')
        for field in self.allowed_fields:
            if self.__dict__[field] is not None and self.__dict__[field] != 0 and self.__dict__[field] != "":
                locals()[field] = et.SubElement(position, field)
                locals()[field].text = str(self.__dict__[field])
        return position


class Player:
    # Full data for player history
    allowed_fields = ['id', 'lastname', 'firstname', 'fathername', 'birthdate', 'sex', 'city', 'mail', 'club_id',
                      'razr', 'razr_temp', 'pb', 'rate', 'rate_rank', 'mb', 'emb',
                      'best_rate', 'best_rate_dt', 'best_rank', 'best_rank_dt', 'is_sputnik', 'sputnik_first']

    def __init__(self, **kwargs):
        self.id = None
        self.lastname = None
        self.firstname = None
        self.fathername = None
        self.sex = None
        self.birthdate = None
        self.city = None
        self.club_id = None
        self.razr = None
        self.razr_temp = False
        self.pb = None
        self.rate = None
        self.mb = None
        self.emb = None
        self.positions = []
        self.directing = []
        self.results = []
        self.other = []
        self.wbf_id = None
        self.acbl_id = None
        self.gambler_nick = None
        self.bbo_nick = None
        self.rate_rank = None
        self.best_rate = None
        self.best_rate_dt = None
        self.best_rank = None
        self.best_rank_dt = None
        self.is_sputnik: bool = False
        self.sputnik_first = None

        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)
        if self.firstname == 'Щ':
            self.firstname = ''
        if self.fathername == 'Щ':
            self.fathername = ''

    def addPosition(self, position):
        """
        :type position: AdminPos
        """
        self.positions.append(position)

    def addDirecting(self, position):
        """
        :type position: TdPos
        """
        self.directing.append(position)

    def addResult(self, result):
        """
        :type result: PlayingRecord
        """
        self.results.append(result)

    def addOther(self, record):
        """
        :type record: OtherPos
        """
        self.other.append(record)

    def setExternalIds(self, wbf_id, acbl_id, gambler_nick, bbo_nick):
        """
        :type wbf_id: int
        :type acbl_id: int
        :type gambler_nick:
        :type bbo_nick: str
        """
        self.wbf_id = wbf_id
        self.acbl_id = acbl_id
        if isinstance(gambler_nick, str):
            self.gambler_nick = gambler_nick.split(",")
        self.bbo_nick = bbo_nick

    def setRateStat(self, best_rate, best_rate_date, best_rank, best_rank_date):
        self.best_rate = best_rate
        self.best_rate_dt = best_rate_date
        self.best_rank = best_rank
        self.best_rank_dt = best_rank_date

    @property
    def xml(self) -> et.Element:
        player_record = et.Element('player')
        player_record.set('id', str(self.id))
        if self.id:
            info = et.SubElement(player_record, 'info')
            for field in ['lastname', 'firstname', 'fathername', 'city', 'mail']:
                if field in self.__dict__:
                    locals()[field] = et.SubElement(info, field)
                    locals()[field].text = self.__dict__[field]
            if self.club_id:
                club = et.SubElement(info, "club")
                club.set('id', str(self.club_id))
            # if hasattr(self.birthdate, "strftime"):
            #     birthdate = et.SubElement(info, 'birthdate')
            #     birthdate.text = self.birthdate.strftime("%Y-%m-%d")
            photo_url = f'foto/{self.id}.jpg'
            if os.path.exists('src/static/' + photo_url) and os.path.isfile('src/static/' + photo_url):
                photo = et.SubElement(info, 'photo')
                photo.set('url', 'https://db.bridgesport.ru/' + photo_url)

            sportlevel = et.SubElement(player_record, 'sportlevel')
            for field in ['razr', 'pb', 'rate']:
                locals()[field] = et.SubElement(sportlevel, field)
                locals()[field].text = str(self.__dict__[field])

            mb = et.SubElement(sportlevel, 'mb')
            mb.text = str(self.mb + (self.emb if self.emb else 0))
            if self.emb:
                emb = et.SubElement(sportlevel, 'emb')
                emb.text = str(self.emb)

            if self.razr_temp:
                locals()['razr'].set('temp', '1')

            rstat = et.SubElement(player_record, 'stat')
            position = et.SubElement(rstat, 'RateRank')
            if self.rate_rank:
                position.text = str(self.rate_rank)
            else:
                position.text = "-"
            bestpos = et.SubElement(rstat, 'BestRateRank')
            bestrate = et.SubElement(rstat, 'BestRate')
            if self.best_rank:
                bestpos.set('date', self.best_rank_dt.strftime("%Y-%m-%d"))
                bestpos.text = str(self.best_rank)
                bestrate.set('date', self.best_rate_dt.strftime("%Y-%m-%d"))
                bestrate.text = str(self.best_rate)
            else:
                bestpos.text = "-"
                bestrate.text = "-"

            if self.wbf_id or self.acbl_id or self.gambler_nick or self.bbo_nick:
                ext = et.SubElement(player_record, 'IDs')
                if self.wbf_id:
                    wbf = et.SubElement(ext, "WBF")
                    wbf.set('id', str(self.wbf_id))
                if self.acbl_id:
                    acbl = et.SubElement(ext, "ACBL")
                    acbl.set('id', str(self.acbl_id))
                if self.gambler_nick:
                    gambler = et.SubElement(ext, "Gambler")
                    for nick in self.gambler_nick:
                        gamblernick = et.SubElement(gambler, 'nick')
                        gamblernick.text = str(nick)
                if self.bbo_nick:
                    bbo = et.SubElement(ext, "BBO")
                    bbonick = et.SubElement(bbo, 'nick')
                    bbonick.text = str(self.bbo_nick)

            if self.results:
                results = et.SubElement(player_record, 'results')
                for rec in self.results:
                    if rec.placeh > 0:
                        results.append(rec.xml)

            if self.positions:
                admin = et.SubElement(player_record, 'administrative')
                for pos in self.positions:
                    admin.append(pos.xml)

            if self.directing:
                directing = et.SubElement(player_record, 'directing')
                for pos in self.directing:
                    directing.append(pos.xml)

            if self.other:
                other = et.SubElement(player_record, 'other')
                for pos in self.other:
                    other.append(pos.xml)
        else:
            player_record.text = "Player not found"
        return player_record

    @property
    def info(self):
        # short player info to show in hint
        result = {}
        if self.lastname:
            if (self.firstname and len(self.firstname) == 1) or (self.fathername and len(self.fathername) == 1):
                name = Helper.shortPlayerName(self.lastname, self.firstname, self.fathername)
            else:
                name = self.lastname + (' ' + self.firstname if self.firstname else '') + \
                       (' ' + self.fathername if self.fathername else '')
            result['name'] = name
            result['city'] = self.city
            result['razr'] = self.razr
            result['rate'] = self.rate
            photo_url = f'foto/{self.id}.jpg'
            if os.path.exists('src/static/' + photo_url) and os.path.isfile('src/static/' + photo_url):
                result['photo'] = 'http://bridgesport.ru/players/' + photo_url
        return result


class TournamentRecord:
    # Tournament record in player's history
    allowed_fields = ['placeh', 'placel', 'result', 'pb', 'ro', 'mb']

    def __init__(self, **kwargs):
        self.placeh = None
        self.placel = None
        self.result = None
        self.pb = None
        self.ro = None
        self.mb = None
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)

    @property
    def place(self):
        return str(self.placeh) if self.placeh == self.placel else "{0}-{1}".format(self.placeh, self.placel)

    @property
    def xml(self) -> et.Element:
        record = et.Element('record')
        result = et.SubElement(record, 'result')
        result.text = "{0}".format(self.result, '.2f')

        place = et.SubElement(record, 'place')
        place.text = self.place
        for field in ['pb', 'ro', 'mb']:
            if self.__dict__[field]:
                locals()[field] = et.SubElement(record, field)
                locals()[field].text = str(self.__dict__[field])
        return record


class TournamentRecordInd(TournamentRecord):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = kwargs['player']

    @property
    def xml(self) -> et.Element:
        result = super().xml
        participant = et.SubElement(result, 'participant')
        player = et.SubElement(participant, 'player')
        player.set('id', str(self.player[1]))
        player.text = self.player[0]
        return result


class TournamentRecordPair(TournamentRecord):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player1 = kwargs['player1']
        self.player2 = kwargs['player2']

    @property
    def xml(self) -> et.Element:
        result = super().xml
        participant = et.SubElement(result, 'participant')
        player1 = et.SubElement(participant, 'player')
        player1.set('id', str(self.player1[1]))
        player1.text = self.player1[0]
        player2 = et.SubElement(participant, 'player')
        player2.set('id', str(self.player2[1]))
        player2.text = self.player2[0]
        return result


class TournamentRecordTeam(TournamentRecord):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.team = kwargs['team']
        self.players = kwargs['players']
        if 'players_nq' in kwargs:
            self.players_nq = kwargs['players_nq']
        else:
            self.players_nq = []

    @property
    def xml(self) -> et.Element:
        result = super().xml
        team = et.SubElement(result, 'team')
        team.set('name', self.team)
        for pl in self.players:
            player = et.SubElement(team, 'player')
            player.set('id', str(pl[1]))
            player.text = pl[0]
        for pl in self.players_nq:
            player = et.SubElement(team, 'player')
            player.set('qualified', "0")
            player.set('id', str(pl[1]))
            player.text = pl[0]
        return result


class Tournament:
    # Full data of a tournament result
    allowed_fields = ['id', 'type', 'name', 'start', 'end', 'city', 'parent_id', 'family', 'is_show']
    types = {1: "Individual", 2: "Pair", 3: "Team", 4: "Session", 5: "Club", 6: "Festival"}

    def __init__(self, **kwargs):
        self.id = None
        self.type = None
        self.name = None
        self.start = None
        self.end = None
        self.city = None
        self.parent_id = None
        self.parent_name = None
        self.family = None
        self.nested = []
        self.participants = []
        self.is_show: Optional[bool] = None
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)

    def addParticipant(self, participant: TournamentRecord):
        self.participants.append(participant)

    @property
    def xml(self) -> et.Element:
        tournament = et.Element('tournament')
        tournament.set('id', str(self.id))
        if self.id:
            tournament.set('type', self.types[self.type])
            if self.family:
                tournament.set('family', str(self.family))
            if self.is_show:
                tournament.set('show', "1")
            if self.nested:
                nested = et.SubElement(tournament, 'nested')
                for child in self.nested:
                    nested_tournament = et.SubElement(nested, 'tournament')
                    nested_tournament.set('id', str(child.id))
                    nested_tournament.text = str(child.name)
            if self.parent_id:
                parent = et.SubElement(tournament, 'parent')
                parent.set('id', str(self.parent_id))
                parent.text = self.parent_name
            info = et.SubElement(tournament, 'info')
            for field in ['name', 'city', 'start', 'end']:
                locals()[field] = et.SubElement(info, field)
                locals()[field].text = str(self.__dict__[field])
            if self.participants:
                participants = et.SubElement(tournament, 'participants')
                for part in self.participants:
                    participants.append(part.xml)
        else:
            tournament.text = "Tournament not found"
        return tournament

    @property
    def xmlShort(self) -> et.Element:
        result = et.Element('tournament')
        result.set('id', str(self.id))
        if self.parent_id:
            result.set('parent', str(self.parent_id))
        if self.family:
            result.set('family', str(self.family))
        if self.is_show:
            result.set('show', "1")
        if self.id:
            for field in ['name', 'city', 'start', 'end']:
                locals()[field] = et.SubElement(result, field)
                locals()[field].text = str(self.__dict__[field])
        else:
            result.text = "Tournament not found"
        return result


class RateRecord:
    # One record in full list or rate list
    allowed_fields = ['id', 'lastname', 'firstname', 'fathername', 'city', 'club_id',
                      'razr', 'razr_temp', 'pb', 'rate', 'mb', 'emb']

    def __init__(self, **kwargs):
        self.id = None
        self.lastname = ''
        self.firstname = ''
        self.fathername = ''
        self.city = ''
        self.club_id = None
        self.razr = None
        self.razr_temp = False
        self.pb = 0
        self.rate = 0
        self.mb = 0
        self.emb = 0
        self.categories = ['O']
        self.isW = False
        self.isJ = False
        self.isS = False
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)
        if self.firstname == 'Щ':
            self.firstname = ''
        if self.fathername == 'Щ':
            self.fathername = ''
        self.shortname = '{0} {1}.{2}.'.format(self.lastname,
                                               (self.firstname[0] if len(self.firstname) > 0 else ''),
                                               (self.fathername[0] if len(self.fathername) > 0 else ''))
        if 'sex' in kwargs and kwargs['sex'] == 0:
            self.categories.append('W')
            self.isW = True

        if 'birthdate' in kwargs and hasattr(kwargs['birthdate'], 'year'):  # birthdate is valid date
            # TODO Replace today with actual date
            age = datetime.date.today().year - kwargs['birthdate'].year
            if age < 26:
                self.categories.append('J')
                self.isJ = True
            if age >= 61:
                # This age should be revisited later according to EBL policies.
                # See SCoC for current european Championship
                self.categories.append('S')
                self.isS = True

    @property
    def xmlFullList(self) -> et.Element:
        result = et.Element('player')
        result.set('id', str(self.id))
        lastname = et.SubElement(result, 'lastname')
        lastname.text = self.lastname
        firstname = et.SubElement(result, 'firstname')
        firstname.text = self.firstname
        fathername = et.SubElement(result, 'fathername')
        fathername.text = self.fathername
        city = et.SubElement(result, 'city')
        city.text = self.city
        if self.club_id:
            club = et.SubElement(result, "club")
            club.set('id', str(self.club_id))
        razr = et.SubElement(result, 'razr')
        razr.text = str(self.razr)
        if self.razr_temp:
            razr.set('temp', '1')
        mb = et.SubElement(result, 'mb')
        mb.text = str(self.mb + (self.emb if self.emb else 0))
        emb = et.SubElement(result, 'emb')
        emb.text = str(self.emb)
        pb = et.SubElement(result, 'pb')
        pb.text = str(self.pb)
        rate = et.SubElement(result, 'rate')
        rate.text = str(self.rate)
        return result

    @property
    def xmlRate(self) -> et.Element:
        result = et.Element('player')
        result.set('id', str(self.id))
        name = et.SubElement(result, 'name')
        name.text = self.shortname
        razr = et.SubElement(result, 'razr')
        razr.text = str(self.razr)
        if self.razr_temp:
            razr.set('temp', '1')
        city = et.SubElement(result, 'city')
        city.text = self.city
        if self.club_id:
            club = et.SubElement(result, "club")
            club.set('id', str(self.club_id))
        rate = et.SubElement(result, 'rate')
        rate.text = str(self.rate)
        pb = et.SubElement(result, 'pb')
        pb.text = str(self.pb)
        categories = et.SubElement(result, 'categories')
        for cat in self.categories:
            category = et.SubElement(categories, 'category')
            category.text = cat
        return result

    @property
    def xlRecord(self) -> OrderedDict:
        if self.id == 1936:
            pass
        return OrderedDict([
                ('id', self.id),
                ('Фамилия', self.lastname),
                ('Имя', self.firstname),
                ('Отчество', self.fathername),
                ('Город', self.city),
                ('Разряд', self.razr),
                ('МБ', (self.mb or 0) + (self.emb or 0)),
                ('ПБ', self.pb),
                ('Рейтинг', self.rate),
                ('*', '*' if self.razr_temp else ''),
                ('Клуб', self.club_id),
                ('Ж', 1 if self.isW else ''),
                ('Ю', 1 if self.isJ else ''),
                ('C', 1 if self.isS else '')])


class RateForecastTournRecord:
    def __init__(self, ro: int, tourn_id: int, tourn_name: str, is_of: bool):
        self.ro: int = ro
        self.tourn_id: int = tourn_id
        self.tourn_name: str = tourn_name
        self.is_of: bool = is_of

    @property
    def xml(self):
        result = et.Element('record')
        result.text = str(self.ro)
        result.set('tourn_id', str(self.tourn_id))
        result.set('tourn', self.tourn_name)
        if self.is_of:
            result.set('official', '1')
        return result


class RateForecastRecord:
    # One player record in rate forecast
    allowed_fields = ['player_id', 'lastname', 'firstname', 'fathername', 'city']

    def __init__(self, **kwargs):
        self.player_id: int = 0
        self.lastname: str = ''
        self.firstname: str = ''
        self.fathername: str = ''
        self.city: str = ''
        self.rate: int = 0
        self.rate_records: List[RateForecastTournRecord] = []
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)

    def addRecord(self, ro: int, tourn_id: int, tourn_name: str, is_of: bool):
        self.rate_records.append(RateForecastTournRecord(ro, tourn_id, tourn_name, is_of))

    @property
    def xml(self):
        result = et.Element('player')
        result.set('id', str(self.player_id))
        result.set('name', Helper.shortPlayerName(self.lastname, self.firstname, self.fathername))
        result.set('city', self.city)
        result.set('rate', str(self.rate))
        for rateRec in self.rate_records:
            result.append(rateRec.xml)
        return result
