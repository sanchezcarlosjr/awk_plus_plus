# Awk plus plus

> A domain-specific language designed for data orchestration.

AWK plays a significant role in the UNIX culture and as a toolkit for data science tasks, however, it can turn hard to manage mesh unstructured data with modern formats, protocols, and information retrieval systems to ask structured questions. We propose AWK Plus Plus to make a similar language to AWK, in the sense, that the user employs a query language to ask, receive answers, and execute actions to those that fit the pattern in the ingested data. AWK Plus Plus conceptualized as a metadata layer or storage system middleware, introduces an architecture to manage distributed datasets and LLMs employing a language that segregates resources to enhance functionality by introducing a DuckDB as an in-process database with JSON NET as an assembling language to interpret the URLs with Lark with a Macro system. Like GraphQL where what you see is what you get, but unlike this language, we don’t impose a type system.

AWK Plus Plus tracks a dataset with SQL. A row is scanned for each SQL-based pattern in the program, and for each pattern that matches, the associated actions are executed.

## Contents

```{toctree}
:maxdepth: 2

Overview <readme>
Contributions & Help <contributing>
License <license>
Authors <authors>
Changelog <changelog>
Module Reference <api/modules>
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`

[Sphinx]: http://www.sphinx-doc.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[MyST]: https://myst-parser.readthedocs.io/en/latest/
