
# DJ POlyglot

**DJ POlyglot** is a Django library that provides python manage.py commands manage translations strings in .po files.
It will read your .po files, and push the strings to the translation service. It will also read the translations from the translation service and update your .po files.

It works together with the Django application UI: https://github.com/Thutmose3/dj-polyglot-app

## Installation

```bash
pip install dj-polyglot
```

## Configuration

Add the following to your settings.py file:

```python
DJ_POLYGLOT_PROJECT = "your_project_name"
DJ_POLYGLOT_KEY = "your_api_key"
```


## Usage

```bash
python manage.py push_translations
python manage.py push_translations no_obsolete
python manage.py push_translations auto_translate
```

This will read your .po files and push the strings to the translation service.

```bash
python manage.py pull_translations
```

This will read the translations from the translation service and update your .po files.

## Development
# update version in setup.cfg and setup.py
python setup.py sdist bdist_wheel
twine upload dist/*



