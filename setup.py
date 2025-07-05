#!/usr/bin/env python3
"""
Setup script for Email Ledger POC.
"""

from setuptools import setup, find_packages
import os

def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="email-ledger-poc",
    version="1.0.0",
    author="Risma",
    author_email="development.risma@gmail.com",
    description="AI-powered email scraping to live ledger system",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/email-ledger-poc",
    project_urls={
        "Bug Tracker": "https://github.com/example/email-ledger-poc/issues",
        "Documentation": "https://github.com/example/email-ledger-poc#readme",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "email-ledger=src.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="email,ai,ledger,financial,automation",
    license="MIT",
)
