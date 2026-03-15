import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="opl-rhcloud-perf-team-extras",
    version="0.0.1",
    maintainer="Jan Hutar",
    maintainer_email="jhutar@redhat.com",
    description="Our performance library, extra bits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redhat-performance/opl",
    packages=setuptools.find_namespace_packages(include=["opl.*", "opl"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.6",
    install_requires=[
        "kafka-python",
        "locust",
        "psycopg2-binary",
        "numpy",
    ],
    package_data={
        "opl": [
            "*.yaml",
            "*.json",
            "*.txt",
        ],
        "opl.generators": [
            "*.json",
            "*.j2",
            "*.txt",
        ],
    },
    entry_points={
        "console_scripts": [
            "script-skip-to-end.py = opl.skip_to_end:main",
            "script-manage-db.py = opl.manage_db:main",
            "script-hbi-populate.py = opl.hbi_utils:populate_main",
            "script-hbi-cleanup.py = opl.hbi_utils:cleanup_main",
            "create_packages_template_from_dnf_repoquery.py = opl.create_packages_template_from_dnf_repoquery:parse_repoquery_output_from_stdin",
            "horreum_api.py = opl.horreum_api:main",
        ],
    },
)
