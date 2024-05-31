# Pyfactoring
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A Python linter that will help you find and refactor copy-paste

- 🛠️ `pyproject.toml` support
- 🔍 Search for copy-paste and more general code fragments
- 🔧 Fix support, automatic refactoring (isolating clones into a function and replacing them)

## Table Of Contents
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Support](#support)
- [License](#license)

## Getting Started

### Installation

```shell
poetry add --git https://github.com/Kiriruso/pyfactoring.git
```

### Usage

To run Pyfactoring as a linter (default), try any of the following:

```shell
pyfactoring check                        # Lint all files in the current directory (and any subdirectories)
pyfactoring check path/to/code           # Lint all files in `/path/to/code` (and any subdirectories)
pyfactoring check path/to/code/source.py # Lint `source.py`
pyfactoring check paths.txt              # Lint using an input file, treating its contents as newline-delimited command-line arguments
```

> Pyfactoring by default uses `check`, so this command can be omitted

Or, to run Pyfactoring as a formatter:

```shell
pyfactoring format                        # Format all files in the current directory (and any subdirectories)
pyfactoring format path/to/code           # Format all files in `/path/to/code` (and any subdirectories)
pyfactoring format path/to/code/source.py # Format `source.py`
pyfactoring format paths.txt              # Format using an input file, treating its contents as newline-delimited command-line arguments
```

You can also restore formatted files:

```shell
pyfactoring restore # Restores all previously formatted files
```

### Example

Let's say we have the following source code:

```python
# file_containing_clone.py

a, b, c = 1, 2, 3
x, y, z = 1, 2, 3

...

if a > b:
    local_variable = 10
    if a > c:
        print(a)
    elif c < b:
        print(b)
    else:
        print(c)
    print(local_variable)

...

if x > y:
    local_variable = 500
    if x > z:
        print(x)
    elif z < y:
        print(y)
    else:
        print(z)
    print(local_variable)

...
```

Let's analyze the file using:
```shell
pyfactoring check file_containing_clone.py
``` 

And see the following output:
```shell
file_containing_clone.py:6:0: clone found [lines: 9]
file_containing_clone.py:18:0: clone found [lines: 9]
Total clones: 2
Total lines: 18
```

Okay, we found the clones and their locations. 
Let's start the formatting process:
```shell
pyfactoring format file_containing_clone.py 
```

And we will see the following output in the shell:
```shell
file_containing_clone.py:0: Formatted: clone replaced by call file_containing_clone_func_0(a, b, c, 10)
file_containing_clone.py:0: Formatted: clone replaced by call file_containing_clone_func_0(x, y, z, 500)
file_containing_clone.py:0: Formatted: define file_containing_clone_func_0
```

And also changes in the file:
```python
# Pyfactoring: rename this!
def file_containing_clone_func_0(__var_0__, __var_1__, __var_2__, __const_0__):
    if __var_0__ > __var_1__:
        __local_0__ = __const_0__
        if __var_0__ > __var_2__:
            print(__var_0__)
        elif __var_2__ < __var_1__:
            print(__var_1__)
        else:
            print(__var_2__)
        print(__local_0__)

a, b, c = 1, 2, 3
x, y, z = 1, 2, 3

...

file_containing_clone_func_0(a, b, c, 10)

...

file_containing_clone_func_0(x, y, z, 500)

...
```

You can also rollback the formatting:
```shell
pyfactoring restore
```

## Configuration

Pyfactoring can be configured using the `pyproject.toml` file. [Configuration example](https://github.com/Kiriruso/pyfactoring/blob/master/pyproject.example.toml).

If left unspecified, Pyfactoring's default configuration is equivalent to the following pyproject.toml file:

```toml
[tool.pyfactoring]
# Default command, also possible: "format", "restore"
action = "check"

# Disables caching for the command and forces it to be executed from scratch
no_cache = false

# When defining a function, pack constants into *consts
pack_consts = false

# Directories for analysis and formatting
paths = [
    ".",
]

# Exclude a variety of commonly ignored directories.
exclude = [
    "venv",
    ".venv",
    "build",
    "_build",
    "__pycache__",
    "__pypackages__",
    "dist",
    "site-packages",
    ".pyfactoring_cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    ".git",
    ".git-rewrite",
]

# Paths to be chained, such paths will be analyzed as a single file
chain = []

# Or set all files passed to paths as chained
chain_all = false

[tool.pyfactoring.pydioms]
# Activate metric analysis
enable = false

# Output additional information for metric analysis
verbose = false

# Minimum number of trees needed to identify them as a clone
count = 5

# Minimum length of trees for analysis
length = 20

[tool.pyfactoring.pyclones]
# Minimum number of code fragments to identify as a clone
count = 2

# Minimum length of code fragments for analysis
length = 4

# Save code fragment template as "code", also available "tree"
template_mode = "code"

# Output patterns corresponding to each set of clones
template_view = false
```

Configuration options can also be provided using special command line arguments, for example:

```shell
pyfactoring --template-view --pc-count=5 check --chain-all
```

See `pyfactoring --help` for more on Pyfactoring's top-level commands, or `pyfactoring check --help` and `pyfactoring format --help` for more on the linting and formatting commands, respectively.

## Support

Having trouble? Check out the existing issues on [GitHub](https://github.com/Kiriruso/pyfactoring/issues), or feel free to [open a new one](https://github.com/Kiriruso/pyfactoring/issues/new).

You can also ask me for help on [Telegram](https://t.me/kirysha_gaa).

## License

This repository is licensed under the [MIT License](https://github.com/Kiriruso/pyfactoring/blob/master/LICENSE).
