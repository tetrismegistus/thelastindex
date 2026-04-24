"""
budget web app — FastAPI + SQLite
Serves the dashboard UI and exposes a JSON API for CRUD on budget data.
Auth is handled entirely by nginx (HTTP Basic), so no auth logic here.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── budget logic (copied verbatim from budget.py, minus file I/O) ────────────

import calendar
from dataclasses import dataclass, field
from enum import Enum


class Freq(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


def _add_months(d: date, n: int) -> date:
    month = d.month - 1 + n
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _snap_to_weekday(anchor: date, weekday: int) -> date:
    days_ahead = (weekday - anchor.weekday()) % 7
    return anchor + timedelta(days=days_ahead)


@dataclass
class RecurringExpense:
    name: str
    amount: float
    freq: Freq
    anchor: Optional[date]
    end: Optional[date] = None
    category: str = "expense"
    weekday: Optional[int] = None

    def occurrences_in(self, start: date, end: date) -> list[date]:
        if self.anchor is None:
            return []
        anchor = self.anchor
        if self.weekday is not None and self.freq in (Freq.WEEKLY, Freq.BIWEEKLY):
            anchor = _snap_to_weekday(anchor, self.weekday)
        results = []
        cur = anchor
        if self.freq in (Freq.WEEKLY, Freq.BIWEEKLY):
            step = 7 if self.freq == Freq.WEEKLY else 14
            while cur < start:
                cur += timedelta(days=step)
            while cur <= end:
                if self.end is None or cur <= self.end:
                    results.append(cur)
                cur += timedelta(days=step)
        else:
            months_step = {Freq.MONTHLY: 1, Freq.QUARTERLY: 3, Freq.ANNUAL: 12}[self.freq]
            while cur < start:
                cur = _add_months(cur, months_step)
            while cur <= end:
                if self.end is None or cur <= self.end:
                    results.append(cur)
                cur = _add_months(cur, months_step)
        return results


@dataclass
class OneOffExpense:
    name: str
    amount: float
    on: Optional[date]
    category: str = "one-off"

    def occurrences_in(self, start: date, end: date) -> list[date]:
        if self.on is None:
            return []
        return [self.on] if start <= self.on <= end else []


@dataclass
class IncomeStream:
    name: str
    net: float
    freq: Freq
    anchor: Optional[date]
    end: Optional[date] = None
    weekday: Optional[int] = None

    def occurrences_in(self, start: date, end: date) -> list[date]:
        if self.anchor is None:
            return []
        proxy = RecurringExpense(
            name=self.name, amount=self.net, freq=self.freq,
            anchor=self.anchor, end=self.end, weekday=self.weekday,
        )
        return proxy.occurrences_in(start, end)


def project(balance: float, income: list, expenses: list, weeks: int) -> list[dict]:
    today = date.today()
    horizon = today + timedelta(weeks=weeks)
    events = []

    for stream in income:
        for d in stream.occurrences_in(today, horizon):
            events.append({"date": d, "name": stream.name, "amount": +stream.net, "category": "income"})

    for exp in expenses:
        for d in exp.occurrences_in(today, horizon):
            events.append({"date": d, "name": exp.name, "amount": -exp.amount, "category": exp.category})

    events.sort(key=lambda e: e["date"])
    running = balance
    for e in events:
        running += e["amount"]
        e["running_balance"] = running
        e["date"] = e["date"].isoformat()
    return events


# ── SQLite helpers ────────────────────────────────────────────────────────────

DB_PATH = Path("budget.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS income (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                net     REAL NOT NULL,
                freq    TEXT NOT NULL,
                anchor  TEXT NOT NULL,
                end_date TEXT,
                weekday INTEGER
            );

            CREATE TABLE IF NOT EXISTS recurring (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT NOT NULL,
                amount   REAL NOT NULL,
                freq     TEXT NOT NULL,
                anchor   TEXT NOT NULL,
                end_date TEXT,
                weekday  INTEGER,
                category TEXT NOT NULL DEFAULT 'expense'
            );

            CREATE TABLE IF NOT EXISTS oneoff (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                amount  REAL NOT NULL,
                on_date TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'one-off'
            );
        """)
        # seed defaults
        conn.execute(
            "INSERT OR IGNORE INTO settings VALUES ('balance', '0')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO settings VALUES ('weeks', '16')"
        )
        conn.commit()


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class SettingsIn(BaseModel):
    balance: float
    weeks: int

class IncomeIn(BaseModel):
    name: str
    net: float
    freq: str
    anchor: str
    end_date: Optional[str] = None
    weekday: Optional[int] = None

class RecurringIn(BaseModel):
    name: str
    amount: float
    freq: str
    anchor: str
    end_date: Optional[str] = None
    weekday: Optional[int] = None
    category: str = "expense"

class OneOffIn(BaseModel):
    name: str
    amount: float
    on_date: str
    category: str = "one-off"


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="Budget")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def index():
    return Path("templates/index.html").read_text()


# ── Settings ──────────────────────────────────────────────────────────────────

@app.get("/api/settings")
def get_settings():
    with get_db() as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
    return {r["key"]: r["value"] for r in rows}

@app.post("/api/settings")
def save_settings(body: SettingsIn):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO settings VALUES ('balance', ?)", (str(body.balance),))
        conn.execute("INSERT OR REPLACE INTO settings VALUES ('weeks', ?)", (str(body.weeks),))
        conn.commit()
    return {"ok": True}


# ── Income ────────────────────────────────────────────────────────────────────

@app.get("/api/income")
def list_income():
    with get_db() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM income ORDER BY id").fetchall()]

@app.post("/api/income")
def add_income(body: IncomeIn):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO income (name, net, freq, anchor, end_date, weekday) VALUES (?,?,?,?,?,?)",
            (body.name, body.net, body.freq, body.anchor, body.end_date, body.weekday)
        )
        conn.commit()
        return {"id": cur.lastrowid}

@app.put("/api/income/{id}")
def update_income(id: int, body: IncomeIn):
    with get_db() as conn:
        conn.execute(
            "UPDATE income SET name=?, net=?, freq=?, anchor=?, end_date=?, weekday=? WHERE id=?",
            (body.name, body.net, body.freq, body.anchor, body.end_date, body.weekday, id)
        )
        conn.commit()
    return {"ok": True}

@app.delete("/api/income/{id}")
def delete_income(id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM income WHERE id=?", (id,))
        conn.commit()
    return {"ok": True}


# ── Recurring expenses ────────────────────────────────────────────────────────

@app.get("/api/recurring")
def list_recurring():
    with get_db() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM recurring ORDER BY id").fetchall()]

@app.post("/api/recurring")
def add_recurring(body: RecurringIn):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO recurring (name, amount, freq, anchor, end_date, weekday, category) VALUES (?,?,?,?,?,?,?)",
            (body.name, body.amount, body.freq, body.anchor, body.end_date, body.weekday, body.category)
        )
        conn.commit()
        return {"id": cur.lastrowid}

@app.put("/api/recurring/{id}")
def update_recurring(id: int, body: RecurringIn):
    with get_db() as conn:
        conn.execute(
            "UPDATE recurring SET name=?, amount=?, freq=?, anchor=?, end_date=?, weekday=?, category=? WHERE id=?",
            (body.name, body.amount, body.freq, body.anchor, body.end_date, body.weekday, body.category, id)
        )
        conn.commit()
    return {"ok": True}

@app.delete("/api/recurring/{id}")
def delete_recurring(id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM recurring WHERE id=?", (id,))
        conn.commit()
    return {"ok": True}


# ── One-offs ──────────────────────────────────────────────────────────────────

@app.get("/api/oneoff")
def list_oneoff():
    with get_db() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM oneoff ORDER BY on_date").fetchall()]

@app.post("/api/oneoff")
def add_oneoff(body: OneOffIn):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO oneoff (name, amount, on_date, category) VALUES (?,?,?,?)",
            (body.name, body.amount, body.on_date, body.category)
        )
        conn.commit()
        return {"id": cur.lastrowid}

@app.put("/api/oneoff/{id}")
def update_oneoff(id: int, body: OneOffIn):
    with get_db() as conn:
        conn.execute(
            "UPDATE oneoff SET name=?, amount=?, on_date=?, category=? WHERE id=?",
            (body.name, body.amount, body.on_date, body.category, id)
        )
        conn.commit()
    return {"ok": True}

@app.delete("/api/oneoff/{id}")
def delete_oneoff(id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM oneoff WHERE id=?", (id,))
        conn.commit()
    return {"ok": True}


# ── Projection ────────────────────────────────────────────────────────────────

@app.get("/api/projection")
def get_projection():
    with get_db() as conn:
        settings = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM settings").fetchall()}
        balance = float(settings.get("balance", 0))
        weeks   = int(settings.get("weeks", 16))

        income_rows    = conn.execute("SELECT * FROM income").fetchall()
        recurring_rows = conn.execute("SELECT * FROM recurring").fetchall()
        oneoff_rows    = conn.execute("SELECT * FROM oneoff").fetchall()

    def _date(s):
        return date.fromisoformat(s) if s else None

    income = [
        IncomeStream(
            name=r["name"], net=r["net"], freq=Freq(r["freq"]),
            anchor=_date(r["anchor"]), end=_date(r["end_date"]), weekday=r["weekday"]
        ) for r in income_rows
    ]
    recurring = [
        RecurringExpense(
            name=r["name"], amount=r["amount"], freq=Freq(r["freq"]),
            anchor=_date(r["anchor"]), end=_date(r["end_date"]),
            weekday=r["weekday"], category=r["category"]
        ) for r in recurring_rows
    ]
    oneoffs = [
        OneOffExpense(name=r["name"], amount=r["amount"], on=_date(r["on_date"]), category=r["category"])
        for r in oneoff_rows
    ]

    events = project(balance, income, recurring + oneoffs, weeks)
    today  = date.today()
    horizon = today + timedelta(weeks=weeks)

    total_income   = sum(e["amount"] for e in events if e["amount"] > 0)
    total_expenses = sum(abs(e["amount"]) for e in events if e["amount"] < 0)
    final_balance  = events[-1]["running_balance"] if events else balance
    min_balance    = min((e["running_balance"] for e in events), default=balance)

    return {
        "events": events,
        "summary": {
            "balance": balance,
            "weeks": weeks,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "final_balance": final_balance,
            "min_balance": min_balance,
            "from": today.isoformat(),
            "to": horizon.isoformat(),
        }
    }
