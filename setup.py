from setuptools import setup, find_packages

setup(
    name="dj-polyglot",
    version="0.12.0",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/Yeoki-ERP/dj_polyglot",
    install_requires=[
        "Django>=3.2",
        "polib>=1.2.0",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
    ],
)