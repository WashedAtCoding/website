# Before running, make sure to run in the terminal:
# pip install bcrypt
# pip install flask

from flask import Flask, request, redirect, url_for, render_template, session
from database import get_db, init_db
import bcrypt
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"

init_db()

# ---------- PASSWORD VALIDATION ----------
def is_valid_password(password):
    return (
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[^A-Za-z0-9]", password)
    )


def get_game_suggestions(platforms, genres):
    catalog = [
        {
            "title": "The Legend of Zelda: Breath of the Wild",
            "description": "Explore a vast open world, solve puzzles, and battle enemies in a beautiful fantasy adventure.",
            "platforms": ["Nintendo Switch"],
            "genres": ["Action", "RPG"]
        },
        {
            "title": "Super Mario Odyssey",
            "description": "Join Mario on a globe-trotting 3D platformer full of creative levels and charming challenges.",
            "platforms": ["Nintendo Switch"],
            "genres": ["Action", "Party"]
        },
        {
            "title": "Beat Saber",
            "description": "Slash through neon blocks to the beat in this immersive VR rhythm game.",
            "platforms": ["Oculus Quest"],
            "genres": ["Action"]
        },
        {
            "title": "Superhot VR",
            "description": "Time moves only when you move, creating thrilling slow-motion combat puzzles.",
            "platforms": ["Oculus Quest"],
            "genres": ["Shooter", "Action"]
        },
        {
            "title": "Hades",
            "description": "Fight your way out of the Underworld in a fast-paced action roguelike with deep storytelling.",
            "platforms": ["Steam"],
            "genres": ["Action", "RPG"]
        },
        {
            "title": "Stardew Valley",
            "description": "Build a farm, make friends, and explore a relaxing pixel-art world at your own pace.",
            "platforms": ["Steam"],
            "genres": ["RPG", "Strategy"]
        },
        {
            "title": "Forza Horizon 5",
            "description": "Drive across a breathtaking open-world Mexico in this thrilling racing game.",
            "platforms": ["Xbox"],
            "genres": ["Action"]
        },
        {
            "title": "Halo Infinite",
            "description": "Return to the Master Chief story with epic sci-fi combat and large-scale multiplayer.",
            "platforms": ["Xbox"],
            "genres": ["Shooter"]
        },
        {
            "title": "God of War",
            "description": "Experience a cinematic action-adventure with Kratos and his son on a journey through Norse mythology.",
            "platforms": ["Playstation"],
            "genres": ["Action", "RPG"]
        },
        {
            "title": "Marvel's Spider-Man: Miles Morales",
            "description": "Swing through New York City as Miles Morales in a vibrant superhero action game.",
            "platforms": ["Playstation"],
            "genres": ["Action"]
        },
        {
            "title": "Civilization VI",
            "description": "Lead a civilization from ancient times to the modern era using diplomacy and strategy.",
            "platforms": ["Steam", "Xbox"],
            "genres": ["Strategy"]
        },
        {
            "title": "Mario Party Superstars",
            "description": "Play classic mini-games with friends in a party board game for Nintendo Switch.",
            "platforms": ["Nintendo Switch"],
            "genres": ["Party"]
        },
        {
            "title": "Jackbox Party Pack 10",
            "description": "Enjoy hilarious multiplayer trivia and drawing games with local or remote friends.",
            "platforms": ["Steam"],
            "genres": ["Party"]
        }
    ]

    suggestions = []
    for game in catalog:
        match_platform = any(platform in game["platforms"] for platform in platforms)
        match_genre = any(genre in game["genres"] for genre in genres)
        if match_platform or match_genre:
            suggestions.append(game)

    return suggestions

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Incorrect username or password"

    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            error = "Fields cannot be empty"
        elif not is_valid_password(password):
            error = "Password must include uppercase, lowercase, number, and special character"
        else:
            conn = get_db()
            try:
                hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_pw)
                )
                conn.commit()
                session["user"] = username

                return redirect(url_for("prefrences"))
            except:
                conn.rollback()
                error = "Username already exists or error occurred"
            finally:
                conn.close()

    return render_template("register.html", error=error)

@app.route("/prefrences", methods=["GET", "POST"])
def prefrences():
    if request.method == "POST":
        selected_platforms = request.form.getlist("platforms")
        session["preferred_platforms"] = selected_platforms
        return redirect(url_for("genres"))
    return render_template("prefrences.html")

@app.route("/genres", methods=["GET", "POST"])
def genres():
    if request.method == "POST":
        selected_genres = request.form.getlist("genres")
        session["preferred_genres"] = selected_genres
        return redirect(url_for("dashboard"))
    return render_template("genres.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    comments = conn.execute(
        "SELECT * FROM comments"
    ).fetchall()
    conn.close()
    preferred_platforms = session.get("preferred_platforms", [])
    preferred_genres = session.get("preferred_genres", [])
    suggestions = get_game_suggestions(preferred_platforms, preferred_genres)
    return render_template(
        "dashboard.html",
        comments=comments,
        username=session["user"],
        suggestions=suggestions,
        preferred_platforms=preferred_platforms,
        preferred_genres=preferred_genres
    )


# ---------- CREATE ----------
# TODO: Create a route like /create
# This page should:
# - Show a form (GET)
# - Save data to the database (POST)
# - Redirect back to dashboard
# NOTE: Remove the triple """ before and after each route to 'uncomment'

@app.route("/create", methods=["GET", "POST"])
def create():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        # TODO: Get form data (title, content)

        # TODO: conn = get_db()
        conn = get_db()
        # TODO: Insert into comments table
        try:

            conn.execute(
                "INSERT INTO comments (title, content) VALUES (?, ?)",
                (title, content)
            )
            conn.commit()
        finally:
            conn.close()
        # TODO: Commit and close

        return redirect(url_for("dashboard"))

    return render_template("create.html")


# ---------- UPDATE ----------
# TODO: Create a route like /edit/<id>
# This page should:
# - Load existing data
# - Show it in a form
# - Update the database on submit


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    comment = conn.execute(
        "SELECT * FROM comments WHERE id=?",
        (id,)
    ).fetchone()

    if not comment:
        conn.close()
        return "Comment not found"

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if not title or not content:
            error = "Fields cannot be empty"
        else:
            try:
                conn.execute(
                    "UPDATE comments SET title=?, content=? WHERE id=?",
                    (title, content, id)
                )
                conn.commit()
                conn.close()
                return redirect(url_for("dashboard"))
            except:
                conn.rollback()
                conn.close()
                return "Error updating comment"

    conn.close()
    return render_template("edit.html", comment=comment)

# ---------- DELETE ----------
# TODO: Create a route like /delete/<id>
# This should:
# - Delete an entry from the database
# - Redirect back to dashboard


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    comment = conn.execute(
        "SELECT * FROM comments WHERE id=?",
        (id,)
    ).fetchone()
    conn.close()

    if not comment:
        return "Comment not found", 404

    if request.method == "POST":
        conn = get_db()
        try:
            conn.execute(
                "DELETE FROM comments WHERE id=?",
                (id,)
            )
            conn.commit()
        finally:
            conn.close()

        return redirect(url_for("dashboard"))

    return render_template("delete.html", comment=comment)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)