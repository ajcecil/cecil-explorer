import json
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import subprocess

# Load color theme from JSON file
def load_theme():
    with open("formatting/theme.json", "r") as theme_file:
        theme = json.load(theme_file)
    return theme

# Predefined quick-access folders
QUICK_ACCESS_FOLDERS = {
    "Home": os.path.expanduser("~"),
    "Documents": os.path.join(os.path.expanduser("~"), "Documents"),
    "Downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
    "Desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
    "Projects": "C:/Users/ajcecil/Project_Work"
}

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.theme = load_theme()  # Load theme from JSON file
        self.root.title("Custom File Explorer")
        self.root.geometry("900x600")

        # Load icons
        self.folder_icon = ImageTk.PhotoImage(Image.open("icons/folder.png").resize((16, 16)))
        self.file_icon = ImageTk.PhotoImage(Image.open("icons/document.png").resize((16, 16)))
        self.zip_icon = ImageTk.PhotoImage(Image.open("icons/soil_cube.png").resize((16, 16)))

        # Apply theme colors to window
        self.apply_theme()

        # Create a toolbar frame
        self.toolbar = tk.Frame(root, bg=self.theme["toolbar_background"], height=30)
        self.toolbar.pack(side="top", fill="x")

        # Toolbar buttons
        ttk.Button(self.toolbar, text="Rename", command=self.rename_item).pack(side="left", padx=5, pady=2)
        ttk.Button(self.toolbar, text="Delete", command=self.delete_item).pack(side="left", padx=5, pady=2)
        ttk.Button(self.toolbar, text="Unzip", command=self.unzip_item).pack(side="left", padx=5, pady=2)

        # Create a PanedWindow to separate Sidebar and Main content
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill="both", expand=True)

        # Sidebar Frame (Left)
        self.sidebar_frame = tk.Frame(self.paned_window, width=200, bg=self.theme["sidebar_background"])
        self.paned_window.add(self.sidebar_frame)

        # Quick Access Listbox
        self.folder_listbox = tk.Listbox(self.sidebar_frame, bg=self.theme["sidebar_background"], fg=self.theme["sidebar_foreground"])
        self.folder_listbox.pack(fill="x", padx=5, pady=5)
        self.folder_listbox.bind("<<ListboxSelect>>", self.load_selected_folder)

        # Populate Quick Access sidebar
        for folder in QUICK_ACCESS_FOLDERS.keys():
            self.folder_listbox.insert(tk.END, folder)

        # Folder Tree (Under Quick Access)
        self.tree = ttk.Treeview(self.sidebar_frame)
        self.tree.heading("#0", text="Folders", anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_single_click)  # Single click for folders
        self.tree.bind("<Double-1>", self.on_double_click)  # Double click for files

        # Main Content (Right)
        self.main_frame = tk.Frame(self.paned_window, bg=self.theme["main_frame_background"])
        self.paned_window.add(self.main_frame)

        self.file_tree = ttk.Treeview(self.main_frame, columns=("name",), show="tree")
        self.file_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.file_tree.bind("<Double-1>", self.on_double_click)

    def apply_theme(self):
        """Applies the color theme to the app."""
        self.root.configure(bg=self.theme["background"])
        
    def load_selected_folder(self, event):
        """Loads the selected folder into the tree and file display."""
        selected_index = self.folder_listbox.curselection()
        if selected_index:
            folder_name = self.folder_listbox.get(selected_index)
            folder_path = QUICK_ACCESS_FOLDERS[folder_name]
            self.tree.delete(*self.tree.get_children())  # Clear tree
            self.populate_tree(folder_path, "")
            self.display_folder_contents(folder_path)

    def populate_tree(self, path, parent=""):
        """Populates the tree with subfolders only (no files)."""
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    node = self.tree.insert(parent, "end", text=item, image=self.folder_icon, values=[full_path])
                    self.tree.insert(node, "end", text="Loading...")  # Placeholder for lazy loading
        except PermissionError:
            pass
    def display_folder_contents(self, path):
        """Displays the contents of the selected folder in the right pane with icons."""
        self.file_tree.delete(*self.file_tree.get_children())  # Clear existing items
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isfile(full_path):
                    # Choose the right icon
                    if item.endswith(".zip"):
                        icon = self.zip_icon
                    else:
                        icon = self.file_icon
                    # Insert the file into the tree with an icon
                    self.file_tree.insert("", "end", text=item, image=icon, values=[full_path])
        except PermissionError:
            pass

    def on_single_click(self, event):
        """Handles single-click on a folder to expand/collapse it."""
        selected_item = self.tree.focus()
        path = self.tree.item(selected_item, "values")

        if path:
            path = path[0]
            if os.path.isdir(path):
                # Check if it's already expanded
                if self.tree.get_children(selected_item):  # Folder is expanded, collapse it
                    self.tree.delete(*self.tree.get_children(selected_item))
                else:  # Expand it
                    self.populate_tree(path, selected_item)
                    self.display_folder_contents(path)


    def on_double_click(self, event):
        """Handles double-click on either a file (to open it) or a folder (to load its contents)."""
        selected_item = self.file_tree.focus()
        file_path = self.file_tree.item(selected_item, "values")
        
        if file_path:  # If it's a file in the file tree
            file_path = file_path[0]
            if os.path.isfile(file_path):
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(file_path)
                    elif os.name == 'posix':  # macOS/Linux
                        subprocess.call(['open', file_path])  # macOS
                        # subprocess.call(['xdg-open', file_path])  # Linux
                    messagebox.showinfo("File Opened", f"{os.path.basename(file_path)} opened successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {e}")


    def rename_item(self):
        """Renames a selected file."""
        selected_index = self.file_listbox.curselection()
        if selected_index:
            old_name = self.file_listbox.get(selected_index)
            folder = self.get_current_folder()
            if folder:
                full_old_path = os.path.join(folder, old_name)
                new_name = filedialog.asksaveasfilename(initialdir=folder, initialfile=old_name)
                if new_name:
                    os.rename(full_old_path, new_name)
                    self.display_folder_contents(folder)

    def delete_item(self):
        """Deletes a selected file."""
        selected_index = self.file_listbox.curselection()
        if selected_index:
            file_name = self.file_listbox.get(selected_index)
            folder = self.get_current_folder()
            if folder:
                full_path = os.path.join(folder, file_name)
                if messagebox.askyesno("Delete", f"Are you sure you want to delete {file_name}?"):
                    try:
                        os.remove(full_path)
                        self.display_folder_contents(folder)
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not delete: {e}")

    def unzip_item(self):
        """Extracts a selected ZIP file."""
        selected_index = self.file_listbox.curselection()
        if selected_index:
            file_name = self.file_listbox.get(selected_index)
            folder = self.get_current_folder()
            if folder:
                full_path = os.path.join(folder, file_name)
                if full_path.endswith(".zip"):
                    extract_to = filedialog.askdirectory()
                    if extract_to:
                        try:
                            shutil.unpack_archive(full_path, extract_to)
                            messagebox.showinfo("Unzip", "File extracted successfully!")
                            self.display_folder_contents(folder)
                        except Exception as e:
                            messagebox.showerror("Error", f"Could not unzip: {e}")

    def get_current_folder(self):
        """Returns the currently selected folder path."""
        selected_index = self.folder_listbox.curselection()
        if selected_index:
            folder_name = self.folder_listbox.get(selected_index)
            return QUICK_ACCESS_FOLDERS.get(folder_name, None)
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()

