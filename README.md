# K3BWA ARRL Field Day Tracker

A Flask web application that listens for UDP multicast packets from [N1MM Logger+](https://n1mmwp.hamdocs.com/) and displays a live Field Day contact dashboard served via nginx and gunicorn.

## Features

- Receives N1MM contact events (add, update, delete) over UDP multicast on port 12060
- Stores contacts in a local SQLite database
- Rolling 5-page display that auto-rotates:
  - **Page 1** (5 s) — ARRL section tracker (worked/unworked chips) + last 10 contacts
  - **Page 2** (5 s) — Contact statistics by mode, band, and operator
  - **Page 3** (15 s) — Field Day overview
  - **Page 4** (15 s) — Club info page
  - **Page 5** — File distribution listing (skipped in auto-rotation; accessible when paused)
- Day/night theme toggle with localStorage persistence
- UTC clock with seconds in the header
- Pause/Resume/Next controls on the rotation bar; paused state persists across page changes

---

## Directory Structure

```
.
├── configuration/                  # Deployment config files (not auto-installed)
│   ├── hub.k3bwa.us.service        # systemd unit for gunicorn
│   ├── hub-listener.k3bwa.us.service  # systemd unit for UDP listener
│   └── sites-available/
│       ├── hub.k3bwa.us.conf       # nginx named vhost
│       └── default                 # nginx default server (IP access)
├── n1mm_examples/                  # Reference material
│   ├── udp_packet_examples.txt     # Sample N1MM UDP XML packets
│   ├── arrl_tracker.html           # Original design reference
│   └── ham_test.s3db               # Sample N1MM database
├── static/                         # Static files served directly by nginx
│   ├── fonts.css                   # Local @font-face declarations
│   ├── fonts/                      # Self-hosted web fonts
│   │   ├── orbitron.woff2
│   │   └── share-tech-mono.woff2
│   ├── files/                      # Files distributed via the /files page
│   └── bwa_logo.png                # Club logo
├── webapp/
│   ├── app.py                      # Flask routes (read-only from DB)
│   ├── listener.py                 # Standalone UDP listener (writes to DB)
│   ├── db.py                       # SQLite schema and query helpers
│   ├── arrl_sections.py            # ARRL/RAC section definitions and band map
│   ├── clear_contacts.py           # Utility: wipe all contacts from the DB
│   ├── import_n1mm.py              # Utility: import contacts from an N1MM .s3db file
│   ├── wsgi.py                     # Gunicorn entry point
│   ├── requirements.txt
│   └── templates/
│       ├── base.html               # Shared layout, theme toggle, rotation timer
│       ├── tracker.html            # Page 1: section grid + contact log
│       ├── stats.html              # Page 2: QSO statistics
│       ├── fieldday.html           # Page 3: Field Day explanation
│       ├── club.html               # Page 4: Club info
│       └── files.html              # Page 5: File distribution listing
└── .gitignore
```

---

## Setup

### 1. Python environment

```bash
cd webapp
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. nginx

Copy (or symlink) the appropriate config and reload:

```bash
# Named vhost
sudo cp configuration/sites-available/hub.k3bwa.us.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/hub.k3bwa.us.conf /etc/nginx/sites-enabled/

# Or use the default server block for IP access
sudo cp configuration/sites-available/default /etc/nginx/sites-available/default

sudo nginx -t && sudo systemctl reload nginx
```

### 3. systemd services

Two services run independently so gunicorn workers remain read-only:

```bash
# Web app (gunicorn)
sudo cp configuration/hub.k3bwa.us.service /etc/systemd/system/
sudo systemctl enable --now hub.k3bwa.us

# UDP listener (writes to DB)
sudo cp configuration/hub-listener.k3bwa.us.service /etc/systemd/system/
sudo systemctl enable --now hub-listener.k3bwa.us
```

The SQLite database (`webapp/fieldday.db`) is created automatically on first start.

### 4. N1MM Logger+ configuration

In N1MM: **Config → Configure Ports, Mode Control, Winkey, etc. → Broadcast Data**

Enable contact broadcasts and set the destination IP to the server running this app. N1MM defaults to multicast group `239.255.255.0` port `12060`, which matches the listener.

---

## Development

Run the Flask app locally (no gunicorn needed):

```bash
cd webapp
.venv/bin/python app.py
```

Run the listener in a separate terminal:

```bash
cd webapp
.venv/bin/python listener.py
```

Watch listener logs in production:

```bash
sudo journalctl -fu hub-listener.k3bwa.us
```

Clear all contacts from the database:

```bash
cd webapp
.venv/bin/python clear_contacts.py
```

---

## Importing from an N1MM Database

If you need to pre-load contacts from an existing N1MM Logger+ database (e.g. to restore after a reset during the event), use `import_n1mm.py`:

```bash
cd webapp

# Import FD contacts (default contest name "FD")
.venv/bin/python import_n1mm.py /path/to/n1mm-log.s3db

# Explicit contest name
.venv/bin/python import_n1mm.py /path/to/n1mm-log.s3db FD
```

The script will:
1. Read all `DXLOG` rows matching the given contest name from the source `.s3db` file.
2. Ask whether to clear existing contacts first or merge on top of them (duplicates replaced by ID).
3. Import the contacts into `fieldday.db`, mapping N1MM schema differences automatically.

Schema differences handled:
- `Band` stored as a float in N1MM (`14.0`) is converted to the string key used by this app (`"14"`).
- `rcvnr` (received FD class) is derived from `Exchange1`; for digital modes it falls back to `SNT` when `Exchange1` is empty.
- `isMultiplier3` case variation is handled.

---

## N1MM UDP Packet Reference

N1MM broadcasts three XML message types on UDP port 12060:

| Tag | Event |
|---|---|
| `<contactinfo>` | New contact logged |
| `<contactreplace>` | Existing contact edited |
| `<contactdelete>` | Contact deleted |

Full schema: https://n1mmwp.hamdocs.com/appendices/external-udp-broadcasts/

---

## License

MIT
