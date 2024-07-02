import json
import os.path
import pickle

import numpy as np
from PIL import Image


class ProjectManager:
    def __init__(self, root):
        self.data_root = root
        self.project_dir = None
        self.project_name = None
        self.project_files = []
        self.current_item = None
        self.current_item_path = ""
        self.current_tab = 0

    def sort_files(self):
        self.project_files = self._sort_files(self.project_files)

    def _sort_files(self, items):
        items.sort(key=lambda item: item.casefold() if isinstance(item, str) else item[0].casefold())
        return [item if isinstance(item, str) else (item[0], self._sort_files(item[1])) for item in items]

    def add_file(self, file):
        self.project_files.append(file)
        self.sort_files()

    def _sort_key(self, item):
        # If the item is a string, return the string itself
        if isinstance(item, str):
            return item
        # If the item is a tuple, return the first element of the tuple
        elif isinstance(item, tuple) and isinstance(item[0], str):
            return item[0]
        else:
            raise ValueError("Invalid item in list")

    def open_item(self, item):
        path = self.project_dir + item
        if os.path.isdir(path):
            self.current_item = None
        name, ext = os.path.splitext(path)
        match ext:
            case ".geom":
                with open(path, "rb") as file:
                    self.current_item = pickle.load(file)
            case ".npy":
                self.current_item = np.load(path)
            case '.jpg' | '.jpeg' | '.png' | '.tif' | '.tiff':
                self.current_item = np.array(Image.open(path))

    def open_project(self, directory):
        self.project_files = self._scan_directory(directory)
        self.project_dir = directory + "/"

    def _scan_directory(self, directory):
        import os
        directory_contents = []
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            if os.path.isdir(path):
                directory_contents.append((item, self._scan_directory(path)))
            else:
                directory_contents.append(item)
        return directory_contents
