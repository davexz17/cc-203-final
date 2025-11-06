import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

DATA_FILE = 'recipes.json'


def load_recipes():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_recipes(recipes):
    with open(DATA_FILE, 'w') as f:
        json.dump(recipes, f, indent=4)


class RecipeBookApp:
    def __init__(self, master):
        self.master = master
        master.title(" Simple Recipe Book")
        master.geometry("600x400")

        self.recipes = load_recipes()

        # UI Elements
        self.recipe_listbox = tk.Listbox(master, width=50, height=15)
        self.recipe_listbox.pack(pady=15)

        # Buttons
        self.btn_frame = tk.Frame(master)
        self.btn_frame.pack()

        tk.Button(self.btn_frame, text="Create", width=10, command=self.create_recipe).grid(row=0, column=0, padx=5)
        tk.Button(self.btn_frame, text="View", width=10, command=self.view_recipe).grid(row=0, column=1, padx=5)
        tk.Button(self.btn_frame, text="Update", width=10, command=self.update_recipe).grid(row=0, column=2, padx=5)
        tk.Button(self.btn_frame, text="Delete", width=10, command=self.delete_recipe).grid(row=0, column=3, padx=5)

        self.load_recipe_list()

    def load_recipe_list(self):
        self.recipe_listbox.delete(0, tk.END)
        for recipe in self.recipes:
            self.recipe_listbox.insert(tk.END, recipe['title'])

    def create_recipe(self):
        title = simpledialog.askstring("Create Recipe", "Enter recipe title:")
        if not title:
            return

        ingredients = simpledialog.askstring("Ingredients", "Enter ingredients (comma separated):")
        if not ingredients:
            return

        instructions = simpledialog.askstring("Instructions", "Enter instructions:")
        if not instructions:
            return

        new_recipe = {
            "title": title,
            "ingredients": [i.strip() for i in ingredients.split(',')],
            "instructions": instructions
        }

        self.recipes.append(new_recipe)
        save_recipes(self.recipes)
        self.load_recipe_list()
        messagebox.showinfo("Success", "Recipe created successfully!")

    def view_recipe(self):
        selected = self.recipe_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a recipe to view.")
            return

        index = selected[0]
        recipe = self.recipes[index]
        info = f"Title: {recipe['title']}\n\nIngredients:\n" + "\n".join(recipe['ingredients']) + \
               f"\n\nInstructions:\n{recipe['instructions']}"
        messagebox.showinfo("Recipe Details", info)

    def update_recipe(self):
        selected = self.recipe_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a recipe to update.")
            return

        index = selected[0]
        recipe = self.recipes[index]

        title = simpledialog.askstring("Update Title", "Enter new title:", initialvalue=recipe['title'])
        ingredients = simpledialog.askstring("Update Ingredients", "Enter new ingredients (comma separated):",
                                             initialvalue=", ".join(recipe['ingredients']))
        instructions = simpledialog.askstring("Update Instructions", "Enter new instructions:",
                                              initialvalue=recipe['instructions'])

        if title: recipe['title'] = title
        if ingredients: recipe['ingredients'] = [i.strip() for i in ingredients.split(',')]
        if instructions: recipe['instructions'] = instructions

        self.recipes[index] = recipe
        save_recipes(self.recipes)
        self.load_recipe_list()
        messagebox.showinfo("Success", "Recipe updated successfully!")

    def delete_recipe(self):
        selected = self.recipe_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a recipe to delete.")
            return

        index = selected[0]
        confirm = messagebox.askyesno("Delete Confirmation", f"Are you sure you want to delete '{self.recipes[index]['title']}'?")
        if confirm:
            del self.recipes[index]
            save_recipes(self.recipes)
            self.load_recipe_list()
            messagebox.showinfo("Deleted", "Recipe deleted successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeBookApp(root)
    root.mainloop()
