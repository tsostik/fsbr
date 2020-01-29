import pymysql.cursors
from src.interface import *
from src.queries import Queries
from src.helper import Helper
from src.RateTours import RateTournaments


class BaseIFace:
    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.connectToDb()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def connectToDb(self):
        self.conn = pymysql.connect(user='fsbr_plrs_python',
                                    host='localhost',
                                    password='fsbr_plrs_python',
                                    db='fsbr')

    def loadPlayerData(self, plid) -> Player:
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = Queries.select_player.format("player_id = {0}".format(plid))
            cursor.execute(sql)
            record = cursor.fetchone()
            if record:
                (razr, razr_temp) = Helper.getRazr(record['razr'], record['razr_coeff'])
                pl = Player(id=record['player_id'],
                            lastname=record['firstname'],
                            firstname=record['lastname'],
                            fathername=record['surname'],
                            birthdate=record['birthdate'],
                            city=record['city_name'],
                            mail=record['mail'],
                            razr=razr,
                            razr_temp=razr_temp,
                            rate=record['rate'],
                            rate_rank=record['place'],
                            pb=record['pb'],
                            mb=record['mb'],
                            emb=record['emb'])
            else:
                pl = Player()
        return pl

    def loadAdminPos(self, pl: Player):
        if pl.id:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = Queries.select_admin.format(pl.id)
                cursor.execute(sql)
                for pos in cursor.fetchall():
                    pl.addPosition(AdminPos(**pos))

    def loadDirecting(self, pl: Player):
        if pl.id:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = Queries.select_directing.format(pl.id)
                cursor.execute(sql)
                for pos in cursor.fetchall():
                    pl.addDirecting(TdPos(**pos))

    def loadOtherRecords(self, pl: Player):
        if pl.id:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = Queries.select_other.format(pl.id)
                cursor.execute(sql)
                for pos in cursor.fetchall():
                    pl.addOther(OtherPos(**pos))

    def loadPlayingRecords(self, pl: Player):
        if pl.id:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # Для ускорения последующей работы заранее загрузим данные о командах и партнерах
                # Парные турниры
                sql = \
                    "select tour_id, players.player_id as player_id, firstname, lastname, surname " \
                    "from (select tour_id, if(player1={0}, player2, player1) as player_id " \
                    "from tourn_pair " \
                    "where {0} in (player1, player2) ) as s_partner " \
                    "left join players using(player_id);".format(pl.id)
                cursor.execute(sql)
                parts_pair = {}
                for rec in cursor.fetchall():
                    parts_pair[rec['tour_id']] = \
                        (Helper.shortPlayerName(rec['firstname'], rec['lastname'], rec['surname']), rec['player_id'])

                # Командные турниры
                sql = \
                    "select tour_id, teams.team_id, team_name, player_id, firstname, lastname, surname " \
                    "from team_players " \
                    "left join teams using (team_id) " \
                    "left join players using (player_id) " \
                    "left join tourn_team using (team_id) " \
                    "where team_id in (select team_id from team_players where player_id = {0})".format(pl.id)
                cursor.execute(sql)
                parts_team = {}
                for rec in cursor.fetchall():
                    if rec['tour_id'] in parts_team:
                        parts_team[rec['tour_id']][1].append(
                            (Helper.shortPlayerName(rec['firstname'], rec['lastname'],
                                                    rec['surname']), rec['player_id']))
                    else:
                        parts_team[rec['tour_id']] = \
                            [rec['team_name'],
                             [(Helper.shortPlayerName(rec['firstname'], rec['lastname'], rec['surname']),
                               rec['player_id'])]]

                sql = Queries.select_results.format(pl.id)
                cursor.execute(sql)
                for rec in cursor.fetchall():
                    record = rec
                    if rec['id'] in parts_pair:
                        record['partner'] = parts_pair[rec['id']]
                    if rec['id'] in parts_team:
                        record['partner'] = parts_team[rec['id']]
                    pl.addResult(PlayingRecord(**rec))

    def loadExternalIDs(self, pl: Player):
        if pl.id:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = Queries.select_external_ids.format(pl.id)
                cursor.execute(sql)
                record = cursor.fetchone()
                if record:
                    pl.setExternalIds(record['wbf_id'] + 20000 if record['wbf_id'] else None, record['acbl_id'],
                                      record['gambler_nick'], record['bbo_nick'])

    def loadRateStat(self, pl: Player):
        if pl.id:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = Queries.select_rate_stat.format(pl.id)
                cursor.execute(sql)
                record = cursor.fetchone()
                if record:
                    pl.setRateStat(record['best_rate'], record['best_rate_date'],
                                   record['best_rank'], record['best_rank_date'])

    def loadPlayers(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = Queries.select_player.format("state in (1, 2, 4, 5)")
            cursor.execute(sql)
            result = []
            for record in cursor.fetchall():
                (razr, razr_temp) = Helper.getRazr(record['razr'], record['razr_coeff'])
                pl = Player(id=record['player_id'],
                            lastname=record['firstname'],
                            firstname=record['lastname'],
                            fathername=record['surname'],
                            birthdate=record['birthdate'],
                            city=record['city_name'],
                            razr=razr,
                            razr_temp=razr_temp,
                            rate=record['rate'],
                            pb=record['pb'],
                            mb=record['mb'],
                            emb=record['emb'])
                result.append(pl)
        return result

    def loadTournamentData(self, tid: int) -> Tournament:
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = Queries.select_tourn.format(tid)
            if cursor.execute(sql):
                tourn = Tournament(**cursor.fetchone())
                # Load nested tournaments
                sql = "select tourn_id as id, name from tourn_header where tounr_pair = {0};".format(tourn.id)
                cursor.execute(sql)
                for record in cursor.fetchall():
                    tourn.nested.append(Tournament(**record))
                if tourn.parent_id is not None and tourn.parent_id > 0:
                    sql = Queries.select_tourn.format(tourn.parent_id)
                    cursor.execute(sql)
                    parent = cursor.fetchone()
                    if parent:
                        tourn.parent_name = parent['name']
            else:
                tourn = Tournament()
        return tourn

    def loadIndividualParticipants(self, tourn: Tournament):
        if tourn.id:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = Queries.select_ind.format(tourn.id)
                cursor.execute(sql)
                for record in cursor.fetchall():
                    record['player'] = (Helper.shortPlayerName(record['firstname'], record['lastname'],
                                                               record['surname']), record['player_id'])
                    tourn.addParticipant(TournamentRecordInd(**record))

    def loadPairParticipants(self, tourn: Tournament):
        if tourn.id:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = Queries.select_pair.format(tourn.id)
                cursor.execute(sql)
                for record in cursor.fetchall():
                    record['player1'] = (Helper.shortPlayerName(record['first1'], record['last1'], record['sur1']),
                                         record['id1'])
                    record['player2'] = (Helper.shortPlayerName(record['first2'], record['last2'], record['sur2']),
                                         record['id2'])
                    tourn.addParticipant(TournamentRecordPair(**record))

    def loadSessionParticipants(self, tourn: Tournament):
        if tourn.id:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = Queries.select_session.format(tourn.id)
                cursor.execute(sql)
                for record in cursor.fetchall():
                    if (record['id1'] == record['id2']) or record['id2'] is None:
                        record['player'] = (Helper.shortPlayerName(record['first1'], record['last1'], record['sur1']),
                                            record['id1'])
                        tourn.addParticipant(TournamentRecordInd(**record))
                    else:
                        record['player1'] = (Helper.shortPlayerName(record['first1'], record['last1'], record['sur1']),
                                             record['id1'])
                        record['player2'] = (Helper.shortPlayerName(record['first2'], record['last2'], record['sur2']),
                                             record['id2'])
                        tourn.addParticipant(TournamentRecordPair(**record))

    def loadTeamParticipants(self, tourn: Tournament):
        if tourn.id:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = Queries.select_teams.format(tourn.id)
                cursor.execute(sql)
                team_records = {}
                for record in cursor.fetchall():
                    if record['tid'] in team_records:
                        team_records[record['tid']]['players'].append(
                            (Helper.shortPlayerName(record['firstname'], record['lastname'], record['surname']),
                             record['plid']))
                    else:
                        team_records[record['tid']] = {}
                        for key in ['placeh', 'placel', 'result', 'pb', 'ro', 'mb']:
                            team_records[record['tid']][key] = record[key]
                        team_records[record['tid']]['team'] = record['team_name']
                        team_records[record['tid']]['players'] = \
                            [(Helper.shortPlayerName(record['firstname'], record['lastname'],
                                                     record['surname']), record['plid'])]
                        team_records[record['tid']]['players_nq'] = []
                sql = Queries.select_teams_nq.format(tourn.id)
                cursor.execute(sql)
                for record in cursor.fetchall():
                    if record['tid'] in team_records:
                        team_records[record['tid']]['players_nq'].append(
                            (Helper.shortPlayerName(record['firstname'], record['lastname'], record['surname']),
                             record['plid']))
                    else:
                        team_records[record['tid']] = {}
                        for key in ['placeh', 'placel', 'result', 'pb', 'ro', 'mb']:
                            team_records[record['tid']][key] = record[key]
                        team_records[record['tid']]['team'] = record['team_name']
                        team_records[record['tid']]['players_nq'] = \
                            [(Helper.shortPlayerName(record['firstname'], record['lastname'],
                                                     record['surname']), record['plid'])]
                cursor.execute(sql)
                for team in team_records.values():
                    tourn.addParticipant(TournamentRecordTeam(**team))

    def findPlayerByName(self, name: str):
        if len(name) >= 3:
            with self.conn.cursor(pymysql.cursors.Cursor) as cursor:
                sql = Queries.select_find_player.format(pymysql.escape_string(name.strip()))
                cursor.execute(sql)
                return cursor.fetchall()

    def loadList(self, do_full=0):
        result = []
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            if do_full:
                sql = Queries.select_fullList
            else:
                sql = Queries.select_rate
            cursor.execute(sql)
            for record in cursor.fetchall():
                (razr, razr_temp) = Helper.getRazr(record['razr'], record['razr_coeff'])
                player = RateRecord(id=record['player_id'],
                                    lastname=record['firstname'],
                                    firstname=record['lastname'],
                                    fathername=record['surname'],
                                    birthdate=record['birthdate'],
                                    sex=record['sex'],
                                    city=record['city_name'],
                                    razr=razr,
                                    razr_temp=razr_temp,
                                    rate=record['rate'],
                                    pb=record['pb'],
                                    mb=record['mb'],
                                    emb=record['emb'])
                result.append(player)
        return result

    def loadRate(self, dt: datetime.date):
        result = []
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = Queries.select_rate.format(dt.strftime("%Y%m%d"))
            cursor.execute(sql)
            for record in cursor.fetchall():
                (razr, razr_temp) = Helper.getRazr(record['razr'], record['razr_coeff'])
                player = RateRecord(id=record['player_id'],
                                    lastname=record['firstname'],
                                    firstname=record['lastname'],
                                    fathername=record['surname'],
                                    birthdate=record['birthdate'],
                                    sex=record['sex'],
                                    city=record['city_name'],
                                    razr=razr,
                                    razr_temp=razr_temp,
                                    rate=record['rate'],
                                    pb=record['pb'],
                                    mb=record['mb'],
                                    emb=record['emb'])
                result.append(player)
        return result

    def loadTournList(self):
        result = []
        sql = Queries.select_all_tourns
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            for record in cursor.fetchall():
                result.append(Tournament(**record))
        return result

    def loadRateDates(self):
        result = []
        sql = Queries.select_rate_dates
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            for record in cursor.fetchall():
                result.append(record['r_date'])
        return result

    def loadRateTourns(self, year: int) -> RateTournaments:
        # Load rate tournaments for specified year
        result = RateTournaments(year)
        sql = Queries.select_rate_tourns.format(year)
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            for record in cursor.fetchall():
                result.addRecord(record['tid'], record['name'], record['player_id'],
                                 Helper.shortPlayerName(record['firstname'], record['lastname'], record['surname']),
                                 record['placeh'], record['placel'], record['pb'], record['ro'])
        return result
