from unittest.mock import MagicMock

import pytest

from src.db import BaseIFace
from src.interface import Tournament


def test_team_with_only_nonqualified_players():
    row = dict(tid=1, placeh=1, placel=1, result=None, pb=None, ro=None, mb=None,
               team_name='Команда', firstname='Иванов', lastname='Иван',
               surname=None, plid=10)
    cursor = MagicMock()
    cursor.fetchall.side_effect = [[], [row]]
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    base = BaseIFace()
    base._conn = connection
    tournament = Tournament(id=10, type=3)

    base.loadTeamParticipants(tournament)

    team = tournament.xml.find('participants/record/team')
    assert team.get('name') == 'Команда'
    assert [player.attrib for player in team.findall('player')] == [
        {'id': '10', 'qualified': '0'},
    ]
