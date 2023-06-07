# Generates a "random" service/package/whatever
# implemented as picking random item from corresponding .json/.txt file and returning it

import os.path
import json
import random


class PackagesGenerator:
    def __init__(self,data_dir_name="packages_data.json"):
        data_dirname = os.path.dirname(__file__)
        self.data_file = os.path.join(data_dirname, data_dir_name)

        # Load data
        with open(self.data_file, "r") as fp:
            data_raw = json.load(fp)

        # Only pick one version and drop rest of them to make
        # `generate()` faster
        self.data = []
        for key in data_raw.keys():
            self.data.append(random.choice(data_raw[key]))

        # Sort data randomly, again to make `generate()` faster
        random.shuffle(self.data)
        self.len = len(self.data)

    def count(self):
        return len(self.data)

    def generate(self, count):
        if count > self.len:
            i = 0
        else:
            i = random.randint(0, self.len - count)
        return self.data[i : i + count]


class YumReposGenerator:
    def __init__(self):
        data_dirname = os.path.dirname(__file__)
        self.data = [
            yum_repo
            for yum_repo in open(os.path.join(data_dirname, "yum_repos.txt"), "r")
            .read()
            .split("\n")
        ]

    def count(self):
        return len(self.data)

    def generate(self, count):
        return random.sample(self.data, count)


class EnabledServicesGenerator:
    def __init__(self) -> None:
        data_dirname = os.path.dirname(__file__)
        self.data = [
            service
            for service in open(os.path.join(data_dirname, "enabled_services.txt"), "r")
            .read()
            .split("\n")
        ]

    def count(self):
        return len(self.data)

    def generate(self, count):
        return random.sample(self.data, count)


class InstalledServicesGenerator:
    def __init__(self) -> None:
        data_dirname = os.path.dirname(__file__)
        self.data = [
            service
            for service in open(
                os.path.join(data_dirname, "installed_services.txt"), "r"
            )
            .read()
            .split("\n")
        ]

    def count(self):
        return len(self.data)

    def generate(self, count):
        return random.sample(self.data, count)


class RunningProcessesGenerator:
    def __init__(self) -> None:
        data_dirname = os.path.dirname(__file__)
        self.data = [
            service
            for service in open(
                os.path.join(data_dirname, "running_processes.txt"), "r"
            )
            .read()
            .split("\n")
        ]

    def count(self):
        return len(self.data)

    def generate(self, count):
        return random.sample(self.data, count)
