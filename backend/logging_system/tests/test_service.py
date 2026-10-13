from unittest.mock import patch, Mock
from django.test import TestCase

from logging_system.models import SystemState
from logging_system.services import (
    FortranCalcLoggingService,
    RiskAssessmentLoggingService,
    LoggingToggleService,
)


class BaseServiceTests(TestCase):
    """Общие проверки: is_enabled / set_enabled."""

    def setUp(self):
        self.state = SystemState.objects.create(id=1, logging_enabled=True)

    def test_is_enabled_true(self):
        self.state.logging_enabled = True
        self.state.save()
        self.assertTrue(FortranCalcLoggingService.is_enabled())

    def test_is_enabled_false(self):
        self.state.logging_enabled = False
        self.state.save()
        self.assertFalse(FortranCalcLoggingService.is_enabled())

    @patch("logging_system.services.LoggingToggleService.logger")
    def test_set_enabled_turns_on(self, mock_logger):
        self.state.logging_enabled = False
        self.state.save()
        LoggingToggleService.set_enabled(True)
        self.state.refresh_from_db()
        self.assertTrue(self.state.logging_enabled)
        mock_logger.info.assert_called_with("Логирование включено")

    @patch("logging_system.services.LoggingToggleService.logger")
    def test_set_enabled_turns_off(self, mock_logger):
        self.state.logging_enabled = True
        self.state.save()
        LoggingToggleService.set_enabled(False)
        self.state.refresh_from_db()
        self.assertFalse(self.state.logging_enabled)
        mock_logger.info.assert_called_with("Логирование выключено")

    @patch("logging_system.services.LoggingToggleService.logger")
    def test_set_enabled_no_change(self, mock_logger):
        self.state.logging_enabled = True
        self.state.save()
        LoggingToggleService.set_enabled(True)
        mock_logger.info.assert_not_called()

    @patch("logging_system.services.SystemState.get_current_state")
    def test_is_enabled_fallback_when_db_error(self, mock_get_state):
        """При ошибке БД is_enabled возвращает True."""
        mock_get_state.side_effect = Exception("DB connection error")
        self.assertTrue(FortranCalcLoggingService.is_enabled())


class FortranCalcLoggingServiceTests(TestCase):

    def setUp(self):
        SystemState.objects.create(id=1, logging_enabled=True)

    @patch("logging_system.services.FortranCalcLoggingService.logger")
    def test_log_request_when_enabled(self, mock_logger):
        user = Mock(username="testuser", is_authenticated=True)

        FortranCalcLoggingService.log_request(
            user,
            status="caution",
            rank=0.53,
            all_drugs=["drugA", "drugB"],
        )

        mock_logger.info.assert_called_once()
        line = mock_logger.info.call_args[0][0]
        self.assertIn("User: testuser", line)
        self.assertIn("Status: caution", line)
        self.assertIn("Rank: 0.53", line)
        self.assertIn("Drugs: ['drugA', 'drugB']", line)

    @patch("logging_system.services.FortranCalcLoggingService.logger")
    def test_log_request_anonymous_user(self, mock_logger):
        user = Mock(is_authenticated=False)
        FortranCalcLoggingService.log_request(user, status="compatible")
        line = mock_logger.info.call_args[0][0]
        self.assertIn("User: Anonymous", line)

    @patch("logging_system.services.FortranCalcLoggingService.logger")
    def test_log_request_disabled(self, mock_logger):
        state = SystemState.objects.get(id=1)
        state.logging_enabled = False
        state.save()

        user = Mock(username="u", is_authenticated=True)
        FortranCalcLoggingService.log_request(user, status="caution")
        mock_logger.info.assert_not_called()

    @patch("logging_system.services.FortranCalcLoggingService.logger")
    def test_banned_pairs_cont_is_written_as_is(self, mock_logger):
        """Fortran получает канонический формат [(drug, [contra])]."""
        user = Mock(username="u", is_authenticated=True)
        cont = [("Аспирин", ["язва", "астма"])]

        FortranCalcLoggingService.log_request(
            user,
            status="banned-contraindications",
            banned_pairs_cont=cont,
        )
        line = mock_logger.info.call_args[0][0]
        self.assertIn("[('Аспирин', ['язва', 'астма'])]", line)


class RiskAssessmentLoggingServiceTests(TestCase):

    def setUp(self):
        SystemState.objects.create(id=1, logging_enabled=True)

    @patch("logging_system.services.RiskAssessmentLoggingService.logger")
    def test_log_request_with_missing_drugs(self, mock_logger):
        user = Mock(username="testuser", is_authenticated=True)

        RiskAssessmentLoggingService.log_request(
            user,
            status="caution",
            rank=0.53,
            missing_drugs=["unknown"],
            all_drugs=["drugA", "drugB"],
        )
        line = mock_logger.info.call_args[0][0]
        self.assertIn("MissingDrugs: ['unknown']", line)
        self.assertIn("Drugs: ['drugA', 'drugB']", line)

    @patch("logging_system.services.RiskAssessmentLoggingService.logger")
    def test_banned_pairs_cont_is_canonicalized(self, mock_logger):
        """Risk получает плоский формат — превращается в [(drug, [contra])]."""
        user = Mock(username="u", is_authenticated=True)
        flat = [
            {"drugName": "Аспирин", "contraindicationName": "язва"},
            {"drugName": "Аспирин", "contraindicationName": "астма"},
            {"drugName": "Варфарин", "contraindicationName": "кровотечение"},
        ]

        RiskAssessmentLoggingService.log_request(
            user,
            status="banned-contraindications",
            banned_pairs_cont=flat,
        )
        line = mock_logger.info.call_args[0][0]
        self.assertIn("('Аспирин', ['язва', 'астма'])", line)
        self.assertIn("('Варфарин', ['кровотечение'])", line)


from logging_system.services import BaseLoggingService


class FormatBannedPairsTests(TestCase):
    """Тесты для BaseLoggingService._format_banned_pairs."""

    def test_none_returns_empty(self):
        self.assertEqual(BaseLoggingService._format_banned_pairs(None), [])

    def test_empty_list_returns_empty(self):
        self.assertEqual(BaseLoggingService._format_banned_pairs([]), [])

    def test_pair_key_is_used(self):
        """Формат DrugPairChecker: {'pair': [name1, name2], 'comment': ...}."""
        pairs = [{"pair": ["Аспирин", "Варфарин"], "comment": "кровотечение"}]
        self.assertEqual(
            BaseLoggingService._format_banned_pairs(pairs),
            [["Аспирин", "Варфарин"]],
        )

    def test_names_key_is_used(self):
        """Формат risk: {'names': [name1, name2], 'reason': ...}."""
        pairs = [{"names": ["Аспирин", "Варфарин"], "reason": None}]
        self.assertEqual(
            BaseLoggingService._format_banned_pairs(pairs),
            [["Аспирин", "Варфарин"]],
        )

    def test_names_takes_priority_over_pair(self):
        """Если есть оба ключа — приоритет у 'names'."""
        pairs = [{
            "names": ["A1", "A2"],
            "pair": ["B1", "B2"],
        }]
        self.assertEqual(
            BaseLoggingService._format_banned_pairs(pairs),
            [["A1", "A2"]],
        )

    def test_single_name_returns_string(self):
        """Если в names только один элемент — вернуть его как есть (не список)."""
        pairs = [{"names": ["Аспирин"]}]
        self.assertEqual(
            BaseLoggingService._format_banned_pairs(pairs),
            ["Аспирин"],
        )

    def test_more_than_two_names_takes_first_two(self):
        """Если names длиннее двух — берём первые два."""
        pairs = [{"names": ["A", "B", "C"]}]
        self.assertEqual(
            BaseLoggingService._format_banned_pairs(pairs),
            [["A", "B"]],
        )

    def test_empty_names_is_skipped(self):
        """Пустой список names → элемент пропускается."""
        pairs = [{"names": []}, {"pair": ["X", "Y"]}]
        self.assertEqual(
            BaseLoggingService._format_banned_pairs(pairs),
            [["X", "Y"]],
        )

    def test_item_without_any_names_key_is_skipped(self):
        """У элемента нет ни 'names', ни 'pair' — пропускаем."""
        pairs = [{"comment": "нет данных"}]
        self.assertEqual(
            BaseLoggingService._format_banned_pairs(pairs),
            [],
        )

    def test_multiple_pairs_preserve_order(self):
        pairs = [
            {"pair": ["A", "B"]},
            {"names": ["C", "D"]},
            {"pair": ["E", "F"]},
        ]
        self.assertEqual(
            BaseLoggingService._format_banned_pairs(pairs),
            [["A", "B"], ["C", "D"], ["E", "F"]],
        )

    def test_banned_pairs_appear_in_log_line(self):
        """Интеграционная проверка: результат попадает в строку лога."""
        with patch("logging_system.services.FortranCalcLoggingService.logger") as mock_logger:
            SystemState.objects.create(id=1, logging_enabled=True)

            user = Mock(username="u", is_authenticated=True)
            FortranCalcLoggingService.log_request(
                user,
                status="banned",
                banned_pairs=[{"pair": ["Аспирин", "Варфарин"], "comment": "x"}],
            )
            line = mock_logger.info.call_args[0][0]
            self.assertIn("BannedPairs: [['Аспирин', 'Варфарин']]", line)