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


AWK has long been a cornerstone of UNIX culture and a powerful tool for data science tasks. However, it can become difficult to manage unstructured data meshes, especially when dealing with modern formats, protocols, and information retrieval systems, where structured queries are needed. We propose AWK++, a language inspired by AWK, where users can query, receive answers, and execute actions based on patterns in ingested data.

AWK++ is conceptualized as a metadata layer or middleware for storage systems, introducing an architecture designed to handle distributed datasets and large language models (LLMs). The language segregates resources to enhance functionality by incorporating DuckDB as an in-process database and Jsonnet as an assembly language to interpret URLs, along with Lark for macro-based parsing. Like GraphQL, AWK++ follows a "what you see is what you get" model; however, unlike GraphQL, it does not impose a strict type system. Additionally, others systems can query an AWK++ service via HTTP, providing flexibility for external interacdtions.


## Features
* **Fuzzy regex engine** and **semantic search** for retrieving information from an in-process database.
* **End-user programming** capabilities.
* **Orthogonal Persistence** implemented with DuckDB and SQL Macros.
* **Transparent reference** using Jsonnet, with plans to execute we plan to execute this feature via Dask.
* **URL interpreter** for managing different data sources, protocols, and schedulers with plugins.

## Installation from pip
Install the package with:
```bash
pip install awk_plus_plus
```

# CLI Usage
You output your data to JSON with the `cti` command.

## Web service
The command runs a web service with Gradio, allowing you to execute your expressions through a user-friendly user interface or by making HTTP requests.
```bash
cti run-webservice
```

## Jsonnet support
### Hello world
```bash
cti i "Hello world" -p -v 4
```
Output:
```bash
"Hello world"
````

### Jsonnet support
```bash
cti i '{"keys":: ["AWK", "SED", "SHELL"], "languages": [std.asciiLower(x) for x in self.keys]}'
```

Output:
```json
{
   "languages": [
        "awk",
        "sed",
        "shell"
   ]
}
```

## URL interpreter
Our step further is the URL interpreter which allows you to manage different data sources with an unique syntax across a set of plugins.

## STDIN, STDOUT, STDERR
Traditional UNIX streams are supported in AWK++. For instance, the following command will read from a file with content `hello\nworld<EOF>` and write it to the standard output:

```bash
cat file.txt | cti i '{"lines": interpret("stream://stdin?strip=true")}'
```

Output:
```bash
{
   "lines": [
        "hello",
        "world"
   ]
}
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

## Connect and call different data sources in one expression
```jsonnet
{
   "emails": i("sql:SELECT subject FROM `%s`" %  self.email),
   // This expression saves the unseen emails from your inbox, as defined in your keyring, using IMAP query criteria. It then returns the netloc hash, which refers to the table.
   "email": i(i("keyring://backend/awk_plus_plus/primary_email")+"?q=UNSEEN")
}
```

# Protocols and Plugins
* pop3://
* imap://
* keyring://backend/{service}/{username}
* sql:{expression}
* https://
* file:/

## Note

This project has been set up using [PyScaffold] 4.5 and the [dsproject extension] 0.0.post167+g4386552.

[conda]: https://docs.conda.io/
[pre-commit]: https://pre-commit.com/
[Jupyter]: https://jupyter.org/
[nbstripout]: https://github.com/kynan/nbstripout
[Google style]: http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[PyScaffold]: https://pyscaffold.org/
[dsproject extension]: https://github.com/pyscaffold/pyscaffoldext-dsproject
