import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fieldday.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS DXLOG (
    ID            TEXT PRIMARY KEY,
    TS            TEXT,
    Timestamp     TEXT,
    Call          TEXT,
    Operator      TEXT,
    Mode          TEXT,
    Band          TEXT,
    Freq          REAL,
    QSXFreq       REAL,
    SNT           TEXT,
    RCV           TEXT,
    SentNr        TEXT,
    rcvnr         TEXT,
    ContestName   TEXT,
    ContestNR     TEXT,
    CountryPrefix TEXT,
    WPXPrefix     TEXT,
    StationPrefix TEXT,
    Continent     TEXT,
    Sect          TEXT,
    Prec          TEXT,
    CK            TEXT,
    ZN            TEXT,
    IsMultiplier1 INTEGER DEFAULT 0,
    IsMultiplier2 INTEGER DEFAULT 0,
    IsMultiplier3 INTEGER DEFAULT 0,
    Points        INTEGER DEFAULT 0,
    Exchange1     TEXT,
    QTH           TEXT,
    GridSquare    TEXT,
    RoverLocation TEXT,
    IsRunQSO      INTEGER DEFAULT 0,
    Run1Run2      INTEGER DEFAULT 0,
    RadioNR       INTEGER DEFAULT 1,
    RadioInterfaced INTEGER DEFAULT 0,
    IsOriginal    INTEGER DEFAULT 1,
    CLAIMEDQSO    INTEGER DEFAULT 1
)
"""


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(_SCHEMA)
        conn.commit()


def insert_contact(data):
    sql = """
        INSERT OR REPLACE INTO DXLOG (
            ID, TS, Timestamp, Call, Operator, Mode, Band, Freq, QSXFreq,
            SNT, RCV, SentNr, rcvnr, ContestName, ContestNR, CountryPrefix,
            WPXPrefix, StationPrefix, Continent, Sect, Prec, CK, ZN,
            IsMultiplier1, IsMultiplier2, IsMultiplier3, Points,
            Exchange1, QTH, GridSquare, RoverLocation, IsRunQSO,
            Run1Run2, RadioNR, RadioInterfaced, IsOriginal, CLAIMEDQSO
        ) VALUES (
            :ID, :TS, :Timestamp, :Call, :Operator, :Mode, :Band, :Freq, :QSXFreq,
            :SNT, :RCV, :SentNr, :rcvnr, :ContestName, :ContestNR, :CountryPrefix,
            :WPXPrefix, :StationPrefix, :Continent, :Sect, :Prec, :CK, :ZN,
            :IsMultiplier1, :IsMultiplier2, :IsMultiplier3, :Points,
            :Exchange1, :QTH, :GridSquare, :RoverLocation, :IsRunQSO,
            :Run1Run2, :RadioNR, :RadioInterfaced, :IsOriginal, :CLAIMEDQSO
        )
    """
    with _connect() as conn:
        conn.execute(sql, data)
        conn.commit()


def delete_contact(contact_id):
    with _connect() as conn:
        conn.execute("DELETE FROM DXLOG WHERE ID = ?", (contact_id,))
        conn.commit()


def get_recent_contacts(limit=10):
    with _connect() as conn:
        rows = conn.execute(
            """SELECT Timestamp, Call, Band, Mode,
                      COALESCE(NULLIF(Exchange1,''), NULLIF(rcvnr,'')) AS Class,
                      Sect, Operator
               FROM DXLOG
               ORDER BY TS DESC
               LIMIT ?""",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_worked_sections():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT Sect FROM DXLOG WHERE Sect IS NOT NULL AND Sect != ''"
        ).fetchall()
    return {row["Sect"].strip().upper() for row in rows}


def get_stats():
    with _connect() as conn:
        by_mode = conn.execute(
            """SELECT
                CASE
                    WHEN UPPER(Mode) IN ('USB','LSB','FM','AM','SSB') THEN 'Phone'
                    WHEN UPPER(Mode) IN ('DIG','DIGI') THEN 'Digital'
                    ELSE Mode
                END AS Mode,
                COUNT(*) as count
               FROM DXLOG
               GROUP BY 1
               ORDER BY count DESC"""
        ).fetchall()
        by_operator = conn.execute(
            "SELECT Operator, COUNT(*) as count FROM DXLOG GROUP BY Operator ORDER BY count DESC"
        ).fetchall()
        by_band = conn.execute(
            "SELECT Band, COUNT(*) as count FROM DXLOG GROUP BY Band ORDER BY count DESC"
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) as count FROM DXLOG").fetchone()["count"]
        points_row = conn.execute("SELECT SUM(Points) as pts FROM DXLOG").fetchone()
        points = points_row["pts"] or 0
    return {
        "total": total,
        "points": points,
        "by_mode": [dict(r) for r in by_mode],
        "by_operator": [dict(r) for r in by_operator],
        "by_band": [dict(r) for r in by_band],
    }
