import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

DB_FILE = "recipes.db"




def init_db():
    """Initialize the SQLite database and create the table if not exists."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def fetch_recipes(search_query=None, category=None):
    """Fetch all recipes or filter by search/category."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if search_query and category:
        cursor.execute(
            "SELECT id, title, category, ingredients, instructions FROM recipes "
            "WHERE (title LIKE ? OR ingredients LIKE ?) AND category LIKE ?",
            (f"%{search_query}%", f"%{search_query}%", f"%{category}%")
        )
    elif search_query:
        cursor.execute(
            "SELECT id, title, category, ingredients, instructions FROM recipes "
            "WHERE title LIKE ? OR ingredients LIKE ?",
            (f"%{search_query}%", f"%{search_query}%")
        )
    elif category:
        cursor.execute(
            "SELECT id, title, category, ingredients, instructions FROM recipes "
            "WHERE category LIKE ?",
            (f"%{category}%",)
        )
    else:
        cursor.execute("SELECT id, title, category, ingredients, instructions FROM recipes")

    recipes = cursor.fetchall()
    conn.close()
    return recipes


def insert_recipe(title, category, ingredients, instructions):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO recipes (title, category, ingredients, instructions) VALUES (?, ?, ?, ?)",
        (title, category, ingredients, instructions)
    )
    conn.commit()
    conn.close()


def update_recipe_in_db(recipe_id, title, category, ingredients, instructions):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE recipes SET title=?, category=?, ingredients=?, instructions=? WHERE id=?",
        (title, category, ingredients, instructions, recipe_id)
    )
    conn.commit()
    conn.close()


def delete_recipe_from_db(recipe_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
    conn.commit()
    conn.close()




class RecipeBookApp:
    def __init__(self, master):
        self.master = master
        master.title("Simple Recipe Book with Categories & Search")
        master.geometry("700x500")

        self.recipes = []


        search_frame = tk.Frame(master)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=1, padx=5)

        tk.Label(search_frame, text="Category:").grid(row=0, column=2, padx=5)
        self.category_entry = tk.Entry(search_frame, width=20)
        self.category_entry.grid(row=0, column=3, padx=5)

        tk.Button(search_frame, text="Filter", command=self.search_recipes).grid(row=0, column=4, padx=5)
        tk.Button(search_frame, text="Clear", command=self.clear_search).grid(row=0, column=5, padx=5)


        self.recipe_listbox = tk.Listbox(master, width=70, height=15)
        self.recipe_listbox.pack(pady=15)


        self.btn_frame = tk.Frame(master)
        self.btn_frame.pack()

        tk.Button(self.btn_frame, text="Create", width=10, command=self.create_recipe).grid(row=0, column=0, padx=5)
        tk.Button(self.btn_frame, text="View", width=10, command=self.view_recipe).grid(row=0, column=1, padx=5)
        tk.Button(self.btn_frame, text="Update", width=10, command=self.update_recipe).grid(row=0, column=2, padx=5)
        tk.Button(self.btn_frame, text="Delete", width=10, command=self.delete_recipe).grid(row=0, column=3, padx=5)

        self.load_recipe_list()



    def load_recipe_list(self, search_query=None, category=None):
        """Load and display recipe titles."""
        self.recipe_listbox.delete(0, tk.END)
        self.recipes = fetch_recipes(search_query, category)
        for recipe in self.recipes:
            title_display = f"{recipe[1]}  ({recipe[2] if recipe[2] else 'No Category'})"
            self.recipe_listbox.insert(tk.END, title_display)

    def clear_search(self):
        """Clear search filters."""
        self.search_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.load_recipe_list()

    def search_recipes(self):
        """Filter recipes by search and/or category."""
        search_query = self.search_entry.get().strip()
        category = self.category_entry.get().strip()
        self.load_recipe_list(search_query, category)

    def create_recipe(self):
        """Create a new recipe."""
        title = simpledialog.askstring("Create Recipe", "Enter recipe title:")
        if not title:
            return

        category = simpledialog.askstring("Category", "Enter category (e.g., Dessert, Main, Vegan):")
        if category is None:
            category = ""

        ingredients = simpledialog.askstring("Ingredients", "Enter ingredients (comma separated):")
        if not ingredients:
            return

        instructions = simpledialog.askstring("Instructions", "Enter instructions:")
        if not instructions:
            return

        insert_recipe(title, category, ingredients, instructions)
        self.load_recipe_list()
        messagebox.showinfo("Success", "Recipe created successfully!")

    def view_recipe(self):
        """View details of selected recipe in a resizable scrollable window."""
        selected = self.recipe_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a recipe to view.")
            return

        index = selected[0]
        recipe = self.recipes[index]


        view_win = tk.Toplevel(self.master)
        view_win.title(f"Recipe Details - {recipe[1]}")
        view_win.geometry("500x400")
        view_win.resizable(True, True)


        title_label = tk.Label(view_win, text=recipe[1], font=("Helvetica", 16, "bold"))
        title_label.pack(pady=5)


        cat_text = f"Category: {recipe[2] if recipe[2] else 'None'}"
        cat_label = tk.Label(view_win, text=cat_text, font=("Helvetica", 12, "italic"))
        cat_label.pack(pady=2)


        text_frame = tk.Frame(view_win)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        text_area = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set)
        text_area.pack(fill="both", expand=True)
        scrollbar.config(command=text_area.yview)

        
        text_area.insert(tk.END, "Ingredients:\n" + "\n".join(recipe[3].split(',')) + "\n\n")
        text_area.insert(tk.END, "Instructions:\n" + recipe[4])
        text_area.config(state="disabled")

    def update_recipe(self):
        """Update a selected recipe."""
        selected = self.recipe_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a recipe to update.")
            return

        index = selected[0]
        recipe_id, title, category, ingredients, instructions = self.recipes[index]

        new_title = simpledialog.askstring("Update Title", "Enter new title:", initialvalue=title)
        new_category = simpledialog.askstring("Update Category", "Enter new category:", initialvalue=category)
        new_ingredients = simpledialog.askstring("Update Ingredients", "Enter new ingredients (comma separated):",
                                                 initialvalue=ingredients)
        new_instructions = simpledialog.askstring("Update Instructions", "Enter new instructions:",
                                                  initialvalue=instructions)

        if new_title and new_ingredients and new_instructions:
            update_recipe_in_db(recipe_id, new_title, new_category, new_ingredients, new_instructions)
            self.load_recipe_list()
            messagebox.showinfo("Success", "Recipe updated successfully!")

    def delete_recipe(self):
        """Delete selected recipe."""
        selected = self.recipe_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a recipe to delete.")
            return

        index = selected[0]
        recipe_id, title, _, _, _ = self.recipes[index]
        confirm = messagebox.askyesno("Delete Confirmation", f"Are you sure you want to delete '{title}'?")
        if confirm:
            delete_recipe_from_db(recipe_id)
            self.load_recipe_list()
            messagebox.showinfo("Deleted", "Recipe deleted successfully!")



if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = RecipeBookApp(root)
    root.mainloop()
