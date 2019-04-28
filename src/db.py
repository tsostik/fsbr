import pymysql.cursors
from src.interface import *


class BaseIFace:
    select_pb = "(select player_id, ifnull( sum(pb), 0) as pb_, sum(emb) as emb_ " \
                "from results " \
                "group by player_id) " \
                "as sel_pb "
    select_mb = "(select r.player_id, tourn_id, sum(if( r.mb > ifnull(s.mb, 0), r.mb, ifnull(s.mb, 0))) as mb_ " \
                "from results as r left join results_ses as s on " \
                "( (r.player_id = s.player_id) and (r.tourn_id = s.main_tourn_id) ) group by player_id )" \
                "as el_mb "
    select_player = \
        "select player_id, firstname, lastname, surname, birthdate, city_name, razr, razr_coeff, mail, " \
        "ifnull(rating, 0) as rate, ifnull(pb_, 0) as pb , ifnull(mb_,0) as mb, ifnull(emb_,0) as emb " \
        "from players " \
        "left join cities using (city_id) " \
        "left join ratelist on player_id=id " \
        "left join " + select_pb + "using(player_id) " \
        "left join " + select_mb + "using(player_id)" \
        "where {0};"
    select_admin = "select year_s as since, year_f as till, position as title, comitee as committee " \
                   "from admin_pos where player_id = {0};"
    select_directing = "select tds.tourn_id as id, tourn_header.name as tournament, " \
                       "tour_date as date, position as title " \
                       "from tds left join tourn_header using (tourn_id) where player_id = {0};"
    select_results = \
        "select type, tourn_header.tourn_id as id, year(results.tour_date) as year, name, placel, placeh, " \
        "pb, ro, if(results.mb > ifnull(results_ses.mb, 0), results.mb, ifnull(results_ses.mb, 0)) as mb, champ_t " \
        "from results " \
        "left join tourn_header using(tourn_id)" \
        "left join results_ses on tourn_id = main_tourn_id and results.player_id = results_ses.player_id " \
        "where type in (1, 2, 3) and results.player_id = {0};"

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

    @staticmethod
    def getRazr(db_razr, coeff):
        result = db_razr
        is_tmp = False
        if result > 50:
            result -= 100
            is_tmp = True
        if result == 30:
            result = 1.2 if coeff is None else coeff * 0.3
        else:
            result /= 2
        return result, is_tmp

    def loadPlayerData(self, plid):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = self.select_player.format("player_id = {0}".format(plid))
            cursor.execute(sql)
            record = cursor.fetchone()
            (razr, razr_temp) = self.getRazr(record['razr'], record['razr_coeff'])
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
                        pb=record['pb'],
                        mb=record['mb'],
                        emb=record['emb'])
        return pl

    def loadAdminPos(self, pl):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = self.select_admin.format(pl.id)
            cursor.execute(sql)
            for pos in cursor.fetchall():
                pl.addPosition(AdminPos(**pos))

    def loadDirecting(self, pl):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = self.select_directing.format(pl.id)
            cursor.execute(sql)
            for pos in cursor.fetchall():
                pl.addDirecting(TdPos(**pos))

    def loadPlayingRecords(self, pl):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = self.select_results.format(pl.id)
            cursor.execute(sql)
            for rec in cursor.fetchall():
                pl.addResult(PlayingRecord(**rec))

    def loadPlayers(self):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = self.select_player.format("state in (1, 2, 4, 5)")

            cursor.execute(sql)
            result = []
            for record in cursor.fetchall():
                (razr, razr_temp) = self.getRazr(record['razr'], record['razr_coeff'])
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
