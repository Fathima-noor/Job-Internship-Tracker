from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "job-tracker-secret-key"


# ---------------- DATABASE ----------------

def get_db():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


def init_db():

    connection = sqlite3.connect("database.db")

    # Users table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Applications table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            company TEXT NOT NULL,
            job_title TEXT NOT NULL,
            application_type TEXT NOT NULL,
            location TEXT,
            application_date TEXT,
            deadline TEXT,
            status TEXT NOT NULL,
            job_url TEXT,
            salary TEXT,
            notes TEXT
        )
    """)

    # Add user_id if old database doesn't have it
    try:
        connection.execute(
            "ALTER TABLE applications ADD COLUMN user_id INTEGER"
        )
    except sqlite3.OperationalError:
        pass

    connection.commit()
    connection.close()


# ---------------- HOME ----------------

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = get_db()

        try:

            connection.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
                """,
                (name, email, hashed_password)
            )

            connection.commit()
            connection.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            connection.close()

            return render_template(
                "register.html",
                error="Email already registered."
            )

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        connection = get_db()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    connection = get_db()

    total = connection.execute(
        """
        SELECT COUNT(*)
        FROM applications
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()[0]

    interviews = connection.execute(
        """
        SELECT COUNT(*)
        FROM applications
        WHERE user_id = ?
        AND status = 'Interview'
        """,
        (user_id,)
    ).fetchone()[0]

    selected = connection.execute(
        """
        SELECT COUNT(*)
        FROM applications
        WHERE user_id = ?
        AND status = 'Selected'
        """,
        (user_id,)
    ).fetchone()[0]

    rejected = connection.execute(
        """
        SELECT COUNT(*)
        FROM applications
        WHERE user_id = ?
        AND status = 'Rejected'
        """,
        (user_id,)
    ).fetchone()[0]

    recent = connection.execute(
        """
        SELECT *
        FROM applications
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        user_name=session["user_name"],
        total=total,
        interviews=interviews,
        selected=selected,
        rejected=rejected,
        recent=recent
    )


# ---------------- ADD APPLICATION ----------------

@app.route("/add-application", methods=["GET", "POST"])
def add_application():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        company = request.form["company"]
        job_title = request.form["job_title"]
        application_type = request.form["application_type"]
        location = request.form["location"]
        application_date = request.form["application_date"]
        deadline = request.form["deadline"]
        status = request.form["status"]
        job_url = request.form["job_url"]
        salary = request.form["salary"]
        notes = request.form["notes"]

        connection = get_db()

        connection.execute(
            """
            INSERT INTO applications
            (
                user_id,
                company,
                job_title,
                application_type,
                location,
                application_date,
                deadline,
                status,
                job_url,
                salary,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                company,
                job_title,
                application_type,
                location,
                application_date,
                deadline,
                status,
                job_url,
                salary,
                notes
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("applications"))

    return render_template("add_application.html")


# ---------------- VIEW APPLICATIONS ----------------

@app.route("/applications")
def applications():

    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "")
    application_type = request.args.get("type", "")

    connection = get_db()

    query = """
        SELECT *
        FROM applications
        WHERE user_id = ?
    """

    parameters = [session["user_id"]]

    if search:

        query += """
            AND (
                company LIKE ?
                OR job_title LIKE ?
                OR location LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value
        ])

    if status:

        query += " AND status = ?"
        parameters.append(status)

    if application_type:

        query += " AND application_type = ?"
        parameters.append(application_type)

    query += " ORDER BY id DESC"

    applications = connection.execute(
        query,
        parameters
    ).fetchall()

    connection.close()

    return render_template(
        "applications.html",
        applications=applications,
        search=search,
        selected_status=status,
        selected_type=application_type
    )


# ---------------- EDIT APPLICATION ----------------

@app.route("/edit-application/<int:id>", methods=["GET", "POST"])
def edit_application(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    application = connection.execute(
        """
        SELECT *
        FROM applications
        WHERE id = ?
        AND user_id = ?
        """,
        (id, session["user_id"])
    ).fetchone()

    if application is None:

        connection.close()

        return redirect(url_for("applications"))

    if request.method == "POST":

        connection.execute(
            """
            UPDATE applications
            SET
                company = ?,
                job_title = ?,
                application_type = ?,
                location = ?,
                application_date = ?,
                deadline = ?,
                status = ?,
                job_url = ?,
                salary = ?,
                notes = ?
            WHERE id = ?
            AND user_id = ?
            """,
            (
                request.form["company"],
                request.form["job_title"],
                request.form["application_type"],
                request.form["location"],
                request.form["application_date"],
                request.form["deadline"],
                request.form["status"],
                request.form["job_url"],
                request.form["salary"],
                request.form["notes"],
                id,
                session["user_id"]
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("applications"))

    connection.close()

    return render_template(
        "edit_application.html",
        application=application
    )


# ---------------- DELETE APPLICATION ----------------

@app.route("/delete-application/<int:id>", methods=["POST"])
def delete_application(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    connection.execute(
        """
        DELETE FROM applications
        WHERE id = ?
        AND user_id = ?
        """,
        (id, session["user_id"])
    )

    connection.commit()
    connection.close()

    return redirect(url_for("applications"))


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------- RUN ----------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)