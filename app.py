from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "mlm_project.db"))
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")


def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with get_db() as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                sponsor_id INTEGER REFERENCES members(id) ON DELETE SET NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )


def build_tree(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    nodes: dict[int, dict[str, Any]] = {
        row["id"]: {"id": row["id"], "name": row["name"], "email": row["email"], "children": []}
        for row in rows
    }
    roots = []
    for row in rows:
        node = nodes[row["id"]]
        if row["sponsor_id"] in nodes:
            nodes[row["sponsor_id"]]["children"].append(node)
        else:
            roots.append(node)
    return roots


@app.get("/")
def index():
    with get_db() as db:
        rows = db.execute(
            "SELECT id, name, email, sponsor_id, created_at FROM members ORDER BY name COLLATE NOCASE"
        ).fetchall()
    return render_template(
        "index.html",
        members=rows,
        tree=build_tree(rows),
        member_count=len(rows),
        sponsor_count=sum(1 for row in rows if row["sponsor_id"] is not None),
    )


@app.post("/members")
def add_member():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    sponsor_value = request.form.get("sponsor_id", "").strip()

    if not name or not email or "@" not in email:
        flash("Enter a name and a valid email address.", "error")
        return redirect(url_for("index"))

    sponsor_id = None
    if sponsor_value:
        try:
            sponsor_id = int(sponsor_value)
        except ValueError:
            flash("Choose a valid sponsor.", "error")
            return redirect(url_for("index"))

    try:
        with get_db() as db:
            if sponsor_id is not None and not db.execute(
                "SELECT 1 FROM members WHERE id = ?", (sponsor_id,)
            ).fetchone():
                flash("That sponsor could not be found.", "error")
                return redirect(url_for("index"))
            db.execute(
                "INSERT INTO members (name, email, sponsor_id) VALUES (?, ?, ?)",
                (name, email, sponsor_id),
            )
    except sqlite3.IntegrityError:
        flash("That email address is already registered.", "error")
        return redirect(url_for("index"))

    flash(f"{name} was added to the network.", "success")
    return redirect(url_for("index"))


@app.post("/members/<int:member_id>/delete")
def delete_member(member_id: int):
    with get_db() as db:
        db.execute("DELETE FROM members WHERE id = ?", (member_id,))
    flash("Member removed.", "success")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
