# Deploy: budget.thelastindex.com

Stack: FastAPI + SQLite, uvicorn behind nginx.
Auth: HTTP Basic Auth at the nginx layer.

---

## 1. Copy files to VPS

```bash
scp -r budget-app/ zero@thelastindex.com:/var/www/budget
```

---

## 2. Python environment

```bash
cd /var/www/budget
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

---

## 3. Permissions

```bash
sudo chown -R www-data:www-data /var/www/budget
sudo chmod 750 /var/www/budget
```

`budget.db` is created automatically on first start.

---

## 4. systemd service

```bash
sudo cp budget.service /etc/systemd/system/budget.service
sudo systemctl daemon-reload
sudo systemctl enable --now budget
sudo systemctl status budget
```

---

## 5. HTTP Basic Auth

```bash
sudo apt install apache2-utils

# your account
sudo htpasswd -c /etc/nginx/.htpasswd-budget zero

# add second user (no -c, that would overwrite)
sudo htpasswd /etc/nginx/.htpasswd-budget <girlfriend>
```

---

## 6. nginx

```bash
sudo cp nginx-budget.conf /etc/nginx/sites-available/budget
sudo ln -s /etc/nginx/sites-available/budget /etc/nginx/sites-enabled/budget
sudo nginx -t && sudo systemctl reload nginx
```

The conf assumes your existing wildcard/root cert at
`/etc/letsencrypt/live/thelastindex.com/`. Adjust the cert paths if yours differ.

---

## 7. DNS

Add an A (or CNAME) record:

```
budget.thelastindex.com  →  <VPS IP>
```

---

## Logs

```bash
sudo journalctl -u budget -f
```
