from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)

# =========================
# SECRET KEY
# =========================

app.secret_key = "ngetich-secret-key"


# =========================
# ADMIN PASSWORD
# =========================

ADMIN_PASSWORD = "1234"


# =========================
# DATABASE
# =========================

def init_db():

    connection = sqlite3.connect("messages.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    columns = connection.execute(
        "PRAGMA table_info(messages)"
    ).fetchall()

    column_names = [
        column[1]
        for column in columns
    ]

    if "created_at" not in column_names:

        connection.execute(
            "ALTER TABLE messages ADD COLUMN created_at TEXT"
        )

        connection.execute(
            """
            UPDATE messages
            SET created_at = ?
            WHERE created_at IS NULL
            """,
            ("Previously received",)
        )

    connection.commit()
    connection.close()


# =========================
# HOME
# =========================

@app.route("/")
def home():

    return render_template("index.html")


# =========================
# ABOUT
# =========================

@app.route("/about")
def about():

    return render_template("about.html")


# =========================
# SERVICES
# =========================

@app.route("/services")
def services():

    return render_template("services.html")


# =========================
# PROJECTS
# =========================

@app.route("/projects")
def projects():

    return render_template("projects.html")


# =========================
# CONTACT
# =========================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        message = request.form["message"]

        created_at = datetime.now().strftime(
            "%d %B %Y, %I:%M %p"
        )

        connection = sqlite3.connect(
            "messages.db"
        )

        connection.execute(
            """
            INSERT INTO messages
            (
                name,
                email,
                message,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                message,
                created_at
            )
        )

        connection.commit()
        connection.close()

        return render_template(
            "contact.html",
            success=True,
            name=name
        )

    return render_template(
        "contact.html"
    )


# =========================
# ADMIN
# =========================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        password = request.form["password"]

        if password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect("/admin")

        return render_template(
            "admin.html",
            error="Incorrect password."
        )

    if not session.get("admin_logged_in"):

        return render_template(
            "admin.html"
        )

    connection = sqlite3.connect(
        "messages.db"
    )

    connection.row_factory = sqlite3.Row

    messages = connection.execute(
        """
        SELECT *
        FROM messages
        ORDER BY id DESC
        """
    ).fetchall()

    total_messages = connection.execute(
        """
        SELECT COUNT(*)
        FROM messages
        """
    ).fetchone()[0]

    today = datetime.now().strftime(
        "%d %B %Y"
    )

    messages_today = connection.execute(
        """
        SELECT COUNT(*)
        FROM messages
        WHERE created_at LIKE ?
        """,
        (today + "%",)
    ).fetchone()[0]

    connection.close()

    return render_template(
        "admin.html",
        messages=messages,
        total_messages=total_messages,
        messages_today=messages_today
    )


# =========================
# REPLY PAGE
# =========================

@app.route("/reply/<int:message_id>")
def reply_message(message_id):

    if not session.get("admin_logged_in"):

        return redirect("/admin")

    connection = sqlite3.connect(
        "messages.db"
    )

    connection.row_factory = sqlite3.Row

    message = connection.execute(
        """
        SELECT *
        FROM messages
        WHERE id = ?
        """,
        (message_id,)
    ).fetchone()

    connection.close()

    if message is None:

        return redirect("/admin")

    return render_template(
        "reply.html",
        message=message
    )


# =========================
# DELETE MESSAGE
# =========================

@app.route(
    "/delete/<int:message_id>",
    methods=["POST"]
)
def delete_message(message_id):

    if not session.get("admin_logged_in"):

        return redirect("/admin")

    connection = sqlite3.connect(
        "messages.db"
    )

    connection.execute(
        """
        DELETE FROM messages
        WHERE id = ?
        """,
        (message_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/admin")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect("/admin")


# =========================
# START WEBSITE
# =========================

if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )