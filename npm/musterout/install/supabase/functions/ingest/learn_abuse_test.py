"""Offline regression for the learning query and owner overflow brief."""
import datetime as dt
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('d2_learn', Path.home() / 'dev/personal-agents/17_WC_Learn/learn.py')
learn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(learn)


class AbuseBriefTests(unittest.TestCase):
    def setUp(self):
        self.date = dt.date(2026, 10, 11)
        self.start, self.end = learn.window(self.date)

    def test_both_queries_exclude_quarantined_and_missing_admission(self):
        for table in ('feedback_reports', 'usage_weeks'):
            sql = learn.sql_for(table, self.start, self.end)
            self.assertIn('where exists', sql)
            self.assertIn('c.install_id = ' + table + '.install_id and not c.quarantined', sql)
            self.assertIn('limit 5001', sql)

    def test_live_template_metrics_alert_and_zero_branches(self):
        for metrics, expected in [([], 'No budget overflow'), ([{'kind': 'feedback', 'overflow': 0}], '0 rejected reports'), ([{'kind': 'feedback', 'overflow': 111}, {'kind': 'usage', 'overflow': 3001}], 'Abuse alert:')]:
            with patch.object(learn, 'query', return_value=metrics) as query:
                brief, receipt = learn.draft(self.date, self.start, self.end, [], [], False)
            self.assertTrue(receipt['complete'])
            self.assertIn(expected, brief)
            self.assertIn('Quarantined installs', brief)
            self.assertIn("scope = 'global'", query.call_args.args[0])
            self.assertIn("week + interval '7 days' >", query.call_args.args[0])
            self.assertNotIn('INCOMPLETE', brief)

    def test_metric_shape_fails_without_echoing_untrusted_values(self):
        for row in [{'kind': 'private detail', 'overflow': 1}, {'kind': 'usage', 'overflow': 'private detail'}, {'kind': 'usage', 'overflow': True}, {'kind': 'usage', 'overflow': -1}, None]:
            with patch.object(learn, 'query', return_value=[row]):
                with self.assertRaisesRegex(learn.RunError, '^overflow_shape$'):
                    learn.draft(self.date, self.start, self.end, [], [], False)

    def test_complete_mocked_wrapper_reads_metrics_and_reuses_checkpoint(self):
        feedback, usage = learn.synthetic_rows(self.end)
        result = {'clusters': [{'topic': 'other', 'members': [f'r{i:04d}' for i in range(14)]}]}
        with tempfile.TemporaryDirectory(prefix='.d2-learn-', dir=Path(__file__).parent) as raw:
            root = Path(raw)
            (root / 'model.json').write_text((learn.ROOT / 'model.json').read_text())
            with patch.object(learn, 'ROOT', root), patch.object(learn, 'query', side_effect=[feedback, usage, [{'kind': 'feedback', 'overflow': 111}]]) as query, patch.object(learn, 'call_model', return_value=result), patch.object(learn, 'notify') as notify, patch.object(learn.dt, 'datetime', wraps=dt.datetime) as clock:
                clock.now.return_value = self.end + dt.timedelta(seconds=1)
                self.assertEqual(learn.main(['--date', str(self.date)]), 0)
                self.assertEqual(learn.main(['--date', str(self.date)]), 0)
                self.assertEqual(query.call_count, 3)
                self.assertEqual(notify.call_count, 1)
                brief = (root / 'briefs' / f'WC-Learn-{self.date}.md').read_text()
                self.assertIn('111 rejected reports', brief)
                self.assertIn('Abuse alert:', brief)


if __name__ == '__main__':
    unittest.main()
