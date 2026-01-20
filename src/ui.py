import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from .config import ConfigManager
from .core import FileEngine
from . import formatters

class SnapCodeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SnapCode - Smart Select & Context Packer")
        self.root.geometry("900x750")
        
        self.engine = FileEngine()
        self.nodes = {}
        self.checked_items = set()
        self.folder_exclude_patterns = []
        self.include_path_var = tk.BooleanVar(value=True)

        self._setup_interface()
        self._load_initial_config()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_interface(self):
        # Using emojis because it's faster and lighter than rendering image assets. 
        # Efficiency is king when you're lazy.
        
        # --- Top Toolbar ---
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED, bg="#f0f0f0")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(toolbar, text="📂 Open Project", command=self.select_folder, bg="#e1e1e1").pack(side=tk.LEFT, padx=5, pady=5)
        
        # Visual separators for that industrial look
        tk.Frame(toolbar, width=2, bg="#aaa").pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        tk.Button(toolbar, text="☑ Select All", command=self.select_all).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="☐ Clear", command=self.deselect_all).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Refresh", command=self.refresh_folder, bg="#ADD8E6").pack(side=tk.LEFT, padx=2)
        
        tk.Frame(toolbar, width=2, bg="#aaa").pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tk.Checkbutton(toolbar, text="Include Path in Header", variable=self.include_path_var, bg="#f0f0f0").pack(side=tk.LEFT, padx=10)

        # --- Filter Sections ---
        # File Filters
        f_frame = tk.Frame(self.root, bg="#e8e8e8")
        f_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        tk.Label(f_frame, text="Include Ext (Empty=All):", bg="#e8e8e8", fg="#006400").pack(side=tk.LEFT, padx=5)
        self.entry_include = tk.Entry(f_frame, width=15)
        self.entry_include.pack(side=tk.LEFT, padx=5)
        
        tk.Label(f_frame, text="Exclude Ext:", bg="#e8e8e8", fg="#8b0000").pack(side=tk.LEFT, padx=15)
        self.entry_exclude = tk.Entry(f_frame, width=35)
        self.entry_exclude.pack(side=tk.LEFT, padx=5)

        # Folder Filters
        cf_frame = tk.Frame(self.root, bg="#e8e8e8")
        cf_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        tk.Label(cf_frame, text="Exclude Folders (Names):", bg="#e8e8e8", fg="#8b0000").pack(side=tk.LEFT, padx=5)
        self.entry_folder_exclude = tk.Entry(cf_frame, width=50)
        self.entry_folder_exclude.pack(side=tk.LEFT, padx=5)

        # --- The Tree (The Meat of the App) ---
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrolly = tk.Scrollbar(tree_frame)
        scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(tree_frame, selectmode="browse", yscrollcommand=scrolly.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrolly.config(command=self.tree.yview)
        self.tree.heading("#0", text="Project Navigator", anchor=tk.W)
        self.tree.bind('<Button-1>', self.on_click)

        # --- Footer Control Panel ---
        footer = tk.Frame(self.root, bg="#ddd")
        footer.pack(fill=tk.X)
        self.lbl_status = tk.Label(footer, text="Ready.", bg="#ddd", anchor="w")
        self.lbl_status.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        self.combo_format = ttk.Combobox(footer, values=["Markdown (Standard)", "XML (Claude/Anthropic)", "String List"], state="readonly")
        self.combo_format.pack(side=tk.LEFT, padx=5)
        
        # High contrast button because we want you to click it
        self.btn_next = tk.Button(footer, text="GENERATE OUTPUT", command=self.process_files, state=tk.DISABLED, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
        self.btn_next.pack(side=tk.RIGHT, padx=10, pady=10)

    def _load_initial_config(self):
        # Loading your past mistakes from the config file
        conf = ConfigManager.load()
        if conf:
            self.entry_include.insert(0, conf.get("include_ext", ""))
            self.entry_exclude.insert(0, conf.get("exclude_ext", ""))
            self.entry_folder_exclude.insert(0, conf.get("exclude_folders", ""))
            self.include_path_var.set(conf.get("include_path", True))
            self.combo_format.current(conf.get("format_index", 0))
            if "geometry" in conf: self.root.geometry(conf["geometry"])
        else:
            self.entry_exclude.insert(0, ".exe, .dll, .bin, .jpg, .png, .gif, .mp4, .zip, .pdf, .pyc, .o, .obj")
            self.entry_folder_exclude.insert(0, "__pycache__, .git, node_modules, venv, .idea, .vscode")
            self.combo_format.current(0)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.engine.load_gitignore(path)
            self._update_folder_exclude_list()
            self.tree.delete(*self.tree.get_children())
            self.nodes = {}
            self.checked_items = set()
            self._populate_tree("", path)
            self.btn_next.config(state=tk.NORMAL)
            self.lbl_status.config(text=f"Root: {os.path.basename(path)}")

    def _update_folder_exclude_list(self):
        raw = self.entry_folder_exclude.get()
        self.folder_exclude_patterns = [x.strip() for x in raw.split(',') if x.strip()]

    def _populate_tree(self, parent, path):
        # Recursion: Because the project is probably deeper than your patience
        try:
            items = os.listdir(path)
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x))
            for item in items:
                if self.engine.is_ignored(item): continue
                abspath = os.path.join(path, item)
                is_dir = os.path.isdir(abspath)
                if is_dir and item in self.folder_exclude_patterns: continue
                oid = self.tree.insert(parent, "end", text=f"☐ {item}", open=False)
                self.nodes[oid] = abspath
                if is_dir: self._populate_tree(oid, abspath)
        except: pass

    def on_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id or os.path.isdir(self.nodes.get(item_id, "")): return
        
        # Smart toggle logic. Don't touch folders, we only want the files.
        txt = self.tree.item(item_id, "text")
        if "☐" in txt:
            self.tree.item(item_id, text=txt.replace("☐", "☑", 1))
            self.checked_items.add(item_id)
        else:
            self.tree.item(item_id, text=txt.replace("☑", "☐", 1))
            self.checked_items.remove(item_id)

    def select_all(self):
        # The industrial select: Filter, check, and move on.
        inc = self.engine.parse_extensions(self.entry_include.get())
        exc = self.engine.parse_extensions(self.entry_exclude.get())
        count = 0
        for oid, path in self.nodes.items():
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                if exc and ext in exc: continue
                if inc and ext not in inc: continue
                txt = self.tree.item(oid, "text")
                if "☐" in txt:
                    self.tree.item(oid, text=txt.replace("☐", "☑", 1))
                    self.checked_items.add(oid)
                    count += 1
        self.lbl_status.config(text=f"Selected: {count} files.")

    def deselect_all(self):
        for oid in self.nodes:
            txt = self.tree.item(oid, "text")
            if "☑" in txt: self.tree.item(oid, text=txt.replace("☑", "☐", 1))
        self.checked_items.clear()
        self.lbl_status.config(text="Selection cleared.")

    def refresh_folder(self):
        # Scorched earth refresh: Re-read everything.
        if not self.engine.root_folder: return
        self.engine.load_gitignore(self.engine.root_folder)
        self._update_folder_exclude_list()
        self.select_folder() 

    def process_files(self):
        if not self.checked_items: return
        data = []
        for oid in self.checked_items:
            rel, content = self.engine.get_content(self.nodes[oid])
            if content: data.append((rel, content))
        
        output = formatters.format_output(data, self.combo_format.get(), self.include_path_var.get())
        
        # Atomic clipboard operation
        self.root.clipboard_clear()
        self.root.clipboard_append(output)
        self.root.update()
        messagebox.showinfo("Success", f"Processed {len(data)} files.\nContext packed and ready for transport.\n\n✅ Paste with Ctrl + V")

    def _on_close(self):
        # Save state before killing the process
        ConfigManager.save({
            "include_ext": self.entry_include.get(),
            "exclude_ext": self.entry_exclude.get(),
            "exclude_folders": self.entry_folder_exclude.get(),
            "include_path": self.include_path_var.get(),
            "format_index": self.combo_format.current(),
            "geometry": self.root.geometry()
        })
        self.root.destroy()