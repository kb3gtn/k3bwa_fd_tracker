#!/usr/bin/env python3
"""
Import contacts from an N1MM Logger+ .s3db database into fieldday.db.

Usage:
    python import_n1mm.py <path-to-n1mm.s3db> [contest-name]

contest-name defaults to 'FD'. The import will offer to clear existing
contacts first or merge on top of them (duplicates are replaced by ID).
"""
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db

# Modes that are phone — in FD, N1MM puts the sent class in SNT for these
_PHONE_MODES = {"USB", "LSB", "FM", "AM", "SSB"}
_DIGI_MODES  = {"FT8", "FT4", "JS8", "RTTY", "PSK31", "PSK63", "DIG", "DIGI"}


def band_str(val):
    """Convert N1MM float band (14.0) to string key ('14')."""
    try:
        f = float(val)
        i = int(f)
        return str(i) if f == i else str(f)
    except (TypeError, ValueError):
        return str(val) if val else ""


def derive_class(row):
    """
    N1MM stores FD class differently by mode:
      - Phone/CW: Exchange1 has received class (e.g. '2A'), SNT has signal report
      - Digital:  SNT has sent class (e.g. '4A'), Exchange1 often empty
    Return best guess at received class, else empty string.
    """
    ex1 = (row.get("Exchange1") or "").strip()
    if ex1:
        return ex1
    # For digital modes SNT holds the sent class not a signal report
    snt  = (row.get("SNT") or "").strip()
    mode = (row.get("Mode") or "").upper()
    if mode in _DIGI_MODES and snt and not snt.isdigit() and len(snt) <= 4:
        return snt
    return ""


def map_row(row):
    """Map an N1MM DXLOG row dict to our fieldday.db schema."""
    ts = row.get("TS") or ""
    return {
        "ID":              row.get("ID") or "",
        "TS":              ts,
        "Timestamp":       ts,
        "Call":            row.get("Call") or "",
        "Operator":        row.get("Operator") or "",
        "Mode":            row.get("Mode") or "",
        "Band":            band_str(row.get("Band")),
        "Freq":            row.get("Freq") or 0.0,
        "QSXFreq":         row.get("QSXFreq") or 0.0,
        "SNT":             row.get("SNT") or "",
        "RCV":             row.get("RCV") or "",
        "SentNr":          str(row.get("SentNr") or ""),
        "rcvnr":           derive_class(row),
        "ContestName":     row.get("ContestName") or "",
        "ContestNR":       str(row.get("ContestNR") or ""),
        "CountryPrefix":   row.get("CountryPrefix") or "",
        "WPXPrefix":       row.get("WPXPrefix") or "",
        "StationPrefix":   row.get("StationPrefix") or "",
        "Continent":       (row.get("Continent") or "").strip(),
        "Sect":            (row.get("Sect") or "").strip(),
        "Prec":            row.get("Prec") or "",
        "CK":              str(row.get("CK") or ""),
        "ZN":              str(row.get("ZN") or ""),
        "IsMultiplier1":   int(row.get("IsMultiplier1") or 0),
        "IsMultiplier2":   int(row.get("IsMultiplier2") or 0),
        "IsMultiplier3":   int(row.get("isMultiplier3") or row.get("IsMultiplier3") or 0),
        "Points":          int(row.get("Points") or 0),
        "Exchange1":       (row.get("Exchange1") or "").strip(),
        "QTH":             (row.get("QTH") or "").strip(),
        "GridSquare":      (row.get("GridSquare") or "").strip(),
        "RoverLocation":   (row.get("RoverLocation") or "").strip(),
        "IsRunQSO":        int(row.get("IsRunQSO") or 0),
        "Run1Run2":        int(row.get("Run1Run2") or 0),
        "RadioNR":         int(row.get("RadioNR") or 1),
        "RadioInterfaced": int(row.get("RadioInterfaced") or 0),
        "IsOriginal":      int(row.get("IsOriginal") or 1),
        "CLAIMEDQSO":      int(row.get("CLAIMEDQSO") or 1),
    }


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <n1mm-database.s3db> [contest-name]")
        sys.exit(1)

    src_path     = sys.argv[1]
    contest_name = sys.argv[2] if len(sys.argv) > 2 else "FD"

    if not os.path.isfile(src_path):
        print(f"Error: file not found: {src_path}")
        sys.exit(1)

    # Read source
    src = sqlite3.connect(src_path)
    src.row_factory = sqlite3.Row
    rows = src.execute(
        "SELECT * FROM DXLOG WHERE ContestName = ? ORDER BY TS",
        (contest_name,)
    ).fetchall()
    src.close()

    if not rows:
        print(f"No contacts found for contest '{contest_name}' in {src_path}")
        sys.exit(0)

    print(f"Found {len(rows)} contacts for contest '{contest_name}' in {src_path}")

    # Ask clear or merge
    choice = input("Clear existing contacts before import? [y/N]: ").strip().lower()
    if choice == "y":
        with db._connect() as conn:
            existing = conn.execute("SELECT COUNT(*) FROM DXLOG").fetchone()[0]
            conn.execute("DELETE FROM DXLOG")
            conn.commit()
        print(f"Cleared {existing} existing contact(s).")

    # Import
    db.init_db()
    imported = 0
    skipped  = 0
    for row in rows:
        try:
            mapped = map_row(dict(row))
            if not mapped["ID"]:
                skipped += 1
                continue
            db.insert_contact(mapped)
            imported += 1
        except Exception as e:
            print(f"  Warning: skipped row ({row.get('Call','?')} @ {row.get('TS','?')}): {e}")
            skipped += 1

    print(f"Imported {imported} contact(s). Skipped {skipped}.")


if __name__ == "__main__":
    main()
