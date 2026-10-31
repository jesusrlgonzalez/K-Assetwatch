import math,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from sys import path
path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from i16.monitor import Reading, validate_readings, mark_anomalies
from i16.demo import generate_readings

T=datetime(2026,1,1,tzinfo=timezone.utc)

class TestMonitor(unittest.TestCase):
    def test_demo_has_alert(self):
        results=mark_anomalies(generate_readings())
        self.assertGreater(sum(x['status']=='REVIEW_REQUIRED' for x in results),0)
    def test_stable_asset_not_alerting(self):
        results=mark_anomalies(generate_readings())
        self.assertEqual(sum(x['status']=='REVIEW_REQUIRED' for x in results if x['asset_id']=='DEMO-B'),0)
    def test_determinism(self):
        data=generate_readings()
        self.assertEqual(mark_anomalies(data),mark_anomalies(data))
    def test_future_suffix_does_not_change_prefix(self):
        data=generate_readings()
        base=mark_anomalies(data[:80]);later=mark_anomalies(data)
        self.assertEqual(base,later[:80])
    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            validate_readings([Reading('A',datetime(2026,1,1),1.0,25,'RUN')])
    def test_duplicate_timestamp_rejected(self):
        r=Reading('A',T,1.0,25,'RUN')
        with self.assertRaises(ValueError):
            validate_readings([r,r])
    def test_reverse_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            validate_readings([Reading('A',T+timedelta(hours=1),1.0,25,'RUN'),Reading('A',T,1.0,25,'RUN')])
    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            validate_readings([Reading('A',T,math.nan,25,'RUN')])
    def test_negative_vibration_rejected(self):
        with self.assertRaises(ValueError):
            validate_readings([Reading('A',T,-1.0,25,'RUN')])
    def test_bad_temperature_rejected(self):
        with self.assertRaises(ValueError):
            validate_readings([Reading('A',T,1.0,900,'RUN')])
    def test_unknown_state_rejected(self):
        with self.assertRaises(ValueError):
            validate_readings([Reading('A',T,1.0,25,'MAINT')])
    def test_off_abstains(self):
        results=mark_anomalies([Reading('A',T,1.0,25,'OFF')])
        self.assertEqual(results[0]['status'],'ABSTAIN')
    def test_insufficient_history_not_alert(self):
        results=mark_anomalies(generate_readings()[:10])
        self.assertTrue(all(x['status']=='NO_EVIDENCE' for x in results))
    def test_bad_monitor_params_rejected(self):
        with self.assertRaises(ValueError):
            mark_anomalies(generate_readings(),min_history=0)

if __name__=='__main__':unittest.main()
