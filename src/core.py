import os
import fnmatch

class FileEngine:
    def __init__(self):
        self.root_folder = ""
        self.gitignore_patterns = []

    def load_gitignore(self, folder):
        self.root_folder = folder
        patterns = []
        git_path = os.path.join(folder, ".gitignore")
        if os.path.exists(git_path):
            try:
                with open(git_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        l = line.strip()
                        # Skip garbage and comments
                        if l and not l.startswith('#'):
                            if l.endswith('/'): l = l[:-1]
                            patterns.append(l)
            except: pass
        self.gitignore_patterns = patterns
        return patterns

    def is_ignored(self, item_name):
        # Hardcoded rules because .git is a disease
        if item_name == ".git": return True
        for pattern in self.gitignore_patterns:
            if fnmatch.fnmatch(item_name, pattern): return True
        return False

    def parse_extensions(self, text_input):
        # Clean the user input because people can't type
        if not text_input.strip(): return set()
        return {("." + p.strip().lower()).replace("..", ".") for p in text_input.split(',') if p.strip()}

    def get_content(self, path):
        # Extraction protocol: Read it, rel-path it, return it.
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                rel_path = os.path.relpath(path, self.root_folder).replace("\\", "/")
                return rel_path, f.read()
        except: return None, None