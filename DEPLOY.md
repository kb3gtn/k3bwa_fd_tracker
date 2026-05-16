# Deployment Guide — Debian Minimal Install

Target: Debian 12 (Bookworm) minimal server, fresh install.

---

## 1. System packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv nginx
```

---

## 2. Create the service user

```bash
sudo useradd -r -m -d /webspaces -s /usr/sbin/nologin k3bwa
```

The `-r` flag creates a system account. The home directory `/webspaces` will
hold the project.

---

## 3. Deploy the project

```bash
sudo mkdir -p /webspaces
sudo chown k3bwa:k3bwa /webspaces

# Clone as root, then fix ownership — or su to k3bwa first
sudo -u k3bwa git clone <repo-url> /webspaces/hub.k3bwa.us
```

If the server has no internet access, copy the project directory instead:

```bash
sudo rsync -a ./hub.k3bwa.us/ k3bwa@<server>:/webspaces/hub.k3bwa.us/
```

---

## 4. Python virtual environment

```bash
sudo -u k3bwa bash -c "
  cd /webspaces/hub.k3bwa.us/webapp
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
"
```

Verify:

```bash
sudo -u k3bwa /webspaces/hub.k3bwa.us/webapp/.venv/bin/gunicorn --version
```

---

## 5. nginx

Remove the default symlink and install the site config:

```bash
sudo rm -f /etc/nginx/sites-enabled/default

# IP-based access (responds to any hostname / direct IP):
sudo cp /webspaces/hub.k3bwa.us/configuration/sites-available/default \
        /etc/nginx/sites-available/hub-fieldday

sudo ln -s /etc/nginx/sites-available/hub-fieldday \
           /etc/nginx/sites-enabled/hub-fieldday
```

> If you have a real DNS hostname, use `hub.k3bwa.us.conf` instead and update
> `server_name` to match your domain.

Test and reload:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## 6. systemd services

### Web app (gunicorn)

```bash
sudo cp /webspaces/hub.k3bwa.us/configuration/hub.k3bwa.us.service \
        /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now hub.k3bwa.us
sudo systemctl status hub.k3bwa.us
```

### UDP listener (N1MM contact receiver)

```bash
sudo cp /webspaces/hub.k3bwa.us/configuration/hub-listener.k3bwa.us.service \
        /etc/systemd/system/

sudo systemctl enable --now hub-listener.k3bwa.us
sudo systemctl status hub-listener.k3bwa.us
```

The database (`webapp/fieldday.db`) is created automatically on first start.

---

## 7. Firewall

If `ufw` or `nftables` is active, open HTTP and the N1MM UDP port:

```bash
# ufw
sudo ufw allow 80/tcp
sudo ufw allow 12060/udp
sudo ufw enable
```

```bash
# nftables (add to /etc/nftables.conf input chain)
tcp dport 80   accept
udp dport 12060 accept
```

---

## 8. Verify end-to-end

```bash
# Check both services are running
systemctl is-active hub.k3bwa.us hub-listener.k3bwa.us

# Hit the web app from the server itself
curl -s -o /dev/null -w "%{http_code}" http://localhost/
# Expected: 200

# Watch listener logs in real time
sudo journalctl -fu hub-listener.k3bwa.us
```

Open `http://<server-ip>/` in a browser — you should see the Field Day Tracker.

---

## 9. N1MM Logger+ configuration

In N1MM on the logging PC:

**Config → Configure Ports, Mode Control, Winkey, etc. → Broadcast Data tab**

| Setting | Value |
|---|---|
| Enabled | ✓ checked |
| Destination IP | `<server-ip>` or `239.255.255.0` (multicast) |
| Destination Port | `12060` |
| Contact broadcast | ✓ checked |

The listener joins the `239.255.255.0` multicast group and also accepts
directed unicast packets on port 12060.

---

## 10. Useful commands

| Task | Command |
|---|---|
| Restart web app | `sudo systemctl restart hub.k3bwa.us` |
| Restart listener | `sudo systemctl restart hub-listener.k3bwa.us` |
| Web app logs | `sudo journalctl -fu hub.k3bwa.us` |
| Listener logs | `sudo journalctl -fu hub-listener.k3bwa.us` |
| nginx logs | `sudo tail -f /var/log/nginx/error.log` |
| Clear contacts | `sudo -u k3bwa /webspaces/hub.k3bwa.us/webapp/.venv/bin/python /webspaces/hub.k3bwa.us/webapp/clear_contacts.py` |
| Import N1MM .s3db | `sudo -u k3bwa /webspaces/hub.k3bwa.us/webapp/.venv/bin/python /webspaces/hub.k3bwa.us/webapp/import_n1mm.py <file.s3db>` |
| Import ADIF | `sudo -u k3bwa /webspaces/hub.k3bwa.us/webapp/.venv/bin/python /webspaces/hub.k3bwa.us/webapp/import_adif.py <file.adi>` |

---

## Directory layout after deployment

```
/webspaces/hub.k3bwa.us/
├── configuration/          # Deployment config (already copied to system)
├── n1mm_examples/          # Reference material
├── static/                 # Served directly by nginx at /static/
│   ├── fonts.css
│   ├── fonts/
│   ├── files/              # Files distributed via the /files page
│   └── bwa_logo.png
└── webapp/
    ├── .venv/              # Python virtualenv (created in step 4)
    ├── fieldday.db         # SQLite database (created on first start)
    ├── app.py
    ├── listener.py
    ├── import_n1mm.py
    ├── import_adif.py
    └── ...
```
