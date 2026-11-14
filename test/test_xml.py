from datetime import date

import lxml.etree as et
import pytest

from src.interface import (
    AdminPos, OtherPos, Player, PlayingRecord, TdPos, TournamentRecord,
    TournamentRecordInd, TournamentRecordPair, TournamentRecordTeam,
)


@pytest.mark.parametrize('value,expected', [
    (None, '-'), (0, '0.00'), (52.125, '52.12'), (-12.5, '-12.50'),
])
def test_tournament_result(value, expected):
    assert TournamentRecord(result=value).xml.findtext('result') == expected


def test_pair_null_result_regression():
    xml = TournamentRecordPair(
        result=None, placeh=1, placel=2,
        player1=('Иванов И.И.', 10), player2=('Петров П.П.', 20),
    ).xml
    assert xml.findtext('result') == '-'
    assert xml.findtext('place') == '1-2'
    assert [(p.get('id'), p.text) for p in xml.findall('participant/player')] == [
        ('10', 'Иванов И.И.'), ('20', 'Петров П.П.'),
    ]


@pytest.mark.parametrize('value,present', [(None, False), (0, False), (2.5, True)])
def test_points_omission(value, present):
    xml = TournamentRecord(pb=value, ro=value, mb=value).xml
    for field in ('pb', 'ro', 'mb'):
        assert (xml.find(field) is not None) == present


def test_individual_participant():
    xml = TournamentRecordInd(player=('Игрок', 10)).xml
    assert xml.find('participant/player').attrib == {'id': '10'}


def test_team_participants():
    xml = TournamentRecordTeam(
        team='Команда & <друзья>', players=[('Игрок', 10)],
        players_nq=[('Вне зачёта', 20)],
    ).xml
    parsed = et.fromstring(et.tostring(xml))
    assert parsed.find('team').get('name') == 'Команда & <друзья>'
    assert [p.attrib for p in parsed.findall('team/player')] == [
        {'id': '10'}, {'id': '20', 'qualified': '0'},
    ]


def test_position_xml_references():
    other = OtherPos(id=12, year=2020, event='Событие', title='Титул').xml
    directing = TdPos(id=13, tournament='Турнир', date=date(2020, 1, 1), title='Судья').xml
    assert other.find('event').attrib == {'id': '12'}
    assert other.find('title').text == 'Титул'
    assert directing.find('tournament').attrib == {'id': '13'}
    assert directing.find('title').text == 'Судья'


def test_empty_admin_position():
    assert len(AdminPos().xml) == 0


def test_minimal_player_xml():
    xml = Player(id=10, lastname='Иванов', firstname=None, fathername=None).xml
    assert xml.get('id') == '10'
    assert xml.findtext('info/lastname') == 'Иванов'
    assert not xml.findall('.//tournament')


def test_playing_record_requires_date():
    with pytest.raises(ValueError, match='отсутствует дата'):
        PlayingRecord(id=10).xml


@pytest.mark.parametrize('championship,kind,place,expected', [
    (3, 2, 3, True), (3, 2, 4, False),
    (40, 2, 10, True), (40, 2, 11, False),
    (40, 3, 8, True), (40, 3, 9, False),
    (None, 2, 1, False), (40, 2, None, False),
])
def test_achievement_boundaries(championship, kind, place, expected):
    assert PlayingRecord(champ_t=championship, type=kind, placeh=place).achievement is expected
