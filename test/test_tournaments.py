from datetime import date
from unittest.mock import MagicMock

import pytest

from src import tournaments
from src.interface import Tournament, TournamentRecordPair


@pytest.mark.parametrize('kind,loader', [
    (1, 'loadIndividualParticipants'), (5, 'loadIndividualParticipants'),
    (2, 'loadPairParticipants'), (3, 'loadTeamParticipants'),
    (4, 'loadSessionParticipants'),
])
def test_tournament_loads_participants(monkeypatch, kind, loader):
    """Логика вызова загрузки участников в зависимости от типа турнира"""
    base = MagicMock()
    base.loadTournamentData.return_value = Tournament(id=10, type=kind)
    factory = MagicMock()
    factory.return_value.__enter__.return_value = base
    monkeypatch.setattr(tournaments, 'BaseIFace', factory)

    xml = tournaments.getTournamentXml(10)

    assert xml.get('id') == '10'
    for name in ('loadIndividualParticipants', 'loadPairParticipants',
                 'loadTeamParticipants', 'loadSessionParticipants'):
        assert getattr(base, name).call_count == (1 if name == loader else 0)
    factory.return_value.__exit__.assert_called_once()


def test_pair_tournament_serializes_missing_result(monkeypatch):
    """Проверяем коректность вывода если в результате пары NULL 
    (Обычно артефакт от старых данных)"""
    tournament = Tournament(id=10, type=2, name='Турнир', start=date(2020, 1, 1))
    base = MagicMock()
    base.loadTournamentData.return_value = tournament
    base.loadPairParticipants.side_effect = lambda target: target.addParticipant(
        TournamentRecordPair(result=None, player1=('Первый', 1), player2=('Второй', 2))
    )
    factory = MagicMock()
    factory.return_value.__enter__.return_value = base
    monkeypatch.setattr(tournaments, 'BaseIFace', factory)

    assert tournaments.getTournamentXml(10).findtext('participants/record/result') == '-'
