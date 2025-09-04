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
    url="https://github.com/redhat-performance/opl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Jinja2>=3.0",
        "boto3",
        "junitparser",
        "kafka-python",
        "locust",
        "psycopg2-binary",
        "PyYAML",
        "requests",
        "tabulate",
        "deepdiff",
        "numpy",
        # Other package dependencies
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
            # Other development dependencies
        ]
    },
    package_data={
        "opl": [
            "status_data_report.txt",
            "cluster_read_example.yaml",
            "cluster_read_sat.yaml",
        ],
        "opl.generators": [
            "inventory_egress_data.json",
            "inventory_egress_template.json.j2",
            "inventory_ingress_RHSM_template.json.j2",
            "inventory_ingress_puptoo_template.json.j2",
            "inventory_ingress_yupana_template.json.j2",
            "inventory_ingress_InvGitUtilsPayload_template.json.j2",
            "packages_data.json",
            "enabled_services.txt",
            "installed_services.txt",
            "running_processes.txt",
            "yum_repos.txt",
            "chrome_notifications_template.json.j2",
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
            "script-skip-to-end.py = opl.skip_to_end:main",
            "script-manage-db.py = opl.manage_db:main",
            "script-hbi-populate.py = opl.hbi_utils:populate_main",
            "script-hbi-cleanup.py = opl.hbi_utils:cleanup_main",
            "shovel.py = opl.shovel:main",
            "create_packages_template_from_dnf_repoquery.py = opl.create_packages_template_from_dnf_repoquery:parse_repoquery_output_from_stdin",
            "horreum_api.py = opl.horreum_api:main",
        ],
    },
)
