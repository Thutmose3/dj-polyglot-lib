from setuptools import setup, find_packages

setup(
    name="dj-polyglot",
    version="0.18.0",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/Thutmose3/dj-polyglot-lib",
    install_requires=[
        "Django>=3.2",
        "polib>=1.2.0",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
    ],
)