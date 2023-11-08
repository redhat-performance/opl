#!/usr/bin/env python3

import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="opl-rhcloud-perf-team-core",
    version="0.0.1",
    maintainer="Jan Hutar",
    maintainer_email="jhutar@redhat.com",
    description="Our performance library, core bits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TODO/TODO",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires='>=3.6',
    install_requires=[
        "Jinja2>=3.0",
        "boto3",
        "junitparser",
        "PyYAML",
        "requests",
        "tabulate",
        "deepdiff",
    ],
    package_data={
        "opl": [
            "status_data_report.txt",
            "cluster_read_example.yaml",
            "cluster_read_sat.yaml",
        ],
        "opl.investigator": [
            "sample_config.yaml",
        ],
    },
    entry_points={
        "console_scripts": [
            "cluster_read.py = opl.cluster_read:main",
            "pass_or_fail.py = opl.pass_or_fail:main",
            "junit_cli.py = opl.junit_cli:main",
            "rp_updater.py = opl.rp_updater:main",
            "status_data_diff.py = opl.status_data:main_diff",
            "status_data.py = opl.status_data:main",
            "status_data_report.py = opl.status_data:main_report",
            "status_data_updater.py = opl.status_data_updater:main",
        ],
    },
)
