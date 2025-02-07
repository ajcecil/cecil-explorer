import json
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import markdown
from tkinterweb import HtmlFrame

# Load color theme from JSON file
def load_theme():
    with open("formatting/theme.json", "r") as theme_file:
        theme = json.load(theme_file)
    return theme

def load_quick_access():
    with open("formatting/quick_access.json", "r") as quick_access:
        QUICK_ACCESS_FOLDERS = json.load(quick_access)
    return QUICK_ACCESS_FOLDERS


class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.theme = load_theme()  # Load theme from JSON file
        self.QUICK_ACCESS_FOLDERS = load_quick_access() # Load the Quick Access Folders
        self.root.title("Custom File Explorer")
        self.root.geometry("900x800")  # Increase window size for additional content

        # Load icons
        self.folder_icon = ImageTk.PhotoImage(Image.open("icons/folder.png").resize((16, 16)))
        self.file_icon = ImageTk.PhotoImage(Image.open("icons/document.png").resize((16, 16)))
        self.zip_icon = ImageTk.PhotoImage(Image.open("icons/soil_cube.png").resize((16, 16)))

        # Apply theme colors to window
        self.apply_theme()
        
        # Configure Treeview Styles for Font and Background
        self.style = ttk.Style()
        self.style.configure("Treeview", 
                            background=self.theme["tree_background"], 
                            foreground=self.theme["tree_foreground"], 
                            fieldbackground=self.theme["tree_background"])
        self.style.configure("Treeview.Heading", 
                            background=self.theme["tree_heading_background"], 
                            foreground=self.theme["tree_heading_foreground"])

        # Create a toolbar frame
        self.toolbar = tk.Frame(root, bg=self.theme["toolbar_background"], height=30)
        self.toolbar.pack(side="top", fill="x")

        # Toolbar buttons
        ttk.Button(self.toolbar, text="Rename", command=self.rename_item).pack(side="left", padx=5, pady=2)
        ttk.Button(self.toolbar, text="Delete", command=self.delete_item).pack(side="left", padx=5, pady=2)
        ttk.Button(self.toolbar, text="Unzip", command=self.unzip_item).pack(side="left", padx=5, pady=2)

        # Create a PanedWindow to separate Sidebar and Main content
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg=self.theme["background"])
        self.paned_window.pack(fill="both", expand=True)

        # Sidebar Frame (Left)
        self.sidebar_frame = tk.Frame(self.paned_window, width=200, bg=self.theme["sidebar_background"])
        self.paned_window.add(self.sidebar_frame)

        # Quick Access Listbox
        self.folder_listbox = tk.Listbox(self.sidebar_frame, bg=self.theme["sidebar_background"], fg=self.theme["sidebar_foreground"])
        self.folder_listbox.pack(fill="x", padx=5, pady=5)
        self.folder_listbox.bind("<<ListboxSelect>>", self.load_selected_folder)

        # Populate Quick Access sidebar
        for folder in self.QUICK_ACCESS_FOLDERS.keys():
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

        # Markdown display area (below file tree)
        self.md_frame = tk.Frame(root, bg=self.theme["background"])
        self.md_frame.pack(fill="both", expand=True)
        self.md_html_frame = HtmlFrame(self.md_frame, width=800, height=400)
        self.md_html_frame.pack(fill="both", expand=True)

    def apply_theme(self):
        """Applies the color theme to the app."""
        self.root.configure(bg=self.theme["background"])
        
    def load_selected_folder(self, event):
        """Loads the selected folder into the tree and file display."""
        selected_index = self.folder_listbox.curselection()
        if selected_index:
            folder_name = self.folder_listbox.get(selected_index)
            folder_path = self.QUICK_ACCESS_FOLDERS[folder_name]
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
        md_files = []  # List to store .md files
        readme_found = None  # Track if README.md exists

        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isfile(full_path):
                    # Identify markdown files
                    if item.lower() == "readme.md":
                        readme_found = full_path
                    elif item.endswith(".md"):
                        md_files.append(full_path)

                    # Choose the right icon
                    icon = self.zip_icon if item.endswith(".zip") else self.file_icon
                    self.file_tree.insert("", "end", text=item, image=icon, values=[full_path])

            # Load priority markdown file
            if readme_found:
                self.display_markdown(readme_found)
            elif md_files:
                self.display_markdown(md_files[0])

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
                    if file_path.endswith(".md"):
                        # Load and display the markdown file
                        self.display_markdown(file_path)
                    else:
                        # Open regular files
                        if os.name == 'nt':  # Windows
                            os.startfile(file_path)
                        elif os.name == 'posix':  # macOS/Linux
                            subprocess.call(['open', file_path])  # macOS
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {e}")

    def display_markdown(self, file_path):
        """Converts markdown file to HTML and displays it with configurable styling."""
        with open(file_path, 'r') as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content)

        # Generate CSS dynamically from JSON
        css = f"""
        <style>
            body {{
                font-family: {self.theme['md_font_family']};
                background-color: {self.theme['md_background_color']};
                color: {self.theme['md_text_color']};
                margin: 20px;
                padding: 20px;
            }}
            h1, h2, h3 {{
                color: {self.theme['md_heading_color']};
            }}
            p {{
                font-size: {self.theme['md_font_size']};
            }}
            a {{
                color: {self.theme['md_link_color']};
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
        """
        
        styled_html_content = css + html_content
        self.md_html_frame.load_html(styled_html_content)


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
            return self.QUICK_ACCESS_FOLDERS.get(folder_name, None)
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()

