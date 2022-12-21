from setuptools import setup, find_packages

setup(
    name="SQLiteJSON",
    version="0.0.1",
    url="https://github.com/cgjosephlee/SQLiteJSON",
    author="Joseph Lee",
    author_email="cgjosephlee@gmail.com",
    description="Use SQLite as a simple local NoSQL database to store json documents.",
    packages=find_packages(),
    install_requires=[
        "sqlite>=3.38",
        "tqdm"
        ],
)
