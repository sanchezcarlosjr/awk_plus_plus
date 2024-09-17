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

> A  language designed for data orchestration. 

## Features
* Fuzzy regex engine and Semantic search to retrieve information in an in-process DB.
* End-user programming.
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

## Jsonnet support
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

## Leverage the Power of Reference with Jsonnet
Unlike other programming languages that require multiple steps to reference data, Jsonnet requires only one step, thanks to its reference mechanism.
This is particularly useful for data engineers who want to connect different services in a topological order. The code below represents this scenario in Python:
```python

import requests

def fetch_character(id):
    url = f"https://rickandmortyapi.com/api/character/{id}"
    response = requests.get(url)
    return response.json()

def process_character(character):
    # Add new 'image' field with processed URL
    character['image'] += f"?awk_download=data/{character['name'].replace(' ', '_').lower()}.jpeg"
    
    # Process 'episode' field, fetching additional data if necessary
    character['episode'] = [requests.get(episode).json() for episode in character['episode']]
    
    return character


print([process_character(fetch_character(id)) for id in [1, 2, 3, 4, 5, 6]])

```
Contrary to the previous Python code, Jsonnet allows you to leverage the power of referential transparency. The previous code is equivalent in Jsonnet to:

```jsonnet
[
   i("https://rickandmortyapi.com/api/character/%s" % id) + 
    {image: i(super.image+"?awk_download=data/"+std.strReplace(std.asciiLower(super.name), " ", "_")+".jpeg")} + 
    {episode: [i(episode) for episode in super.episode]}
   for id in [1,2,3,4,5,6]
]
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
