"""Synthetic fixture only; no real assets or true failure labels."""
import csv
from pathlib import Path
from datetime import datetime, timedelta, timezone
from .monitor import Reading, mark_anomalies, VERSION
from hashlib import sha256
import json


def generate_readings():
    start=datetime(2026, 1, 1, tzinfo=timezone.utc)
    result=[]
    for i in range(72):
        t=start+timedelta(hours=i)
        a=2.00+0.04*((i%5)-2) + (1.7 if 40 <= i < 48 else 0)
        b=2.20+0.04*((i%5)-2)
        result.append(Reading("DEMO-A",t,round(a,4),45.0,"RUN"))
        result.append(Reading("DEMO-B",t,round(b,4),44.0,"RUN"))
    # ordered strictly per asset even when assets interleave
    return result


def run_demo(outdir):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    readings=generate_readings()
    inputp=out/'synthetic_sensor_readings.csv'
    with inputp.open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f,lineterminator='\n')
        writer.writerow(['asset_id','observed_at','vibration_mm_s','temp_c','operating_state'])
        for r in readings:
            writer.writerow([r.asset_id,r.observed_at.isoformat(),r.vibration_mm_s,r.temp_c,r.operating_state])
    results=mark_anomalies(readings)
    alerts=[r for r in results if r['status']=='REVIEW_REQUIRED']
    report={
        'project':'I16',
        'kind':'SYNTHETIC_DEMONSTRATION_NOT_REAL_FAILURE_PREDICTION',
        'algorithm_version':VERSION,
        'input_sha256':sha256(inputp.read_bytes()).hexdigest(),
        'sample_count':len(readings),
        'asset_count':len(set(r.asset_id for r in readings)),
        'review_alert_count':len(alerts),
        'alerts':alerts,
        'gates_approved':[],
        'business_impact':'NOT_MEASURED'
    }
    p=out/'report.json'
    p.write_text(json.dumps(report,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report
