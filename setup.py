from setuptools import setup


with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name="ash-parser",
    install_requires=requirements,
    entry_points={
        "console_scripts": ["ash-parser = ash_parser:main"],
    }
)