from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime  # <-- added

CATEGORIES = [
    "Appetizer",
    "Main Course",
    "Dessert",
    "Drinks",
    "Breakfast",
    "Snack",
    "Other"
]

DB_FILE = "recipes.db"

app = Flask(__name__)
app.secret_key = "secretkey123"



def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            user_id INTEGER,
            date_added TEXT,  -- <-- added date column
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def fetch_recipes(search=None, category=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = "SELECT id, title, category, ingredients, instructions, user_id, date_added FROM recipes WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR ingredients LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if category:
        query += " AND category LIKE ?"
        params.append(f"%{category}%")

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_recipe(recipe_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,))
    recipe = cursor.fetchone()
    conn.close()
    return recipe


# ---------------------
# AUTH ROUTES
# ---------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            conn.close()
            flash("Account created! You can now log in.")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Username already taken.")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["username"] = username
            flash("Logged in successfully!")
            return redirect(url_for("index"))

        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("index"))


# ---------------------
# RECIPE ROUTES
# ---------------------
@app.route("/")
def index():
    search = request.args.get("search", "")
    category = request.args.get("category", "")

    recipes = fetch_recipes(search, category)
    return render_template("index.html", recipes=recipes, search=search, category=category, CATEGORIES=CATEGORIES)


@app.route("/create", methods=["POST"])
def create():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    title = request.form["title"]
    category = request.form["category"]
    ingredients = request.form["ingredients"]
    instructions = request.form["instructions"]
    date_added = datetime.now().strftime("%Y-%m-%d")  # <-- added

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recipes (title, category, ingredients, instructions, user_id, date_added)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, category, ingredients, instructions, session["user_id"], date_added))
    conn.commit()
    conn.close()

    flash("Recipe created successfully!")
    return redirect(url_for("index"))


@app.route("/view/<int:recipe_id>")
def view(recipe_id):
    recipe = get_recipe(recipe_id)
    if not recipe:
        return "Recipe not found", 404

    return render_template("view.html", recipe=recipe)


@app.route("/edit/<int:recipe_id>", methods=["GET", "POST"])
def edit(recipe_id):
    recipe = get_recipe(recipe_id)

    if not recipe:
        return "Not found", 404

    if recipe[5] != session.get("user_id"):
        flash("You can only edit your own recipes.")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE recipes
            SET title=?, category=?, ingredients=?, instructions=?
            WHERE id=?
        """, (title, category, ingredients, instructions, recipe_id))
        conn.commit()
        conn.close()

        flash("Recipe updated!")
        return redirect(url_for("view", recipe_id=recipe_id))

    return render_template("edit.html", recipe=recipe)


@app.route("/delete/<int:recipe_id>")
def delete(recipe_id):
    recipe = get_recipe(recipe_id)

    if not recipe:
        return "Not found", 404

    if recipe[5] != session.get("user_id"):
        flash("You can only delete your own recipes.")
        return redirect(url_for("index"))

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
    conn.commit()
    conn.close()

    flash("Recipe deleted!")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
