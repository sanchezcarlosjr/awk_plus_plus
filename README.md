[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![PyPI-Server](https://img.shields.io/pypi/v/awk_plus_plus.svg)](https://pypi.org/project/awk_plus_plus/)

<!-- These are examples of badges you might also want to add to your README. Update the URLs accordingly.
[![Built Status](https://api.cirrus-ci.com/github/<USER>/awk_plus_plus.svg?branch=main)](https://cirrus-ci.com/github/<USER>/awk_plus_plus)
[![ReadTheDocs](https://readthedocs.org/projects/awk_plus_plus/badge/?version=latest)](https://awk_plus_plus.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/awk_plus_plus/main.svg)](https://coveralls.io/r/<USER>/awk_plus_plus)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/awk_plus_plus.svg)](https://anaconda.org/conda-forge/awk_plus_plus)
[![Monthly Downloads](https://pepy.tech/badge/awk_plus_plus/month)](https://pepy.tech/project/awk_plus_plus)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/awk_plus_plus)
-->

# awk_plus_plus

> A domain-specific language designed for data orchestration. 

## Features
* Fuzzy modern regex engine
* Semantic search
* Orthogonal Persistence based on DuckDB
* Transparent reference with Jsonnet. We plan to execute this future with Dask.
* URL interpreter to manage data sources.

## Installation from pip
Install the package with:
```bash
pip install awk_plus_plus
```

# CLI Usage
You output your data to JSON with the `cti` command.

## JSONNET support
### Hello world
```bash
cti i "Hello world" -p -v 4
```

### Jsonnet support
```bash
cti i '{"keys":: ["AWK", "SED", "SHELL"], "languages": [std.asciiLower(x) for x in self.keys]}'
```

## URL interpreter
Our step further is the URL interpreter which allows you to manage different data sources with an unique syntax across a set of plugins.

## STDIN, STDOUT, STDERR
```bash
cti i '{"lines": interpret("stream://stdin?strip=true")}'
```

## Imap
```bash
cti i '{"emails": interpret("imap://USER:PASSWORD@HOST:993/INBOX")}'
```

## Keyring
```bash
cti i '{"email":: interpret("keyring://backend/awk_plus_plus/email"), "emails": interpret($.email)}'
```

## Files
```bash
cti i 'interpret("**/*.csv")'
```

## SQL
```bash
cti i 'interpret("sql:SELECT * FROM email")'
```


## Note

This project has been set up using [PyScaffold] 4.5 and the [dsproject extension] 0.0.post167+g4386552.

[conda]: https://docs.conda.io/
[pre-commit]: https://pre-commit.com/
[Jupyter]: https://jupyter.org/
[nbstripout]: https://github.com/kynan/nbstripout
[Google style]: http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[PyScaffold]: https://pyscaffold.org/
[dsproject extension]: https://github.com/pyscaffold/pyscaffoldext-dsproject
