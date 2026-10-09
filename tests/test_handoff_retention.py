import sys
import types
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from test_core_annual_series import CORE


class HandoffRetentionTests(unittest.TestCase):
    def run_case(self, value, minutes=1, existing=True, dry_run=False):
        now = datetime(2026, 10, 9, tzinfo=timezone.utc)
        recording = types.SimpleNamespace(
            id=7, channel_id=12, start_time=now + timedelta(minutes=minutes),
            channel=types.SimpleNamespace(name='Test', is_catchup=True, catchup_days=7),
            custom_properties={},
        )
        manager = MagicMock()
        manager.select_related.return_value.filter.return_value.order_by.return_value = [recording]
        modules = {
            'django.utils': types.SimpleNamespace(timezone=types.SimpleNamespace(now=lambda: now)),
            'apps.channels.models': types.SimpleNamespace(Recording=types.SimpleNamespace(objects=manager)),
        }
        settings = {'dry_run': dry_run}
        if value != 'missing':
            settings['handoff_minutes'] = value
        schedule = {'id': 9, 'status': 'scheduled'}
        with patch.dict(sys.modules, modules), \
             patch.object(CORE, 'MustarrdClient') as client, \
             patch.object(CORE, '_program_window_from_recording', return_value=(None, None, {})), \
             patch.object(CORE, '_synthetic_program', return_value={'title': 'Test'}), \
             patch.object(CORE, '_restore_raw_episode_metadata', side_effect=lambda c, a, ch, p: p), \
             patch.object(CORE, '_program_key', return_value=(1, '12', 1, 2)), \
             patch.object(CORE, '_schedule_key', return_value=(1, '12', 1, 2)), \
             patch.object(CORE, '_render_filename', return_value='Test'), \
             patch.object(CORE, '_schedule_is_verified', return_value=True), \
             patch.object(CORE, '_fetch_schedules', side_effect=([schedule] if existing else [], [schedule], [schedule])), \
             patch.object(CORE, '_fetch_catchup_channels', return_value={'12': {}}) as catchup, \
             patch.object(CORE, '_delete_dispatcharr_recording', return_value=True) as delete:
            result = CORE.run_handoff(settings)
            return result, delete.call_count, catchup.call_count, client.return_value.post_json.call_count

    def test_zero_keeps_existing_and_newly_mirrored_schedules(self):
        for zero in (0, '0'):
            for existing in (True, False):
                with self.subTest(zero=zero, existing=existing):
                    result, deleted, checked, created = self.run_case(zero, existing=existing)
                    self.assertEqual(result['handoff_minutes'], 0)
                    self.assertEqual(result['handed_off'], 0)
                    self.assertEqual((deleted, checked), (0, 0))
                    self.assertEqual(created, int(not existing))
                    self.assertEqual(result['already_mirrored'] + result['mirrored'], 1)

    def test_positive_window_retains_timed_removal(self):
        for value in (5, '5'):
            for minutes, expected in ((1, 1), (5, 1), (6, 0)):
                with self.subTest(value=value, minutes=minutes):
                    result, deleted, _, _ = self.run_case(value, minutes=minutes)
                    self.assertEqual(deleted, expected)
                    self.assertEqual(result['handed_off'], expected)

    def test_default_missing_and_invalid_remain_sixty_minutes(self):
        for value in ('missing', None, 'invalid'):
            for minutes, expected in ((60, 1), (61, 0)):
                with self.subTest(value=value, minutes=minutes):
                    result, deleted, _, _ = self.run_case(value, minutes=minutes)
                    self.assertEqual(result['handoff_minutes'], 60)
                    self.assertEqual(deleted, expected)

    def test_negative_values_keep_existing_one_minute_clamp(self):
        for value in (-1, "-1"):
            result, deleted, _, _ = self.run_case(value)
            self.assertEqual(result["handoff_minutes"], 1)
            self.assertEqual(deleted, 1)

    def test_dry_run_does_not_delete(self):
        for value in (0, '0', 60):
            with self.subTest(value=value):
                _, deleted, _, _ = self.run_case(value, dry_run=True)
                self.assertEqual(deleted, 0)
