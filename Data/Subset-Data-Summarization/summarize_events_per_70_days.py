#!/usr/bin/env python3
# simple_per70_summary.py
#
# Minimal, readable pipeline:
#   1) load_clean_with_em_flag -> booking-level table with is_EM + day counts
#   2) add_cuts                -> labeled quartiles for LOS & age
#   3) summarize_per70_and_write -> per-70-day summaries to Excel (incl/excl EM)

import argparse
from pathlib import Path
import numpy as np
import pandas as pd


# ---------- helpers ----------

def _safe_qcut_with_labels(s: pd.Series, q=4, decimals=1, unit: str | None = None) -> pd.Categorical:
    """Robust quantile binning that never creates NaN categories; falls back to fewer bins."""
    x = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)
    valid = x.dropna()
    labeled = pd.Series(index=s.index, dtype="object")
    if valid.empty:
        return pd.Categorical(labeled)

    qs = np.linspace(0, 1, q + 1)
    edges = valid.quantile(qs).to_numpy()
    edges = np.unique(np.round(edges.astype(float), 8))  # dedupe/monotone
    if edges.size < 2:
        v = float(valid.iloc[0])
        lab = f"Q1: {v:.{decimals}f}–{v:.{decimals}f}" + (f" {unit}" if unit else "")
        labeled.loc[valid.index] = lab
        return pd.Categorical(labeled)

    L, R = edges[:-1], edges[1:]
    labels = [f"Q{i+1}: {a:.{decimals}f}–{b:.{decimals}f}" + (f" {unit}" if unit else "")
              for i, (a, b) in enumerate(zip(L, R))]
    cat = pd.cut(valid, bins=edges, include_lowest=True, right=True, labels=labels)
    labeled.loc[valid.index] = cat.astype("object")
    return pd.Categorical(labeled, categories=labels, ordered=True)


# ---------- 1) load + clean + EM flag ----------

def load_clean_with_em_flag(
    bookings_csv: str,
    events_csv: str,
    bed_moves_csv: str,
    court_prefix: str = "court a",
    em_pattern: str = "electronic monitoring",
) -> pd.DataFrame:
    """
    Returns booking-level table (Primary Group only) with:
      - booking_id, booking_date_time, length_of_stay
      - optional: gender, age_at_booking, most_severe_crime_time
      - days_with_bed_change / _incident / _infraction / _medical_visit
      - is_EM (bool) flagged from bed_move_event.cell
    """
    # bookings
    bookings = pd.read_csv(
        bookings_csv,
        dtype={"booking_id": "string", "group_type": "string"},
        parse_dates=["booking_date_time"],
        low_memory=False,
    )
    req = {"booking_id", "group_type", "booking_date_time", "length_of_stay"}
    miss = req - set(bookings.columns)
    if miss:
        raise ValueError(f"Missing columns in bookings.csv: {sorted(miss)}")

    # filter to Primary Group
    is_primary = bookings["group_type"].astype("string").str.strip().str.lower().eq("primary group")
    bookings = bookings.loc[is_primary].copy()

    # EM flag from bed moves
    bm = pd.read_csv(bed_moves_csv, dtype={"booking_id": "string", "cell": "string"}, low_memory=False)
    if "cell" not in bm.columns:
        raise ValueError("bed_move_event.csv must contain a 'cell' column")
    em_ids = set(
        bm.loc[bm["cell"].fillna("").str.lower().str.contains(em_pattern.lower()),
               "booking_id"].dropna().astype("string")
    )
    bookings["is_EM"] = bookings["booking_id"].isin(em_ids)

    # events -> daily flags -> day counts
    ev = pd.read_csv(
        events_csv,
        dtype={"booking_id": "string", "event_category": "string", "event_description": "string"},
        parse_dates=["event_date_time"],
        low_memory=False,
    )
    ev = ev[ev["booking_id"].isin(bookings["booking_id"])].copy()
    ev["event_date"] = ev["event_date_time"].dt.date
    cat = ev["event_category"].fillna("").str.strip().str.lower()
    desc = ev["event_description"].fillna("").str.strip().str.lower()

    daily = (
        pd.DataFrame({
            "booking_id": ev["booking_id"],
            "event_date": ev["event_date"],
            "had_bed_change": (cat == "bed_move_event"),
            "had_incident": desc.str.contains("incident", na=False),
            "had_infraction": desc.str.contains("infraction", na=False),
            "had_medical_visit": (desc == "medical"),
        })
        .groupby(["booking_id", "event_date"], as_index=False)
        .agg({  # convert per-day any() to 0/1
            "had_bed_change": "any",
            "had_incident": "any",
            "had_infraction": "any",
            "had_medical_visit": "any",
        })
    )
    for c in ["had_bed_change", "had_incident", "had_infraction", "had_medical_visit"]:
        daily[c] = daily[c].astype(int)

    day_counts = (
        daily.groupby("booking_id", as_index=False)[
            ["had_bed_change", "had_incident", "had_infraction", "had_medical_visit"]
        ].sum()
        .rename(columns={
            "had_bed_change": "days_with_bed_change",
            "had_incident": "days_with_incident",
            "had_infraction": "days_with_infraction",
            "had_medical_visit": "days_with_medical_visit",
        })
    )

    out = bookings.merge(day_counts, on="booking_id", how="left")
    for c in ["days_with_bed_change", "days_with_incident", "days_with_infraction", "days_with_medical_visit"]:
        out[c] = out[c].fillna(0)

    return out


# ---------- 2) add cuts (quartiles) ----------

def add_cuts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds labeled quartile columns:
      - los_quartile (days)
      - age_quartile (yrs)
    Robust to missing/constant values.
    """
    df = df.copy()
    df["los_quartile"] = _safe_qcut_with_labels(df["length_of_stay"], q=4, decimals=1, unit="days")
    if "age_at_booking" not in df.columns:
        df["age_at_booking"] = np.nan
    df["age_quartile"] = _safe_qcut_with_labels(df["age_at_booking"], q=4, decimals=0, unit="yrs")
    return df


# ---------- 3) summarize per-70 and write ----------

def _add_per70_rates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    los = pd.to_numeric(df["length_of_stay"], errors="coerce")
    los[los <= 0] = np.nan
    def _rate(col): return (pd.to_numeric(df[col], errors="coerce") / los) * 70.0
    df["rate70_bed_moves"]      = _rate("days_with_bed_change")
    df["rate70_incidents"]      = _rate("days_with_incident")
    df["rate70_infractions"]    = _rate("days_with_infraction")
    df["rate70_medical_visits"] = _rate("days_with_medical_visit")
    return df

def _summarize(df: pd.DataFrame, by_col: str, breakout_name: str) -> pd.DataFrame:
    rate_cols = ["rate70_bed_moves", "rate70_incidents", "rate70_infractions", "rate70_medical_visits"]
    grp = (
        df.groupby(by_col, dropna=False)[rate_cols]
          .mean(numeric_only=True)
          .reset_index()
          .rename(columns={by_col: "category"})
    )
    counts = df.groupby(by_col, dropna=False)["booking_id"].nunique().reset_index(name="n_bookings")
    out = grp.merge(counts, left_on="category", right_on=by_col, how="left").drop(columns=[by_col])
    out.insert(0, "breakout", breakout_name)
    out["category"] = out["category"].astype("string")
    return out

def _build_summary(df: pd.DataFrame) -> pd.DataFrame:
    df = _add_per70_rates(df)
    for col in ["gender", "most_severe_crime_time"]:
        if col not in df.columns:
            df[col] = np.nan

    parts = [
        _summarize(df, "los_quartile", "length_of_stay_quartile"),
        _summarize(df, "gender", "gender"),
        _summarize(df, "age_quartile", "age_at_booking_quartile")
    ]
    overall = pd.DataFrame({
        "breakout": ["overall"],
        "category": ["All bookings"],
        "n_bookings": [df["booking_id"].nunique()],
        "rate70_bed_moves": [df["rate70_bed_moves"].mean(numeric_only=True)],
        "rate70_incidents": [df["rate70_incidents"].mean(numeric_only=True)],
        "rate70_infractions": [df["rate70_infractions"].mean(numeric_only=True)],
        "rate70_medical_visits": [df["rate70_medical_visits"].mean(numeric_only=True)],
    })
    summary = pd.concat(parts + [overall], ignore_index=True)
    cols = ["breakout", "category", "n_bookings",
            "rate70_bed_moves", "rate70_incidents", "rate70_infractions", "rate70_medical_visits"]
    return summary[cols]

def summarize_per70_and_write(df: pd.DataFrame, xlsx_path: str) -> None:
    """
    Splits by is_EM, creates per-70 summaries for each, writes to one Excel with two sheets.
    """
    df = add_cuts(df)

    df_incl = df.copy()
    df_excl = df.loc[~df["is_EM"].fillna(False)].copy()

    summ_incl = _build_summary(df_incl)
    summ_excl = _build_summary(df_excl)

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as w:
        summ_incl.to_excel(w, index=False, sheet_name="summary_including_EM")
        summ_excl.to_excel(w, index=False, sheet_name="summary_excluding_EM")

    print(f"✅ Wrote {xlsx_path}")
    print(f"   • summary_including_EM rows: {len(summ_incl)}  (bookings n={df_incl['booking_id'].nunique()})")
    print(f"   • summary_excluding_EM rows: {len(summ_excl)}  (bookings n={df_excl['booking_id'].nunique()})")


# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser(description="Per-70-day summaries (incl/excl EM) with simple, readable steps.")
    ap.add_argument("--data-dir", default=".", help="Directory containing bookings.csv, events_log.csv, bed_move_event.csv")
    ap.add_argument("--bookings", help="Override path to bookings.csv")
    ap.add_argument("--events", help="Override path to events_log.csv")
    ap.add_argument("--bed-moves", help="Override path to bed_move_event.csv")
    ap.add_argument("--xlsx", default="per70_summary.xlsx", help="Output Excel path")
    ap.add_argument("--em-pattern", default="electronic monitoring", help="Substring in bed_move_event.cell to flag EM")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    bookings_csv = args.bookings or (data_dir / "bookings.csv")
    events_csv   = args.events   or (data_dir / "events_log.csv")
    bed_moves_csv= args.bed_moves or (data_dir / "bed_move_event.csv")

    for p in [bookings_csv, events_csv, bed_moves_csv]:
        if not Path(p).exists():
            raise SystemExit(f"❌ Missing input file: {p}")

    # 1) load/clean, filter Primary Group, add is_EM, day counts
    df = load_clean_with_em_flag(
        bookings_csv=str(bookings_csv),
        events_csv=str(events_csv),
        bed_moves_csv=str(bed_moves_csv),
        em_pattern=args.em_pattern,
    )

    # 3) summarize + write (2) handles cuts internally
    summarize_per70_and_write(df, xlsx_path=args.xlsx)


if __name__ == "__main__":
    main()
