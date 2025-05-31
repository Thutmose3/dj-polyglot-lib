import os
import time
import polib

import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Extracts all translatable strings and makes an API request with them."

    def handle(self, *args, **kwargs):

        self.stdout.write("Pulling translations...")
        start_time = time.time()

        if not getattr(settings, "DJ_POLYGLOT_PROJECT", None):
            raise ValueError("DJ_POLYGLOT_PROJECT is not set in the settings.")
        
        if not getattr(settings, "DJ_POLYGLOT_KEY", None):
            raise ValueError("DJ_POLYGLOT_KEY is not set in the settings.")

        source_project = settings.DJ_POLYGLOT_PROJECT

        translations = []

        response = requests.post(
            "https://dj-polyglot.com/api/pull-translations/",
            data={"source_project": source_project},
            headers={"Authorization": f"Token {settings.DJ_POLYGLOT_KEY}"},
        )

        if response.status_code != 200:
            self.stdout.write(f"Failed to receive translatable strings. Status code: {response.status_code}, {response.content}. Time: {time.time() - start_time:.2f} seconds.")
            return
    
        translations += response.json()["translations"]

        self.stdout.write(f"Successfully received {len(translations)} translations from {source_project}")

        self.stdout.write(
            f"Successfully received {len(translations)} translatable strings in {time.time() - start_time:.2f} seconds."
        )
        
        # Process translations for each locale
        self.stdout.write("Adding translations to the PO files...")

        locale_mapping = {"zh-hans": "zh_HAns", "zh-hant": "zh_HAnt", "pt-pt": "pt_PT"}

        for locale in [code for code, _ in settings.LANGUAGES]:
            if locale == "en":
                continue

            # Map locale to specific format if necessary
            locale = locale_mapping.get(locale, locale)

            self.stdout.write(f"Processing locale: {locale}")
            po_file_path = os.path.join(settings.BASE_DIR, "locale", locale, "LC_MESSAGES", "django.po")

            if not os.path.exists(po_file_path):
                self.stdout.write(self.style.ERROR(f"File {po_file_path} not found"))
                continue

            # Open the PO file
            po_file = polib.pofile(po_file_path)

            # Update translations in PO file
            locale_translations = [t for t in translations if t.get("locale") == locale.lower()]
            for translation in locale_translations:
                msgid = translation.get("msgid")
                msgstr = translation.get("msgstr")
                msgctxt = translation.get("msgctxt", None)
                if msgctxt:
                    entry = po_file.find(msgid, msgctxt=msgctxt)
                else:
                    entry = po_file.find(msgid)

                if entry:
                    entry.msgstr = msgstr
                else:
                    po_file.append(polib.POEntry(msgid=msgid, msgstr=msgstr, msgctxt=msgctxt))

            # Remove obsolete entries
            for entry in po_file.obsolete_entries():
                po_file.remove(entry)

            # Save the PO file
            po_file.save(po_file_path)

        self.stdout.write("Translations successfully added to the PO files.")
        self.stdout.write(f"Pulling translations completed in {time.time() - start_time:.2f} seconds.")
