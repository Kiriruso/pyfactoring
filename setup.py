from setuptools import setup, find_packages

setup(
    name='pyfactoring',
    version='0.1',
    python_requires='>=3.10',
    install_requires=['setuptools'],
    packages=find_packages(),
    author='Kiriruso',
    author_email='sosnovskix.kir2001@gmail.com',
    description='This is a package that will allow you to automatically refactor your code.',
    url='https://github.com/Kiriruso/pyfactoring',
    license='MIT',
    entry_points={
        'console_scripts': [
            'pyfactoring = pyfactoring.__main__:main',
        ],
    },
)
