import json
import os

CONFIG_FILE = "config_filetree.json"

class ConfigManager:
    @staticmethod
    def load():
        if not os.path.exists(CONFIG_FILE):
            return None
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

    @staticmethod
    def save(data):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving configuration: {e}")