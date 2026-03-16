import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

core_path = os.path.abspath('core')
extras_path = os.path.abspath('extras')

setuptools.setup(
    name="opl-rhcloud-perf-team",
    version="0.0.1",
    maintainer="Jan Hutar",
    maintainer_email="jhutar@redhat.com",
    description="Our performance library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redhat-performance/opl",
    packages=[], # Explicitly empty
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.6",
    install_requires=[
        f"opl-rhcloud-perf-team-core @ file://{core_path}",
        f"opl-rhcloud-perf-team-extras @ file://{extras_path}"
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
            "pyfakefs",
            "responses",
        ]
    },
)
