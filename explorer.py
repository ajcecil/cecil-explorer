import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# Predefined quick-access folders (customize as needed)
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
        self.root.title("Custom File Explorer")
        self.root.geometry("900x600")

        # Load icons
        self.folder_icon = ImageTk.PhotoImage(Image.open("icons/ground-grass-cube-cross-section-isometric-free-stock-image.png").resize((16, 16)))
        self.file_icon = ImageTk.PhotoImage(Image.open("icons/ground-grass-cube-cross-section-isometric-free-stock-image.png").resize((16, 16)))
        self.zip_icon = ImageTk.PhotoImage(Image.open("icons/ground-grass-cube-cross-section-isometric-free-stock-image.png").resize((16, 16)))

        # Create a toolbar frame
        self.toolbar = tk.Frame(root, bg="gray", height=30)
        self.toolbar.pack(side="top", fill="x")

        # Toolbar buttons
        ttk.Button(self.toolbar, text="Rename", command=self.rename_item).pack(side="left", padx=5, pady=2)
        ttk.Button(self.toolbar, text="Delete", command=self.delete_item).pack(side="left", padx=5, pady=2)
        ttk.Button(self.toolbar, text="Unzip", command=self.unzip_item).pack(side="left", padx=5, pady=2)

        # Sidebar for Quick Access
        self.sidebar = tk.Frame(root, width=200, bg="lightgray")
        self.sidebar.pack(side="left", fill="y")

        self.folder_listbox = tk.Listbox(self.sidebar)
        self.folder_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.folder_listbox.bind("<<ListboxSelect>>", self.load_selected_folder)

        # Populate Quick Access sidebar
        for folder in QUICK_ACCESS_FOLDERS.keys():
            self.folder_listbox.insert(tk.END, folder)

        # Main File Explorer View
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(side="right", expand=True, fill="both")

        self.tree = ttk.Treeview(self.main_frame)
        self.tree.heading("#0", text="File Explorer", anchor="w")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)

        # Button to Open a Folder Manually
        self.open_btn = ttk.Button(self.main_frame, text="Open Folder", command=self.open_folder)
        self.open_btn.pack(pady=5)

    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.tree.delete(*self.tree.get_children())  # Clear previous entries
            self.populate_tree(folder, "")

    def load_selected_folder(self, event):
        selected_index = self.folder_listbox.curselection()
        if selected_index:
            folder_name = self.folder_listbox.get(selected_index)
            folder_path = QUICK_ACCESS_FOLDERS[folder_name]
            self.tree.delete(*self.tree.get_children())  # Clear previous entries
            self.populate_tree(folder_path, "")

    def populate_tree(self, path, parent=""):
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    node = self.tree.insert(parent, "end", text=item, image=self.folder_icon, open=False, values=[full_path])
                    self.tree.insert(node, "end", text="Loading...")  # Placeholder for lazy loading
                else:
                    icon = self.zip_icon if item.endswith(".zip") else self.file_icon
                    self.tree.insert(parent, "end", text=item, image=icon, values=[full_path])
        except PermissionError:
            pass

    def on_double_click(self, event):
        selected_item = self.tree.focus()
        path = self.tree.item(selected_item, "values")
        if path:
            path = path[0]
            if os.path.isdir(path):
                self.tree.delete(*self.tree.get_children(selected_item))  # Clear placeholder
                self.populate_tree(path, selected_item)

    def rename_item(self):
        selected_item = self.tree.focus()
        path = self.tree.item(selected_item, "values")
        if path:
            path = path[0]
            new_name = filedialog.asksaveasfilename(initialdir=os.path.dirname(path), initialfile=os.path.basename(path))
            if new_name:
                os.rename(path, new_name)
                self.tree.item(selected_item, text=os.path.basename(new_name), values=[new_name])

    def delete_item(self):
        selected_item = self.tree.focus()
        path = self.tree.item(selected_item, "values")
        if path:
            path = path[0]
            if messagebox.askyesno("Delete", f"Are you sure you want to delete {path}?"):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    self.tree.delete(selected_item)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete: {e}")

    def unzip_item(self):
        selected_item = self.tree.focus()
        path = self.tree.item(selected_item, "values")
        if path and path[0].endswith(".zip"):
            extract_to = filedialog.askdirectory()
            if extract_to:
                try:
                    shutil.unpack_archive(path[0], extract_to)
                    messagebox.showinfo("Unzip", "File extracted successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not unzip: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()
