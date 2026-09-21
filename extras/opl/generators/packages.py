"""Generators picking random items from data files (packages, services, ...)."""
# Generates a "random" service/package/whatever
# implemented as picking random item from corresponding .json/.txt file and returning it

import json
import os.path
import random


class PackagesGenerator:
    """Generate random packages from a JSON data file."""

    def __init__(self, package_file_name="packages_data.json"):
        data_dirname = os.path.dirname(__file__)
        self.data_file = os.path.join(data_dirname, package_file_name)

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
        """Return number of available packages."""
        return len(self.data)

    def generate(self, count):
        """Return up to count random consecutive packages."""
        if count > self.len:
            i = 0
        else:
            i = random.randint(0, self.len - count)
        return self.data[i : i + count]


class YumReposGenerator:
    """Generate random yum repositories."""

    def __init__(self):
        data_dirname = os.path.dirname(__file__)
        self.data = list(
            open(os.path.join(data_dirname, "yum_repos.txt"), encoding="utf-8")
            .read()
            .split("\n")
        )

    def count(self):
        """Return number of available yum repositories."""
        return len(self.data)

    def generate(self, count):
        """Return count random yum repositories."""
        return random.sample(self.data, count)


class EnabledServicesGenerator:
    """Generate random enabled services."""

    def __init__(self) -> None:
        data_dirname = os.path.dirname(__file__)
        self.data = list(
            open(os.path.join(data_dirname, "enabled_services.txt"), encoding="utf-8")
            .read()
            .split("\n")
        )

    def count(self):
        """Return number of available enabled services."""
        return len(self.data)

    def generate(self, count):
        """Return count random enabled services."""
        return random.sample(self.data, count)


class InstalledServicesGenerator:
    """Generate random installed services."""

    def __init__(self) -> None:
        data_dirname = os.path.dirname(__file__)
        self.data = list(
            open(
                os.path.join(data_dirname, "installed_services.txt"), encoding="utf-8"
            )
            .read()
            .split("\n")
        )

    def count(self):
        """Return number of available installed services."""
        return len(self.data)

    def generate(self, count):
        """Return count random installed services."""
        return random.sample(self.data, count)


class RunningProcessesGenerator:
    """Generate random running processes."""

    def __init__(self) -> None:
        data_dirname = os.path.dirname(__file__)
        self.data = list(
            open(
                os.path.join(data_dirname, "running_processes.txt"), encoding="utf-8"
            )
            .read()
            .split("\n")
        )

    def count(self):
        """Return number of available running processes."""
        return len(self.data)

    def generate(self, count):
        """Return count random running processes."""
        return random.sample(self.data, count)
