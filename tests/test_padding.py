"""Padding contracts using real derivation, payload serialization and readback."""
import json
from pathlib import Path
import sys
import types
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from test_core_annual_series import CORE


class PaddingTests(unittest.TestCase):
    def run_case(self, options=None, derived=(3, 7), manual=False, existing=None, dry_run=False, handoff_minutes=0, final_padding=None):
        now = datetime(2026, 10, 9, tzinfo=timezone.utc)
        start, end = now + timedelta(hours=2), now + timedelta(hours=3)
        program = dict(title='Test', start_time=start.isoformat(), end_time=end.isoformat(),
                       start_timestamp=int(start.timestamp()), stop_timestamp=int(end.timestamp()))
        recording = types.SimpleNamespace(
            id=7, channel_id=12, start_time=start - timedelta(minutes=derived[0]),
            end_time=end + timedelta(minutes=derived[1]),
            channel=types.SimpleNamespace(name='Test', is_catchup=True, catchup_days=7),
            custom_properties={} if manual else {'program': program},
        )
        manager = MagicMock()
        manager.select_related.return_value.filter.return_value.order_by.return_value = [recording]
        modules = {
            'django.utils': types.SimpleNamespace(timezone=types.SimpleNamespace(now=lambda: now)),
            'apps.channels.models': types.SimpleNamespace(Recording=types.SimpleNamespace(objects=manager)),
        }
        schedules = [] if existing is None else [existing]
        fetches = 0
        def fetch(client):
            nonlocal fetches
            fetches += 1
            if final_padding is not None and fetches == 3 and schedules:
                schedules[0].update(pre_padding_minutes=final_padding[0], post_padding_minutes=final_padding[1])
            return [dict(s) for s in schedules]
        def create(path, payload):
            self.assertEqual(path, '/api/schedules')
            # Simulate the real Mustarrd response fields, preserving explicit zero.
            wire = json.loads(json.dumps(payload))
            schedules.append(dict(id=9, status='scheduled', account_id=wire['account_id'],
                                  channel_id=wire['channel_id'],
                                  start_timestamp=wire['program']['start_timestamp'],
                                  stop_timestamp=wire['program']['stop_timestamp'],
                                  pre_padding_minutes=wire['pre_padding_minutes'],
                                  post_padding_minutes=wire['post_padding_minutes'],
                                  custom_filename=wire['custom_filename']))
        with patch.dict(sys.modules, modules), \
             patch.object(CORE, 'MustarrdClient') as client, \
             patch.object(CORE, '_resolve_dispatcharr_program', return_value=(program, 'dispatcharr_exact')), \
             patch.object(CORE, '_restore_raw_episode_metadata', side_effect=lambda c, a, ch, p: p), \
             patch.object(CORE, '_render_filename', return_value='Test.ts'), \
             patch.object(CORE, '_fetch_schedules', side_effect=fetch), \
             patch.object(CORE, '_fetch_catchup_channels', return_value={'12': {}}), \
             patch.object(CORE, '_delete_dispatcharr_recording', return_value=True) as delete:
            client.return_value.post_json.side_effect = create
            result = CORE.run_handoff({'handoff_minutes': handoff_minutes, 'dry_run': dry_run, **(options or {})})
            payloads = client.return_value.post_json.call_args_list
            self.assertEqual(delete.call_count, result['handed_off'])
            if not handoff_minutes or dry_run:
                self.assertFalse(delete.called)
            return result, payloads, client.call_count, manager, recording

    def assert_padding(self, options, expected, **kwargs):
        result, calls, _, _, _ = self.run_case(options, **kwargs)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['mirrored'], 1)
        payload = calls[0].args[1]
        self.assertEqual((payload['pre_padding_minutes'], payload['post_padding_minutes']), expected)
        self.assertTrue(all(type(payload[k]) is int for k in ('pre_padding_minutes', 'post_padding_minutes')))
        return payload

    def test_configured_and_independent_overrides(self):
        self.assert_padding({'pre_padding_minutes': 10, 'post_padding_minutes': '20'}, (10, 20))
        self.assert_padding({'pre_padding_minutes': 10}, (10, 7))
        self.assert_padding({'post_padding_minutes': 20}, (3, 20))
        self.assert_padding({'pre_padding_minutes': 120, 'post_padding_minutes': 120}, (120, 120))

    def test_explicit_zero_is_not_fallback(self):
        for zero in (0, '0', 0.0, '0' * 5000):
            self.assert_padding({'pre_padding_minutes': zero, 'post_padding_minutes': zero}, (0, 0))
            self.assert_padding({'pre_padding_minutes': zero}, (0, 7))
            self.assert_padding({'post_padding_minutes': zero}, (3, 0))

    def test_unset_and_legacy_defaults_preserve_derivation(self):
        self.assert_padding({}, (3, 7))
        for blank in (None, '', '  '):
            self.assert_padding({'pre_padding_minutes': blank, 'post_padding_minutes': blank}, (3, 7))
        self.assert_padding(CORE.DEFAULTS, (3, 7))

    def test_padded_and_unpadded_timestamps_never_double_pad(self):
        for derived in ((0, 0), (3, 7)):
            payload = self.assert_padding({'pre_padding_minutes': 5, 'post_padding_minutes': 9}, (5, 9), derived=derived)
            self.assertEqual(payload['program']['start_time'], '2026-10-09T02:00:00+00:00')
            self.assertEqual(payload['program']['end_time'], '2026-10-09T03:00:00+00:00')
        self.assert_padding({}, (0, 0), derived=(0, 0))

    def test_manual_window_is_exact_and_overrides_extend_it(self):
        for options, expected in (({}, (0, 0)), ({'pre_padding_minutes': 5}, (5, 0)),
                                  ({'post_padding_minutes': 9}, (0, 9))):
            payload = self.assert_padding(options, expected, manual=True)
            self.assertEqual(payload['program']['start_time'], '2026-10-09T01:57:00+00:00')
            self.assertEqual(payload['program']['end_time'], '2026-10-09T03:07:00+00:00')

    def test_invalid_values_fail_before_query_or_network(self):
        for name in ('pre_padding_minutes', 'post_padding_minutes'):
            for bad in (-1, '-1', 121, '121', 'abc', 1.5, '1.5', True, False, [], {}, float('inf'), float('nan'), 10**1000, '9' * 5000):
                with self.subTest(name=name, value=bad):
                    result, calls, clients, manager, _ = self.run_case({name: bad})
                    self.assertEqual(result['status'], 'error')
                    self.assertIn(name, result['message'])
                    self.assertEqual((clients, len(calls)), (0, 0))
                    self.assertFalse(manager.select_related.called)

    def test_dry_run_reports_effective_padding_without_writes(self):
        result, calls, _, _, _ = self.run_case({'pre_padding_minutes': 0, 'post_padding_minutes': 11}, dry_run=True)
        detail = next(d for d in result['details'] if d['status'] == 'would_mirror')
        self.assertEqual((detail['pre_padding'], detail['post_padding']), (0, 11))
        self.assertEqual(calls, [])

    def test_existing_different_padding_is_not_rewritten_or_handed_off(self):
        now = datetime(2026, 10, 9, tzinfo=timezone.utc)
        existing = dict(id=9, status='scheduled', account_id=1, channel_id='12',
                        start_timestamp=int((now + timedelta(hours=2)).timestamp()),
                        stop_timestamp=int((now + timedelta(hours=3)).timestamp()),
                        pre_padding_minutes=3, post_padding_minutes=7, custom_filename='Test.ts')
        result, calls, _, _, _ = self.run_case({'pre_padding_minutes': 0}, existing=existing, handoff_minutes=180)
        self.assertEqual(result['skipped'], 1)
        self.assertEqual(result['details'][0]['reason'], 'existing_mustarrd_schedule_mismatch')
        self.assertEqual(calls, [])
        result, calls, _, _, _ = self.run_case(existing=existing)
        self.assertEqual(result['already_mirrored'], 1)
        self.assertEqual(calls, [])

    def test_positive_final_handoff_verifies_override_and_changed_readback(self):
        for padding in ((0, 0), (10, 20)):
            options = dict(pre_padding_minutes=padding[0], post_padding_minutes=padding[1])
            result, _, _, _, _ = self.run_case(options, handoff_minutes=180)
            self.assertEqual(result['handed_off'], 1)
            result, _, _, _, _ = self.run_case(options, handoff_minutes=180, final_padding=(3, 7))
            self.assertEqual(result['handed_off'], 0)
            self.assertEqual(result['details'][-1]['reason'], 'mustarrd_final_schedule_verification_failed')

    def test_legacy_derivation_preserves_dst_elapsed_minutes_and_clamp(self):
        zone = ZoneInfo('America/New_York')
        start = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=1).astimezone(timezone.utc)
        end = start + timedelta(hours=1)
        recording = types.SimpleNamespace(start_time=(start - timedelta(minutes=90)).astimezone(zone),
                                          end_time=(end + timedelta(minutes=300)).astimezone(zone))
        self.assertEqual(CORE._derive_padding(recording, start, end), (90, 120))

    def test_manifest_defaults_are_blank_and_match_runtime(self):
        manifest = json.loads((Path(__file__).resolve().parents[1] / 'mustarrd-dvr-handoff/plugin.json').read_text())
        fields = {f['id']: f for f in manifest['fields']}
        for name in ('pre_padding_minutes', 'post_padding_minutes'):
            self.assertEqual(fields[name]['default'], CORE.DEFAULTS[name])
            self.assertEqual(fields[name]['default'], '')
            self.assertIn('minutes', fields[name]['label'])
