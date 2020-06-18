#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="opl-rhcloud-perf-team",
    version="0.0.1",
    maintainer="Jan Hutar",
    maintainer_email="jhutar@redhat.com",
    description="Our performance library",
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
        "Jinja2",
        "junitparser",
        "kafka-python",
        "locustio==0.14.6",
        "numpy",
        "psycopg2-binary",
        "pyyaml",
        "PyYAML",
        "requests",
        "scipy",
        "tabulate",
        "deepdiff",
    ],
    package_data={
        "opl": [
            "status_data_report.txt",
            "cluster_read_example.yaml",
            "cluster_read_sat.yaml",
        ],
        "opl.generators": [
            "inventory_egress_data.json",
            "inventory_egress_template.json.j2",
        ],
    },
    entry_points={
        "console_scripts": [
            "cluster_read.py = opl.cluster_read:main",
            "data_investogator.py = opl.data_investogator:main",
            "junit_cli.py = opl.junit_cli:main",
            "status_data_diff.py = opl.status_data:main_diff",
            "status_data.py = opl.status_data:main",
            "status_data_report.py = opl.status_data:main_report",
            "script-skip-to-end.py = opl.skip_to_end:main",
            "script-manage-db.py = opl.manage_db:main",
        ],
    },
)
