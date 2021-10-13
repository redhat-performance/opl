# Generates a "random" service/package/whatever
# implemented as picking random item from corresponding .json/.txt file and returning it

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


class YumReposGenerator:
    def __init__(self):
        data_dirname = os.path.dirname(__file__)
        self.data = [yum_repo for yum_repo in open(os.path.join(data_dirname, 'yum_repos.txt'), 'r').read().split('\n')]
    
    def count(self):
        return len(self.data)
    
    def generate(self, count):
        return random.sample(self.data, count)


class EnabledServicesGenerator:
    def __init__(self) -> None:
        data_dirname = os.path.dirname(__file__)
        self.data = [service for service in open(os.path.join(data_dirname, 'enabled_services.txt'), 'r').read().split('\n')]
    
    def count(self):
        return len(self.data)
    
    def generate(self, count):
        return random.sample(self.data, count)


class InstalledServicesGenerator:
    def __init__(self) -> None:
        data_dirname = os.path.dirname(__file__)
        self.data = [service for service in open(os.path.join(data_dirname, 'installed_services.txt'), 'r').read().split('\n')]
    
    def count(self):
        return len(self.data)
    
    def generate(self, count):
        return random.sample(self.data, count)


class RunningProcessesGenerator:
    def __init__(self) -> None:
        data_dirname = os.path.dirname(__file__)
        self.data = [service for service in open(os.path.join(data_dirname, 'running_processes.txt'), 'r').read().split('\n')]
    
    def count(self):
        return len(self.data)
    
    def generate(self, count):
        return random.sample(self.data, count)
