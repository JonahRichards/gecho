import json
import os.path
import numpy as np
from PIL import Image


class ProjectManager:
    def __init__(self, root):
        self.data_root = root
        self.project_dir = None
        self.project_name = None
        self.project_files = []
        self.current_item = None

    def open_item(self, item):
        path = self.project_dir + item
        if os.path.isdir(path):
            self.current_item = None
        name, ext = os.path.splitext(path)
        match ext:
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