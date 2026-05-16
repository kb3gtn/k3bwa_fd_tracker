#!/usr/bin/env python3
"""
Import contacts from an ADIF file into fieldday.db.

Usage:
    python import_adif.py <logfile.adi>

Handles standard ADIF exports from N1MM, WSJT-X, Log4OM, and others.
The CLASS field is used for the received FD class; ARRL_SECT for the section.
"""
import sys
import os
import re
import hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db

# ADIF band string → integer MHz string (matches fieldday.db Band column)
_BAND_MAP = {
    "2190m": "0",
    "630m":  "0",
    "160m":  "1",
    "80m":   "3",
    "60m":   "5",
    "40m":   "7",
    "30m":   "10",
    "20m":   "14",
    "17m":   "18",
    "15m":   "21",
    "12m":   "24",
    "10m":   "28",
    "6m":    "50",
    "4m":    "70",
    "2m":    "144",
    "1.25m": "222",
    "70cm":  "432",
    "33cm":  "902",
    "23cm":  "1240",
}

# ADIF field regex: <NAME:length[:type]>value
_FIELD_RE = re.compile(r'<([^:>\s]+)(?::(\d+)(?::[^>]*)?)?>',  re.IGNORECASE)


def parse_adif(text):
    """Return a list of record dicts (field names uppercased) from ADIF text."""
    # Strip header (everything before <EOH>)
    eoh = re.search(r'<EOH>', text, re.IGNORECASE)
    body = text[eoh.end():] if eoh else text

    records = []
    for chunk in re.split(r'<EOR\s*>', body, flags=re.IGNORECASE):
        chunk = chunk.strip()
        if not chunk:
            continue
        rec = {}
        pos = 0
        for m in _FIELD_RE.finditer(chunk):
            name   = m.group(1).upper()
            length = int(m.group(2)) if m.group(2) else None
            start  = m.end()
            if length is not None:
                value = chunk[start : start + length]
            else:
                # No length: read until next tag or end
                nxt = _FIELD_RE.search(chunk, start)
                value = chunk[start : nxt.start() if nxt else len(chunk)]
            rec[name] = value.strip()
        if rec:
            records.append(rec)
    return records


def band_from_freq(freq_mhz):
    """Derive the band integer string from a frequency in MHz."""
    try:
        f = float(freq_mhz)
    except (TypeError, ValueError):
        return ""
    if   f <   2: return "1"
    elif f <   4: return "3"
    elif f <   6: return "5"
    elif f <   8: return "7"
    elif f <  12: return "10"
    elif f <  16: return "14"
    elif f <  20: return "18"
    elif f <  23: return "21"
    elif f <  26: return "24"
    elif f <  40: return "28"
    elif f <  60: return "50"
    elif f < 100: return "70"
    elif f < 200: return "144"
    elif f < 300: return "222"
    elif f < 600: return "432"
    elif f < 1000: return "902"
    else:          return "1240"


def make_timestamp(date_str, time_str):
    """Convert ADIF QSO_DATE (YYYYMMDD) + TIME_ON (HHMMSS or HHMM) to
    'YYYY-MM-DD HH:MM:SS'."""
    d = (date_str or "").strip()
    t = (time_str or "").strip().ljust(6, "0")[:6]
    if len(d) == 8:
        d = f"{d[:4]}-{d[4:6]}-{d[6:]}"
    return f"{d} {t[:2]}:{t[2:4]}:{t[4:6]}"


def make_id(rec):
    """Generate a stable hex ID from key QSO fields (no native ID in ADIF)."""
    key = "|".join([
        rec.get("CALL", ""),
        rec.get("QSO_DATE", ""),
        rec.get("TIME_ON", ""),
        rec.get("BAND", ""),
        rec.get("MODE", ""),
    ])
    return hashlib.md5(key.encode()).hexdigest()


def map_row(rec):
    """Map an ADIF record dict to the fieldday.db schema."""
    # Prefer FREQ (more precise) over the BAND label, fall back to BAND if no FREQ
    band = band_from_freq(rec.get("FREQ") or "") or \
           _BAND_MAP.get((rec.get("BAND") or "").lower(), "")

    ts = make_timestamp(rec.get("QSO_DATE"), rec.get("TIME_ON"))

    # FD class: standard ADIF field is CLASS; N1MM also exports APP_N1MM_EXCHANGE1
    fd_class = (
        rec.get("CLASS") or
        rec.get("APP_N1MM_EXCHANGE1") or
        ""
    ).strip()

    sect = (
        rec.get("ARRL_SECT") or
        rec.get("APP_N1MM_SECT") or
        ""
    ).strip().upper()

    operator = (
        rec.get("OPERATOR") or
        rec.get("STATION_CALLSIGN") or
        ""
    ).strip()

    # Prefer APP_N1MM_ID for round-trip stability; fall back to derived hash
    contact_id = rec.get("APP_N1MM_ID") or make_id(rec)

    try:
        freq = float(rec.get("FREQ") or 0.0)
    except ValueError:
        freq = 0.0

    return {
        "ID":              contact_id,
        "TS":              ts,
        "Timestamp":       ts,
        "Call":            (rec.get("CALL") or "").strip().upper(),
        "Operator":        operator,
        "Mode":            (rec.get("MODE") or "").strip().upper(),
        "Band":            band,
        "Freq":            freq,
        "QSXFreq":         float(rec.get("FREQ_RX") or freq),
        "SNT":             (rec.get("RST_SENT") or "").strip(),
        "RCV":             (rec.get("RST_RCVD") or "").strip(),
        "SentNr":          str(rec.get("STX") or ""),
        "rcvnr":           fd_class,
        "ContestName":     (rec.get("CONTEST_ID") or "FD").strip(),
        "ContestNR":       str(rec.get("SRX") or ""),
        "CountryPrefix":   (rec.get("COUNTRY") or "").strip(),
        "WPXPrefix":       (rec.get("APP_N1MM_WPXPREFIX") or "").strip(),
        "StationPrefix":   "",
        "Continent":       (rec.get("CONT") or "").strip(),
        "Sect":            sect,
        "Prec":            (rec.get("PRECEDENCE") or "").strip(),
        "CK":              str(rec.get("CHECK") or ""),
        "ZN":              str(rec.get("CQZ") or ""),
        "IsMultiplier1":   int(rec.get("APP_N1MM_ISMULTIPLIER1") or 0),
        "IsMultiplier2":   int(rec.get("APP_N1MM_ISMULTIPLIER2") or 0),
        "IsMultiplier3":   int(rec.get("APP_N1MM_ISMULTIPLIER3") or 0),
        "Points":          int(rec.get("APP_N1MM_POINTS") or 0),
        "Exchange1":       fd_class,
        "QTH":             (rec.get("QTH") or "").strip(),
        "GridSquare":      (rec.get("GRIDSQUARE") or "").strip(),
        "RoverLocation":   "",
        "IsRunQSO":        int(rec.get("APP_N1MM_ISRUNQSO") or 0),
        "Run1Run2":        0,
        "RadioNR":         1,
        "RadioInterfaced": 0,
        "IsOriginal":      1,
        "CLAIMEDQSO":      1,
    }


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <logfile.adi>")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    records = parse_adif(text)
    if not records:
        print(f"No ADIF records found in {path}")
        sys.exit(0)

    print(f"Found {len(records)} record(s) in {path}")

    choice = input("Clear existing contacts before import? [y/N]: ").strip().lower()
    if choice == "y":
        with db._connect() as conn:
            existing = conn.execute("SELECT COUNT(*) FROM DXLOG").fetchone()[0]
            conn.execute("DELETE FROM DXLOG")
            conn.commit()
        print(f"Cleared {existing} existing contact(s).")

    db.init_db()
    imported = 0
    skipped  = 0
    for rec in records:
        try:
            mapped = map_row(rec)
            if not mapped["Call"]:
                skipped += 1
                continue
            db.insert_contact(mapped)
            imported += 1
        except Exception as e:
            print(f"  Warning: skipped record "
                  f"({rec.get('CALL','?')} @ {rec.get('QSO_DATE','?')} "
                  f"{rec.get('TIME_ON','?')}): {e}")
            skipped += 1

    print(f"Imported {imported} contact(s). Skipped {skipped}.")


if __name__ == "__main__":
    main()
