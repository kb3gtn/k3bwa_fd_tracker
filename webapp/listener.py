#!/usr/bin/env python3
"""Standalone N1MM UDP listener — runs as a separate systemd service."""
import socket
import struct
import xml.etree.ElementTree as ET
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db

MCAST_GROUP = "239.255.255.0"
MCAST_PORT = 12060

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger(__name__)


def _get(root, tag, default=""):
    el = root.find(tag)
    return el.text.strip() if el is not None and el.text else default


def _freq_mhz(raw):
    # N1MM sends frequency in 10 Hz units (e.g. 1420000 → 14.200 MHz)
    try:
        return int(raw) / 100000.0
    except (ValueError, TypeError):
        return 0.0


def _int(val, default=0):
    try:
        return int(val or default)
    except (ValueError, TypeError):
        return default


def parse_contact(root):
    return {
        "ID":             _get(root, "ID"),
        "TS":             _get(root, "timestamp"),
        "Timestamp":      _get(root, "timestamp"),
        "Call":           _get(root, "call"),
        "Operator":       _get(root, "operator"),
        "Mode":           _get(root, "mode"),
        "Band":           _get(root, "band"),
        "Freq":           _freq_mhz(_get(root, "rxfreq", "0")),
        "QSXFreq":        _freq_mhz(_get(root, "txfreq", "0")),
        "SNT":            _get(root, "snt"),
        "RCV":            _get(root, "rcv"),
        "SentNr":         _get(root, "sntnr"),
        "rcvnr":          _get(root, "rcvnr"),
        "ContestName":    _get(root, "contestname"),
        "ContestNR":      _get(root, "contestnr"),
        "CountryPrefix":  _get(root, "countryprefix"),
        "WPXPrefix":      _get(root, "wpxprefix"),
        "StationPrefix":  _get(root, "stationprefix"),
        "Continent":      _get(root, "continent"),
        "Sect":           _get(root, "section"),
        "Prec":           _get(root, "prec"),
        "CK":             _get(root, "ck"),
        "ZN":             _get(root, "zone"),
        "IsMultiplier1":  _int(_get(root, "ismultiplier1")),
        "IsMultiplier2":  _int(_get(root, "ismultiplier2")),
        "IsMultiplier3":  _int(_get(root, "ismultiplier3")),
        "Points":         _int(_get(root, "points")),
        "Exchange1":      _get(root, "exchange1"),
        "QTH":            _get(root, "qth"),
        "GridSquare":     _get(root, "gridsquare"),
        "RoverLocation":  _get(root, "RoverLocation"),
        "IsRunQSO":       _int(_get(root, "IsRunQSO")),
        "Run1Run2":       _int(_get(root, "run1run2")),
        "RadioNR":        _int(_get(root, "radionr"), 1),
        "RadioInterfaced":_int(_get(root, "RadioInterfaced")),
        "IsOriginal":     1 if _get(root, "IsOriginal", "True").lower() == "true" else 0,
        "CLAIMEDQSO":     _int(_get(root, "IsClaimedQso"), 1),
    }


def handle_packet(data):
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        log.warning("XML parse error: %s", e)
        return

    tag = root.tag.lower()

    if tag in ("contactinfo", "contactreplace"):
        contact = parse_contact(root)
        db.insert_contact(contact)
        log.info("%s call=%s band=%s mode=%s sect=%s",
                 tag, contact["Call"], contact["Band"], contact["Mode"], contact["Sect"])

    elif tag == "contactdelete":
        contact_id = (root.findtext("ID") or "").strip()
        if contact_id:
            db.delete_contact(contact_id)
            log.info("contactdelete id=%s", contact_id)
        else:
            log.warning("contactdelete with no ID field")

    else:
        log.debug("ignored packet type: %s", tag)


def main():
    db.init_db()
    log.info("DB ready at %s", db.DB_PATH)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", MCAST_PORT))

    mreq = struct.pack("4sL", socket.inet_aton(MCAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    log.info("Listening on port %d (multicast group %s)", MCAST_PORT, MCAST_GROUP)

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            handle_packet(data.decode("utf-8", errors="replace"))
        except Exception as e:
            log.error("packet error: %s", e)


if __name__ == "__main__":
    main()
