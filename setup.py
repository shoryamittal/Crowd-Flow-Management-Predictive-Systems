from setuptools import setup, find_packages

import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

req_file = "requirements-full.txt" if os.path.exists("requirements-full.txt") else ("requirements.txt" if os.path.exists("requirements.txt") else None)
if req_path := req_file:
    with open(req_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    requirements = []

setup(
    name="sentinel-ai",
    version="2.5.0",
    author="Team X Factor — MIT School of Computing",
    description="SENTINEL-AI: Action-Aware Crowd Disaster Prevention & Incident Copilot for High-Density Railway Stations (Indian Railways)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shoryamittal/Crowd-Flow-Management-Predictive-Systems",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sentinel-ai=deploy:main",
            "sentinel-monitor=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
