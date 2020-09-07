import os.path
import json
import random


class PackagesGenerator:
    def __init__(self):
        data_dirname = os.path.dirname(__file__)
        self.data_file = os.path.join(data_dirname, 'packages_data.json')
        with open(self.data_file, 'r') as fp:
            self.data = json.load(fp)

    def count(self):
        return len(self.data)

    def generate(self, count):
        return [random.choice(self.data[key])
                for key in random.sample(self.data.keys(), count)]
