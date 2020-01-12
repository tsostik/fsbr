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
        "select player_id, firstname, lastname, surname, birthdate, city_name, razr, razr_coeff, mail, " \
        "ifnull(rate, 0) as rate, place, ifnull(pb_, 0) as pb , ifnull(mb_,0) as mb, ifnull(emb_,0) as emb " \
        "from players " \
        "left join cities using (city_id) " \
        "left join " \
        "(select * from rate_history where r_date = (select max(r_date) from rate_history) ) as rt " \
        "using (player_id) " \
        "left join " + select_pb + "using(player_id) " \
        "left join " + select_mb + "using(player_id)" \
        "where {0};"
    select_fullList = \
        "select player_id, firstname, lastname, surname, city_name, razr, razr_coeff, sex, birthdate, " \
        "ifnull(rating, 0) as rate, ifnull(pb_, 0) as pb , ifnull(mb_,0) as mb, ifnull(emb_,0) as emb, " \
        "firstname < 'А' as isLatin " \
        "from players " \
        "left join cities using (city_id) " \
        "left join ratelist on player_id=id " \
        "left join " + select_pb + "using(player_id) " \
        "left join " + select_mb + "using(player_id) " \
        "where players.state in (1, 2, 4, 5) " \
        "order by isLatin asc, city_name asc, firstname asc, lastname asc, surname asc"
    select_rate = \
        "select players.player_id, firstname, lastname, surname, city_name, razr, razr_coeff, sex, birthdate, " \
        "ifnull(rate, 0) as rate, ifnull(pb_, 0) as pb, 0 as mb, 0 as emb " \
        "from rate_history " \
        "left join players using(player_id) " \
        "left join cities using (city_id) " \
        "left join " + select_pb + "using(player_id) " \
        "left join " + select_mb + "using(player_id) " \
        "where players.state in (1, 2, 4, 5) and r_date = {0} " \
        "order by rate desc, pb desc, firstname asc"
    select_find_player = " select player_id as plid, firstname, lastname, surname, city_name " \
                         "from players left join cities using(city_id) " \
                         "where state not in (7) and firstname like '%{0}%' " \
                         "order by firstname, lastname, surname, city_name;"
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
        "where type in (1, 2, 3) and results.player_id = {0};"
    select_other = \
        "select events.event_id as id, event_name as event, year(event_date) as year, position as title " \
        "from events_part left join events using (event_id) where player_id = {0};"

    select_tourn = "select tourn_id as id, type, name, ifnull(tour_date_start, tour_date) as start, " \
                   "tour_date as end, city_name as city " \
                   "from tourn_header left join cities using (city_id) " \
                   " where tourn_id = {0};"
    select_all_tourns = "select tourn_id as id, type, name, ifnull(tour_date_start, tour_date) as start, "  \
                        "tour_date as end, city_name as city, tounr_pair as parent " \
                        "from tourn_header left join cities using (city_id) "
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
        "where team_id in (select team_id from tourn_team where tour_id = {0});"
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