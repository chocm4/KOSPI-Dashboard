"""
update_data.py
KOSPI 데이터를 yfinance로 수집해서 docs/kospi_data.json으로 저장합니다.
GitHub Actions 또는 로컬에서 수동 실행 모두 가능합니다.
"""

import json
import math
import os
import subprocess
import sys
from datetime import datetime, timedelta

try:
    import yfinance as yf
except ImportError:
    print("[설치] yfinance 모듈이 없습니다. 자동 설치합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "pandas"])
    import yfinance as yf


# ── 설정 ───────────────────────────────────────────────────────────
TICKER      = "^KS11"          # KOSPI 티커
PERIOD_DAYS = 15000            # 과거 몇 일치를 가져올지 (약 40년)
OUTPUT_PATH = "docs/kospi_data.json"


# ── 데이터 수집 ────────────────────────────────────────────────────
def fetch_kospi(period_days: int = PERIOD_DAYS) -> list[dict]:
    end   = datetime.today()
    start = end - timedelta(days=period_days)

    print(f"[yfinance] {TICKER} 데이터 수집 중... ({start.date()} ~ {end.date()})")
    df = yf.download(
        TICKER,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
    )

    if df.empty:
        raise ValueError("데이터를 가져오지 못했습니다. 티커나 네트워크를 확인하세요.")

    df = df.reset_index()

    # 컬럼 이름이 MultiIndex인 경우 평탄화
    if isinstance(df.columns, type(df.columns)) and hasattr(df.columns, 'droplevel'):
        try:
            df.columns = df.columns.droplevel(1)
        except Exception:
            pass

    records = []
    for _, row in df.iterrows():
        try:
            date_val = row["Date"]
            if hasattr(date_val, "strftime"):
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val)[:10]

            close = float(row["Close"])
            open_ = float(row.get("Open",  close))
            high  = float(row.get("High",  close))
            low   = float(row.get("Low",   close))
            vol   = float(row.get("Volume", 0))

            # NaN 포함 행 제외 (당일 미확정 데이터)
            if any(math.isnan(v) for v in [close, open_, high, low]):
                continue

            records.append({
                "date":   date_str,
                "open":   round(open_, 2),
                "high":   round(high,  2),
                "low":    round(low,   2),
                "close":  round(close, 2),
                "volume": int(vol),
            })
        except Exception as e:
            print(f"  ⚠ 행 파싱 오류 (건너뜀): {e}")
            continue

    records.sort(key=lambda x: x["date"])
    print(f"[yfinance] {len(records)}건 수집 완료")
    return records


# ── 저장 ───────────────────────────────────────────────────────────
def save_json(records: list[dict], path: str = OUTPUT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    payload = {
        "meta": {
            "ticker":     TICKER,
            "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "count":      len(records),
            "source":     "yfinance",
        },
        "data": records,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = os.path.getsize(path) / 1024
    print(f"[저장] {path}  ({size_kb:.1f} KB, {len(records)}건)")


# ── 메인 ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    records = fetch_kospi()
    save_json(records)
    print("✅ 완료")
