import lxml.etree as ET


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
        if self.champ_t <= 10 and self.champ_t != 3:
            pass
        elif self.champ_t > 1000 and self.placeh <= 3:  # Региональный чемпионат, призовое место
            result = True
        elif self.champ_t <= 29 and self.placeh <= 3:  # Малый чемпионат России, призовое место
            result = True
        elif self.champ_t == 31 and self.placeh <= 5:  # КЧР, места 1 - 5
            result = True
        elif (self.champ_t == 32 or self.champ_t == 33) and self.placeh <= 10:  # ПЧР или ПЧР-ИМП, места 1-10
            result = True
        elif (40 <= self.champ_t < 100) and self.type == 2 and self.placeh <= 10:  # Парный чемпионат Европы или Мира, места 1-10
            result = True
        elif (40 <= self.champ_t < 100) and self.type == 3 and self.placeh <= 8:  # Командный чемпионат Европы или Мира, места 1-10
            result = True
        return result

    @property
    def xml(self):
        """
        :rtype: ET.Element
        """
        tournament = ET.Element('tournament')
        tournament.set('id', str(self.id))
        if self.achievement:
            tournament.set('achievement', '1')

        for field in ['id', 'year', 'name']:
            locals()[field] = ET.SubElement(tournament, field)
            locals()[field].text = str(self.__dict__[field])
        for field in ['pb', 'ro', 'mb']:
            if self.__dict__[field]:
                locals()[field] = ET.SubElement(tournament, field)
                locals()[field].text = str(self.__dict__[field])

        place_str = str(self.placeh) if self.placeh == self.placel else str(self.placeh) + ' - ' + str(self.placel)
        place = ET.SubElement(tournament, 'place')
        place.text = place_str
        partner = ET.SubElement(tournament, 'partner')
        if self.partner is None:
            partner.text = ""
        elif type(self.partner) is tuple:
            player = ET.SubElement(partner, 'player')
            player.text = self.partner[0]
            player.set('id', str(self.partner[1]))
        else:
            team = ET.SubElement(partner, 'team')
            team.text = str(self.partner[0])
            for pl in self.partner[1]:
                player = ET.SubElement(team, 'player')
                player.text = pl[0]
                player.set('id', str(pl[1]))
        return tournament


class OtherPos:
    allowed_fields = ['id', 'year', 'event', 'title']

    def __init__(self, **kwargs):
        self.id = None
        self.year = None
        self.event = None
        self.title = None
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)

    @property
    def xml(self):
        """
        :rtype: ET.Element
        """
        record = ET.Element('record')
        for field in ['year', 'event', 'title']:
            locals()[field] = ET.SubElement(record, field)
            locals()[field].text = str(self.__dict__[field])
        locals()['event'].set('id', str(self.id))
        return record


class TdPos:
    allowed_fields = ['id', 'tournament', 'date', 'title']

    def __init__(self, **kwargs):
        self.id = None
        self.tournament = None
        self.date = None
        self.title = None
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)

    @property
    def xml(self):
        """
        :rtype: ET.Element
        """
        position = ET.Element('position')
        for field in ['tournament', 'date', 'title']:
            locals()[field] = ET.SubElement(position, field)
            locals()[field].text = str(self.__dict__[field])
        locals()['tournament'].set('id', str(self.id))
        return position


class AdminPos:
    allowed_fields = ['since', 'till', 'committee', 'title']

    def __init__(self, **kwargs):
        self.since = None
        self.till = None
        self.comitee = None
        self.title = None
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)

    @property
    def xml(self):
        """
        :rtype: ET.Element
        """
        position = ET.Element('position')
        for field in self.allowed_fields:
            if self.__dict__[field] is not None and self.__dict__[field] != 0 and self.__dict__[field] != "":
                locals()[field] = ET.SubElement(position, field)
                locals()[field].text = str(self.__dict__[field])
        return position


class Player:
    allowed_fields = ['id', 'lastname', 'firstname', 'fathername', 'birthdate', 'city', 'mail',
                      'razr', 'razr_temp', 'pb', 'rate', 'mb']

    def __init__(self, **kwargs):
        self.id = None
        self.lastname = None
        self.firstname = None
        self.fathername = None
        self.birthdate = None
        self.city = None
        self.razr = None
        self.razr_temp = False
        self.pb = None
        self.rate = None
        self.mb = None
        self.positions = []
        self.directing = []
        self.results = []
        self.other = []
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

    @property
    def xml(self):
        """
        :rtype: ET.Element
        """
        player_record = ET.Element('player')
        player_record.set('id', str(self.id))

        info = ET.SubElement(player_record, 'info')
        for field in ['lastname', 'firstname', 'fathername', 'city', 'mail']:
            locals()[field] = ET.SubElement(info, field)
            locals()[field].text = self.__dict__[field]
        if hasattr(self.birthdate, "strftime"):
            birthdate = ET.SubElement(info, 'birthdate')
            birthdate.text = self.birthdate.strftime("%Y-%m-%d")

        sportlevel = ET.SubElement(player_record, 'sportlevel')
        for field in ['razr', 'pb', 'rate', 'mb']:
            locals()[field] = ET.SubElement(sportlevel, field)
            locals()[field].text = str(self.__dict__[field])
        if self.razr_temp:
            locals()['razr'].set('temp', '1')

        if self.results:
            results = ET.SubElement(player_record, 'results')
            for rec in self.results:
                results.append(rec.xml)

        if self.positions:
            admin = ET.SubElement(player_record, 'administrative')
            for pos in self.positions:
                admin.append(pos.xml)

        if self.directing:
            directing = ET.SubElement(player_record, 'directing')
            for pos in self.directing:
                directing.append(pos.xml)

        if self.other:
            other = ET.SubElement(player_record, 'other')
            for pos in self.other:
                other.append(pos.xml)

        return player_record


class TournamentRecord:
    allowed_fields = ['placeh', 'placel', 'result', 'pb', 'ro', 'mb']

    def __init__(self, **kwargs):
        self.placeh = None
        self.placel = None
        self.result = None
        self.pb = None
        self.ro = None
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)
        self.mb = None

    @property
    def place(self):
        return str(self.placeh) if self.placeh == self.placel else "{0}-{1}".format(self.placeh, self.placel)

    @property
    def xml(self):
        """
        :rtype: ET.Element
        """
        record = ET.Element('record')
        result = ET.SubElement(record, 'result')
        result.text = "{0}".format(self.result, '.2f')

        place = ET.SubElement(record, 'place')
        place.text = self.place
        for field in ['pb', 'ro', 'mb']:
            if self.__dict__[field]:
                locals()[field] = ET.SubElement(record, field)
                locals()[field].text = str(self.__dict__[field])
        return record


class TournamentRecordInd(TournamentRecord):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = kwargs['player']

    @property
    def xml(self):
        """
        :rtype: ET.Element
        """
        record = super().xml
        participant = ET.SubElement(record, 'participant')
        player = ET.SubElement(participant, 'player')
        player.set('id', str(self.player[1]))
        player.text = self.player[0]
        return record


class Tournament:
    allowed_fields = ['id', 'type', 'name', 'start', 'end', 'city']
    types = {1: "Individual", 2: "Pair", 3: "Team", "4": "Session", 5: "Club", 6: "Festival"}

    def __init__(self, **kwargs):
        self.id = None
        self.type = None
        self.name = None
        self.start = None
        self.end = None
        self.city = None
        self.nested = []
        self.participants = []
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_fields)

    def addParticipant(self, participant):
        """
        :type participant: TournamentRecord
        """
        self.participants.append(participant)

    @property
    def xml(self):
        """
        :rtype: ET.Element
        """
        tournament = ET.Element('tournament')
        tournament.set('id', str(self.id))
        tournament.set('type', self.types[self.type])

        info = ET.SubElement(tournament, 'info')
        for field in ['name', 'city', 'start', 'end']:
            locals()[field] = ET.SubElement(info, field)
            locals()[field].text = str(self.__dict__[field])
        if self.participants:
            participants = ET.SubElement(tournament, 'participants')
            for part in self.participants:
                participants.append(part.xml)
        return tournament
