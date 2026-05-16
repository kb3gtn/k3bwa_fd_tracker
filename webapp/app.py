from flask import Flask, redirect, render_template, request, session, flash
from werkzeug.utils import secure_filename
import db
import os
from arrl_sections import SECTIONS, ALL_SECTIONS, BAND_NAMES

# ── Station configuration ──────────────────────────────────────────────────
STATION_CALL    = "K3BWA"
UPLOAD_PASSWORD = "k3bwa_upload"
SECRET_KEY      = "fd-tracker-k3bwa-secret"   # fixed key is fine for LAN use
# ──────────────────────────────────────────────────────────────────────────

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "files")

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024   # 4 MB
db.init_db()

import datetime

@app.template_filter("datetimeformat")
def datetimeformat(ts):
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


@app.context_processor
def inject_globals():
    return {"station_call": STATION_CALL}


@app.route("/")
def index():
    return redirect("/tracker")


@app.route("/tracker")
def tracker():
    worked = db.get_worked_sections()
    total = len(ALL_SECTIONS)
    worked_count = sum(1 for abbr, _ in ALL_SECTIONS if abbr in worked)
    pct = round(worked_count / total * 100) if total else 0
    return render_template(
        "tracker.html",
        sections=SECTIONS,
        worked=worked,
        total=total,
        worked_count=worked_count,
        pct=pct,
        contacts=db.get_recent_contacts(),
        band_names=BAND_NAMES,
        next_url="/stats",
        page_label="Page 1 of 5",
        dwell_ms=5000,
    )


@app.route("/stats")
def stats():
    data = db.get_stats()
    return render_template(
        "stats.html",
        stats=data,
        band_names=BAND_NAMES,
        next_url="/fieldday",
        page_label="Page 2 of 5",
        dwell_ms=5000,
    )


@app.route("/fieldday")
def fieldday():
    return render_template(
        "fieldday.html",
        next_url="/club",
        page_label="Page 3 of 5",
        dwell_ms=15000,
    )


@app.route("/club")
def club():
    return render_template(
        "club.html",
        next_url="/files",
        page_label="Page 4 of 5",
        dwell_ms=15000,
    )


@app.route("/files")
def files():
    entries = []
    for name in sorted(os.listdir(STATIC_DIR)):
        if name.startswith("."):
            continue
        path = os.path.join(STATIC_DIR, name)
        if os.path.isfile(path):
            stat = os.stat(path)
            entries.append({
                "name": name,
                "size": _human_size(stat.st_size),
                "mtime": stat.st_mtime,
            })
    return render_template(
        "files.html",
        entries=entries,
        logged_in=session.get("upload_auth", False),
        next_url="/tracker",
        page_label="Page 5 of 5",
        dwell_ms=0,
    )


@app.route("/files/login", methods=["POST"])
def files_login():
    if request.form.get("password") == UPLOAD_PASSWORD:
        session["upload_auth"] = True
    else:
        flash("Incorrect password.")
    return redirect("/files")


@app.route("/files/logout", methods=["POST"])
def files_logout():
    session.pop("upload_auth", None)
    return redirect("/files")


@app.route("/files/upload", methods=["POST"])
def files_upload():
    if not session.get("upload_auth"):
        return redirect("/files")
    f = request.files.get("file")
    if not f or not f.filename:
        flash("No file selected.")
        return redirect("/files")
    name = secure_filename(f.filename)
    if not name or name.startswith("."):
        flash("Invalid filename.")
        return redirect("/files")
    f.save(os.path.join(STATIC_DIR, name))
    flash(f"Uploaded: {name}")
    return redirect("/files")


@app.errorhandler(413)
def upload_too_large(e):
    flash("File too large — 4 MB maximum.")
    return redirect("/files")


def _human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} TB"


if __name__ == "__main__":
    app.run(debug=True)
