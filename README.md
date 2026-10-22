# sqlite-playground

A task notebook small enough to read end to end. It demonstrates parameterized CRUD, transactional writes and incremental schema upgrades with the Python standard library.

## Install

Requires Python 3.11 or newer. From this directory:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

## Use

```sh
sqlite-playground init
sqlite-playground seed
sqlite-playground add 'Review query plan'
sqlite-playground list
sqlite-playground update 1 --done yes
sqlite-playground list --done yes
sqlite-playground delete 1
```

`--db path.db` before the subcommand selects a database. Every command initializes or migrates it. Version 1 creates tasks; version 2 adds an index for status filters. Newer unknown schemas are rejected. `seed` adds three demonstration tasks each time it runs. Empty titles and nonexistent IDs return CLI errors. List results are JSON.

## Development

```sh
python -m unittest discover -s tests -v
```

Licensed under MIT.
