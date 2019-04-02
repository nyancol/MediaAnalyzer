#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
from setuptools import find_packages, setup

# Package meta-data.
NAME = 'Media Analyzer'
AUTHOR = 'Yann Colina'
EMAIL = "yanncolina@gmail.com"
URL = "https://github.com/nyancol/MediaAnalyzer"

HERE = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
with io.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = '\n' + f.read()

requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Where the magic happens:
setup(
    name=NAME,
    version="0.1.0",
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "publisher_select=media_analyzer.core.pull:select_publishers",
            "pull_tweets=media_analyzer.core.pull:pull_tweets",
            "process_tweets=media_analyzer.core.process:main",
            "store_records=media_analyzer.core.store:main",
        ]
    },
    python_requires=">=3.6",
    install_requires=requirements,
    include_package_data=True,
    license='MIT License',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
