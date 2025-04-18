import lxml.etree as et
import datetime
import os
from src.helper import Helper
from typing import List, Optional
from collections import OrderedDict


class PlayingRecord:
    allowed_fields = ['id', 'date', 'name', 'partner', 'placel', 'placeh', 'pb', 'ro', 'mb', 'champ_t', 'type']

    def __init__(self, **kwargs):
        self.id = None
        self.date = None
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
        elif (13 <= self.champ_t <= 14) and self.placeh <= 3: #ЖЧР и ЮЧР не набравшие 16 участников
            result = True
        elif (20 <= self.champ_t <= 29) and self.placeh <= 3:  # Малый чемпионат России, призовое место
            result = True
        elif self.champ_t == 31 and self.placeh <= 3:  # КЧР, места 1 - 5
            result = True
        elif (self.champ_t == 32 or self.champ_t == 33) and self.placeh <= 3:  # ПЧР или ПЧР-ИМП, места 1-10
            result = True
        elif (90 <= self.champ_t < 100) and self.placeh <= 3:  # Неквалифицируемые чемпионаты Европы и Мира
            result = True
        elif (40 <= self.champ_t < 100) and self.type == 2 and self.placeh <= 10:
            # Парный чемпионат Европы или Мира, места 1-10
            result = True
        elif (40 <= self.champ_t < 100) and self.type == 3 and self.placeh <= 8:
            # Командный чемпионат Европы или Мира, места 1-8
            result = True
        return result

    @property
    def xml(self) -> et.Element:
        tournament = et.Element('tournament')
        tournament.set('id', str(self.id))
        if self.achievement:
            tournament.set('achievement', '1')

        tid = et.SubElement(tournament, 'id')
        tid.text = str(self.id)
        tyear = et.SubElement(tournament, 'year')
        tyear.text = str(self.date.year)
        tdate = et.SubElement(tournament, 'date')
        tdate.text = str(self.date)

        tname = et.SubElement(tournament, 'name')
        tname.text = str(self.name)
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
                      'razr', 'razr_temp', 'pb', 'rate', 'rate_rank', 'mb', 'emb', 'state', 'quest', 'lifetime',
                      'best_rate', 'best_rate_dt', 'best_rank', 'best_rank_dt', 'is_sputnik', 'sputnik_first' ]

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
        self.categories = ['O']
        self.state = None
        self.club_stat = []
        self.quest: bool = False
        self.lifetime = None

        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)
        if self.firstname == 'Щ' or self.firstname is None:
            self.firstname = ''
        if self.fathername == 'Щ' or self.firstname is None:
            self.fathername = ''
        # TODO categories definition duplicates with RateRecord
        # Move it to separate function
        if self.sex == 0:
            self.categories.append('W')
        try:
            if hasattr(self.birthdate, "year") :
                age = datetime.date.today().year - self.birthdate.year
                if age < 26:
                    self.categories.append('J')
                    self.isJ = True
                if age >= 63:
                    # This age should be reviewed later according to EBL policies.
                    # See SCoC for current european Championship
                    # http://www.eurobridge.org/wp-content/uploads/2017/10/EBL-info-corrective-letter-Senior-Age-121017.pdf
                    self.categories.append('S')
                    self.isS = True
        except AttributeError:
            pass

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

    def addClubStatRecord(self, record: dict):
        self.club_stat.append(record)

    @property
    def xml(self) -> et.Element:
        isDead = self.state == 3
        player_record = et.Element('player')
        player_record.set('id', str(self.id))
        if self.id:
            info = et.SubElement(player_record, 'info')
            for field in ['lastname', 'firstname', 'fathername', 'city']:
                if field in self.__dict__:
                    locals()[field] = et.SubElement(info, field)
                    locals()[field].text = self.__dict__[field]
            if self.mail and not isDead:
                mail = et.SubElement(info, 'mail')
                mail.text = self.mail
            if self.club_id:
                club = et.SubElement(info, "club")
                club.set('id', str(self.club_id))
            # if hasattr(self.birthdate, "strftime"):
            #     birthdate = et.SubElement(info, 'birthdate')
            #     birthdate.text = self.birthdate.strftime("%Y-%m-%d")
            photo_url = f'foto/{self.id}.jpg'
            if os.path.exists('src/static/' + photo_url) and os.path.isfile('src/static/' + photo_url) \
                    and not os.path.islink('src/static/' + photo_url):
                photo = et.SubElement(info, 'photo')
                photo.set('url', 'https://db.bridgesport.ru/' + photo_url)
            if self.quest:
                player_record.set('quest', '1')
            elif not isDead:
                player_record.set('quest', '0')
            if self.lifetime is not None:
                lifetime = et.SubElement(info, 'lifetime')
                lifetime.text = self.lifetime
            if isDead:
                player_record.set('died', '1')
            elif self.state == 5:
                 player_record.set('hidden', '1')
            else:
                categories = et.SubElement(info, 'categories')
                for cat in self.categories:
                    category = et.SubElement(categories, 'category')
                    category.text = cat


            sportlevel = et.SubElement(player_record, 'sportlevel')
            razr = et.SubElement(sportlevel, 'razr')
            razr.text = str(self.razr)
            pb = et.SubElement(sportlevel, 'pb')
            pb.text = str(self.pb)
            if not isDead:
                rate = et.SubElement(sportlevel, 'rate')
                rate.text = str(self.rate)

            mb = et.SubElement(sportlevel, 'mb')
            mb.text = str(self.mb + (self.emb if self.emb else 0))
            if self.emb:
                emb = et.SubElement(sportlevel, 'emb')
                emb.text = str(self.emb)
                if self.mb < self.emb * 2:
                    cmd = et.SubElement(sportlevel, 'cmb')
                    cmd.text = str(self.mb + round( float( self.mb )/2 - 0.01))
                    pass

            if self.razr_temp:
                locals()['razr'].set('temp', '1')

            rstat = et.SubElement(player_record, 'stat')
            if not isDead:
                position = et.SubElement(rstat, 'RateRank')
                if self.rate_rank:
                    position.text = str(self.rate_rank)
                else:
                    position.text = "-"
            if not isDead or self.best_rank:
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
            if self.club_stat:
                pass
                clubStat = et.SubElement(player_record, 'clubMbStatistics')
                for rec in self.club_stat:
                    statRecord = et.SubElement(clubStat, 'record')
                    statDate = et.SubElement(statRecord, 'date')
                    #statDate.text = str(rec['date'])
                    statDate.text = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                                     'Июль', 'Август', 'Сентябрь','Октябрь', 'Ноябрь', 'Декабрь',][rec['date'].month-1] + \
                        ' ' + str(rec['date'].year)
                    statName = et.SubElement(statRecord, 'name')
                    statName.text = str(rec['name'])
                    if(rec['mb']):
                        statMB = et.SubElement(statRecord, 'mb')
                        statMB.text = str(rec['mb'])
                    if (rec['emb']):
                        statEMB = et.SubElement(statRecord, 'emb')
                        statEMB.text = str(rec['emb'])

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
            result['id'] = self.id
            result['name'] = name
            result['city'] = self.city
            result['razr'] = self.razr
            result['rate'] = self.rate
            result['categories'] = self.categories
            photo_url = f'foto/{self.id}.jpg'
            if os.path.exists('src/static/' + photo_url) and os.path.isfile('src/static/' + photo_url) \
                and not os.path.islink('src/static/' + photo_url):
                result['photo'] = 'https://db.bridgesport.ru/' + photo_url
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
        result.text = "{0:.2f}".format(self.result)

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
    allowed_fields = ['id', 'type', 'name', 'start', 'end', 'city', 'family', 'is_show', 'prev', 'next']
    types = {1: "Individual", 2: "Pair", 3: "Team", 4: "Session", 5: "Club", 6: "Festival"}

    def __init__(self, **kwargs):
        self.id = None
        self.type = None
        self.name = None
        self.start = None
        self.end = None
        self.city = None
        self.ancestors = None
        self.family = None
        self.nested = []
        self.participants = []
        self.is_show: Optional[bool] = None
        self.prev = None
        self.next = None
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
            ancestor_level: int = 0
            for ancestor in self.ancestors:
                parent = et.SubElement(tournament, 'parent'+(str(ancestor_level) if ancestor_level else ''))
                parent.set('id', str(ancestor['id']))
                if ancestor['family']:
                    parent.set('family', str(ancestor['family']))
                parent.text = ancestor['name']
                ancestor_level +=1
            info = et.SubElement(tournament, 'info')
            for field in ['name', 'city', 'start', 'end']:
                locals()[field] = et.SubElement(info, field)
                locals()[field].text = str(self.__dict__[field])
            if self.prev or self.next:
                navigation = et.SubElement(tournament, 'navigation')
                if self.prev:
                    navigation.set('prev', str(self.prev))
                if self.next:
                    navigation.set('next', str(self.next))
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
        if self.ancestors and self.ancestors[0]['parent_id']:
            result.set('parent', str(self.ancestors[0]['parent_id']))
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
                      'razr', 'razr_temp', 'pb', 'rate', 'mb', 'emb', 'state']

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
        self.state = None
        self.quest = False
        self.mail = None
        self.mbstat = None
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)
        if (self.firstname == 'Щ') or (self.firstname is None):
            self.firstname = ''
        if (self.fathername == 'Щ') or (self.firstname is None):
            self.fathername = ''
        self.shortname = '{0} {1}.{2}.'.format(self.lastname,
                                              (self.firstname[0] if  self.firstname else ''),
                                              (self.fathername[0] if self.fathername else ''))
        if 'sex' in kwargs and kwargs['sex'] == 0:
            self.categories.append('W')
            self.isW = True

        if 'birthdate' in kwargs and hasattr(kwargs['birthdate'], 'year'):  # birthdate is valid date
            # TODO Replace today with actual date
            age = datetime.date.today().year - kwargs['birthdate'].year
            if age < 26:
                self.categories.append('J')
                self.isJ = True
            if age >= 62:
                # This age should be reviewed later according to EBL policies.
                # See SCoC for current european Championship
                # http://www.eurobridge.org/wp-content/uploads/2017/10/EBL-info-corrective-letter-Senior-Age-121017.pdf
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
        fathername.text = self.fathername if self.fathername else ''
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
        if self.mbstat:
            mbstat = et.SubElement(result, 'mbstat')
            for period in self.mbstat:
                el = et.SubElement(mbstat, period)
                el.text = str(self.mbstat[period])

        if self.state == 3:
            result.set('died', '1')
        else:
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
            ('C', 1 if self.isS else ''),
            ('Анкета', self.quest),
            ('e-mail', self.mail)])


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
        result.set('tourn', str(self.tourn_name).replace('"', '&quot;'))
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
