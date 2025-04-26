
# DJ POlyglot

**DJ POlyglot** is a Django library that provides python manage.py commands manage translations strings in .po files.
It will read your .po files, and push the strings to the translation service. It will also read the translations from the translation service and update your .po files.

---

## Installation

```bash
pip install dj-polyglot
```

It works together with the Django application UI: https://github.com/Thutmose3/dj-polyglot-app

"# dj_polyglot" 
# update version in setup.cfg and setup.py
python setup.py sdist bdist_wheel
twine upload dist/*



