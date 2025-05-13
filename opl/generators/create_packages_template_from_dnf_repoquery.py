import argparse
import sys
import json


def parse_repoquery_output_from_stdin():
    """
    This script helps process output of dnf with packages for a given host into a generator-friendly structure to generate installed packages with. Before using this, run `dnf repoquery --available --show-duplicates` on your desired machine/VM to get a list of all packages that could be installed on your mahcine and either pipe it into this script's stdin using `|`.

    :return: Dictionary of package names and their versions into stdout. You might want to store the results into a file using `>/path/to/output/file.json`.
    Made with the help of an LLM.
    """
    packages = {}

    for line in sys.stdin:
        line = line.strip()
        if line:
            parts = line.split("-0:", 1)
            if len(parts) == 2:
                package_name = parts[0]
                version_arch = parts[1]
                # Add to dictionary:
                if package_name not in packages:
                    packages[package_name] = []
                if (
                    version_arch not in packages[package_name]
                ):  # Avoid duplicates just in case
                    packages[package_name].append(f"{package_name}-0:{version_arch}")

    return packages


def main():
    parser = argparse.ArgumentParser(
        description="This script helps process output of dnf with packages for a given host into a generator-friendly structure to generate installed packages with. Before using this, run `dnf repoquery --available --show-duplicates` on your desired machine/VM to get a list of all packages that could be installed on your mahcine and either pipe it into this script's stdin using `|`. :return: Dictionary of package names and their versions into stdout. You might want to store the results into a file using `>/path/to/output/file.json`. Made with the help of an LLM.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.parse_args()
    result = parse_repoquery_output_from_stdin()
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
