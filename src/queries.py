class Queries:
    """
    Dedicated location to keep sql queries text
    """
    select_pb = "(select player_id, ifnull( sum(pb), 0) as pb_, sum(emb) as emb_ " \
                "from results " \
                "group by player_id) " \
                "as sel_pb "
    select_mb = "(select r.player_id, sum(if( r.mb > ifnull(s.mb, 0), r.mb, ifnull(s.mb, 0))) as mb_ " \
                "from results as r left join results_ses as s on " \
                "( (r.player_id = s.player_id) and (r.tourn_id = s.main_tourn_id) ) group by player_id )" \
                "as sel_mb "
    # TODO: select_player and select_fullList are very similar. Refactor to reduce code duplication
    select_player = \
        "select player_id, p.firstname as firstname, p.lastname as lastname, p.surname as surname, " \
        "p.birthdate as birthdate, city_name, razr, razr_coeff, q.mail as mail, club_id, " \
        "ifnull(rate, 0) as rate, place, ifnull(pb_, 0) as pb , ifnull(mb_,0) as mb, ifnull(emb_,0) as emb " \
        "from players as p left join questionaries as q using (player_id) " \
        "left join cities using (city_id) " \
        "left join " \
        "(select * from rate_history where r_date = (select max(r_date) from rate_history) ) as rt " \
        "using (player_id) " \
        "left join " + select_pb + "using(player_id) " \
        "left join " + select_mb + "using(player_id)" \
        "where {0};"
    select_fullList = \
        "select player_id, firstname, lastname, surname, city_name, razr, razr_coeff, sex, birthdate, club_id, " \
        "ifnull(rating, 0) as rate, ifnull(pb_, 0) as pb , ifnull(mb_,0) as mb, ifnull(emb_,0) as emb, " \
        "firstname < 'А' as isLatin " \
        "from players " \
        "left join cities using (city_id) " \
        "left join ratelist on player_id=id " \
        "left join " + select_pb + "using(player_id) " \
        "left join " + select_mb + "using(player_id) " \
        "where players.state in (1, 2, 4, 5) " \
        "order by isLatin asc, city_name asc, firstname asc, lastname asc, surname asc"
    select_sirius = \
        "select player_id, firstname, lastname, surname, city_name, razr, razr_coeff, sex, birthdate, club_id, " \
        "ifnull(rating, 0) as rate, ifnull(pb_, 0) as pb , ifnull(mb_,0) as mb, ifnull(emb_,0) as emb, " \
        "firstname < 'А' as isLatin " \
        "from players " \
        "left join cities using (city_id) " \
        "left join ratelist on player_id=id " \
        "left join " + select_pb + "using(player_id) " \
        "left join " + select_mb + "using(player_id) " \
        "where players.state in (1, 2, 4, 5) and club_id=25 " \
        "order by isLatin asc, city_name asc, firstname asc, lastname asc, surname asc"

    select_rate = \
        "select players.player_id, firstname, lastname, surname, city_name, razr, razr_coeff, sex, birthdate, " \
        "club_id, ifnull(rate, 0) as rate, ifnull(pb_, 0) as pb, 0 as mb, 0 as emb " \
        "from rate_history " \
        "left join players using(player_id) " \
        "left join cities using (city_id) " \
        "left join " + select_pb + "using(player_id) " \
        "left join " + select_mb + "using(player_id) " \
        "where players.state in (1, 2, 4, 5) and r_date = {0} " \
        "order by rate desc, pb desc, firstname asc"

    select_find_player = \
        "(select player_id as plid, firstname, lastname, surname, city_name, 0 as is_new " \
        "from players left join cities using(city_id) " \
        "where state not in (7) and firstname like '%{0}%') " \
        "union all " \
        "(select new_id as plid, firstname, lastname, surname, city_name, 1 as is_new " \
        "from fsbr_aux.new_players left join cities using(city_id) " \
        "where firstname like '%{0}%') " \
        "order by is_new, firstname, lastname, surname, city_name;"

    select_external_ids = "select wbf as wbf_id, acbl as acbl_id, gambler as gambler_nick, bbo as bbo_nick " \
                          "from external_ids where player_id = {0};"
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
        "where type in (1, 2, 3) and results.player_id = {0} order by results.tour_date desc;"
    select_other = \
        "select events.event_id as id, event_name as event, year(event_date) as year, position as title " \
        "from events_part left join events using (event_id) where player_id = {0};"

    select_tourn = "select tourn_id as id, type, name, ifnull(tour_date_start, tour_date) as start, " \
                   "tour_date as end, city_name as city, tounr_pair as parent_id, is_show " \
                   "from tourn_header left join cities using (city_id) " \
                   "left join tourn_site_data using (tourn_id) " \
                   "where tourn_id = {0};"
    select_all_tourns = "select tourn_id as id, type, name, ifnull(tour_date_start, tour_date) as start, "  \
                        "tour_date as end, city_name as city, tounr_pair as parent_id, family, is_show " \
                        "from tourn_header left join cities using (city_id) " \
                        "left join tourn_site_data using (tourn_id) " \
                        "where type != 5"
    select_ind = "select placeh, placel, pb, ro, mb, result, team_id as player_id, firstname, lastname, surname " \
                 "from tourn_ind left join players on team_id = player_id where tour_id = {0};"
    select_pair = \
        "select placeh, placel, pb, ro, mb, result, " \
        "p1.player_id as id1, p1.firstname as first1, p1.lastname as last1, p1.surname as sur1, " \
        "p2.player_id as id2, p2.firstname as first2, p2.lastname as last2, p2.surname as sur2 " \
        "from tourn_pair " \
        "left join players as p1 on player1 = p1.player_id " \
        "left join players as p2 on player2 = p2.player_id " \
        "where tour_id = {0};"
    select_teams = \
        "select placeh, placel, pb, ro, mb, result, teams.team_id as tid, team_name, " \
        "players.player_id as plid, firstname, lastname, surname " \
        "from team_players " \
        "left join teams using (team_id) " \
        "left join tourn_team using(team_id) " \
        "left join players using (player_id) " \
        "where tour_id = {0};"
    select_teams_nq = \
        "select teams.team_id as tid, team_name, players.player_id as plid, firstname, lastname, surname " \
        "from team_players_nonqual " \
        "left join teams using (team_id) " \
        "left join players using (player_id) " \
        "where team_id in (select team_id from tourn_team where tour_id = {0});"
    select_session = \
        "select placeh, placel, mb, result, " \
        "p1.player_id as id1, p1.firstname as first1, p1.lastname as last1, p1.surname as sur1, " \
        "p2.player_id as id2, p2.firstname as first2, p2.lastname as last2, p2.surname as sur2 " \
        "from tourn_ses " \
        "left join players as p1 on player1 = p1.player_id " \
        "left join players as p2 on player2 = p2.player_id " \
        "where tour_id = {0};"

    select_rate_dates = "select distinct r_date from rate_history order by r_date desc;"

    select_rate_stat = \
        "select " \
        "  srt.player_id as player_id, srt.r_date as best_rate_date, srt.rate as best_rate, " \
        "  srk.r_date as best_rank_date, srk.place as best_rank " \
        "from " \
        "  (select * from rate_history where player_id = {0} order by rate desc limit 1) as srt, " \
        "  (select * from rate_history where player_id = {0} order by place asc limit 1) as srk;"

    select_rate_tourns = \
        "select results.tourn_id as tid, player_id, name, placeh, placel, ro, pb, " \
        "firstname, lastname, surname " \
        "from results left join tourn_header using (tourn_id) " \
        "left join players using (player_id)" \
        "where ro > 0 and results.tour_date between {0}0101 and {0}1231 " \
        "order by results.tour_date asc, results.tourn_id asc, placeh asc, placel asc"

    select_families = \
        "select family_id, f.name as family_name, " \
        "t.name as tourn_name, t.tourn_id as tourn_id, t.tour_date as date " \
        "from tourn_header t left join families f on family_id = family " \
        "where family is not null {0};"

    select_razr_change = \
        "select player_id, firstname as lastname, lastname as firstname, surname as fathername, " \
        "old_razr, new_razr, razr_coeff as coeff " \
        "from razr_change left join players using (player_id) left join cities using (city_id) " \
        "where date = %s " \
        "order by get_razr_num(new_razr, cities.city_id), get_razr_num(old_razr, cities.city_id) desc, old_razr desc"

    select_club_stat = \
        "select club_id, clubs.name as club_name, max(tour_date) as maxdate " \
        "from tourn_header as t, clubs " \
        "where t.type=5 and t.city_id = clubs.city_id group by club_id  order by club_id"

    select_rate_forecast = \
        "select player_id, firstname, lastname, surname, city_name, name as tourn_name, tourn_id, " \
        "num, is_of, r " \
        "from rate_forecast left join players using (player_id) left join cities using (city_id) " \
        "left join tourn_header using (tourn_id) " \
        "order by player_id asc, num asc"

    select_max_id = "select p, n from " \
                    "(select player_id as p from players order by player_id desc limit 1, 1) as s1, " \
                    "(select max(new_id) as n from fsbr_aux.new_players) as s2"

    is_id_available = "select if(m+a>=1, 0, 1) as ok from " \
                      "(select count(1) as m from players where player_id={0}) as s1, " \
                      "(select count(1) as a from fsbr_aux.new_players where new_id={0}) as s2"

    add_new_player = "insert into fsbr_aux.new_players (`new_id`, `firstname`, `lastname`, `surname`, " \
                     "`sex`, `birthdate`, `city_id`, `sputnik`, `sputnik_first`, `author`, `Note`) values " \
                     "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
