"""Deterministic *causal* anomaly marker for synthetic vibration data.

NOT a failure predictor, not real-time capable, not cleared for SCADA.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from collections import defaultdict, deque
from math import isfinite
from statistics import median
from typing import Iterable

VERSION = "baseline-mad-v0.1"

@dataclass(frozen=True)
class Reading:
    asset_id: str
    observed_at: datetime
    vibration_mm_s: float
    temp_c: float
    operating_state: str


def validate_readings(readings: Iterable[Reading]):
    last_by_asset = {}
    out = []
    for r in readings:
        if not isinstance(r, Reading):
            raise ValueError("Expected Reading")
        if not r.asset_id or not isinstance(r.asset_id, str):
            raise ValueError("Missing asset_id")
        if not isinstance(r.observed_at, datetime) or r.observed_at.tzinfo is None or r.observed_at.utcoffset() is None:
            raise ValueError("Timestamp must carry a timezone")
        dt = r.observed_at.astimezone(timezone.utc)
        if r.asset_id in last_by_asset and dt <= last_by_asset[r.asset_id]:
            raise ValueError("Duplicate/non-monotonic (asset_id, timestamp)")
        last_by_asset[r.asset_id] = dt
        if not isinstance(r.vibration_mm_s,(int,float)) or not isfinite(r.vibration_mm_s) or r.vibration_mm_s < 0:
            raise ValueError("Invalid vibration")
        if not isinstance(r.temp_c,(int,float)) or not isfinite(r.temp_c) or not -40 <= r.temp_c <= 200:
            raise ValueError("Invalid temperature")
        if r.operating_state not in {"RUN", "OFF"}:
            raise ValueError("Unknown operating state")
        out.append(Reading(r.asset_id, dt, float(r.vibration_mm_s), float(r.temp_c), r.operating_state))
    return out


def mark_anomalies(readings: Iterable[Reading], min_history=12, history_len=24, consecutive_required=2, cooldown_steps=6):
    """Every output for time t is based on observations with time <= t only.

    Rolling median/MAD computed solely from historic RUN values. This is
    a demo flagging unexpected vibration, never forecasting a failure.
    """
    if min_history < 3 or history_len < min_history or consecutive_required < 1 or cooldown_steps < 0:
        raise ValueError("Invalid monitor parameters")
    history = defaultdict(lambda: deque(maxlen=history_len))
    streak = defaultdict(int)
    cooldown = defaultdict(int)
    results = []
    for r in validate_readings(readings):
        result = {"asset_id":r.asset_id,"observed_at":r.observed_at.isoformat(),
                  "status":"NO_EVIDENCE","reason":"insufficient_history"}
        if r.operating_state != "RUN":
            streak[r.asset_id]=0
            result.update(status="ABSTAIN",reason="asset_not_running")
            results.append(result)
            continue
        prev = history[r.asset_id]
        if len(prev) >= min_history:
            med=median(prev)
            mad=median(abs(x-med) for x in prev)
            # 0.8 mm/s minimum demo threshold avoids zero-MAD explosion.
            gap=max(0.8,5.0*1.4826*mad)
            anomalous = r.vibration_mm_s > med + gap
            streak[r.asset_id] = streak[r.asset_id]+1 if anomalous else 0
            if cooldown[r.asset_id] > 0:
                cooldown[r.asset_id]-=1
                result.update(status="NORMAL",reason="cooldown_suppression")
            elif streak[r.asset_id]>=consecutive_required:
                result.update(status="REVIEW_REQUIRED",reason="persistent_high_vibration")
                streak[r.asset_id]=0
                cooldown[r.asset_id]=cooldown_steps
            else:
                result.update(status="NORMAL",reason="no_persistent_alert")
        prev.append(r.vibration_mm_s)  # appended AFTER classification
        results.append(result)
    return results
