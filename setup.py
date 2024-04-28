from setuptools import find_packages, setup

setup(
    name="pyfactoring",
    version="0.0.2",
    python_requires=">=3.10",
    install_requires=[
        "setuptools >= 69.2.0",
        "wheel >= 0.43.0",
        "colorama >= 0.4.6",
        "pydantic_settings >= 2.2.1",
    ],
    extras_require={
        "dev": [
            "ruff >= 0.4.2",
            "pytest >= 8.2.0",
        ],
    },
    packages=find_packages(),
    author="Kiriruso",
    author_email="sosnovskix.kir2001@gmail.com",
    description="This is a package that will allow you to automatically refactor your code.",
    url="https://github.com/Kiriruso/pyfactoring",
    license="MIT",
    entry_points={
        "console_scripts": [
            "pyfactoring = pyfactoring.__main__:main",
        ],
    },
)
