import logging
import os
import time

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """Extracts all translatable strings and makes an API request with them."""

    help = "Extracts all translatable strings and makes an API request with them."

    def handle(self, *args, **kwargs):
        """Extracts all translatable strings and makes an API request with them."""
        import polib

        logger.info("Pulling translations...")
        start_time = time.time()
        source_project = settings.DJ_POLYGLOT_PROJECT

        if not getattr(settings, "DJ_POLYGLOT_PROJECT", None):
            raise ValueError("DJ_POLYGLOT_PROJECT is not set in the settings.")

        source_projects = [source_project]

        if getattr(settings, "DJ_POLYGLOT_PROJECT_EXTRA", None):
            source_projects += settings.DJ_POLYGLOT_PROJECT_EXTRA

        translations = []

        for source_project in source_projects:
            response = requests.post(
                "https://dj-polyglot.com/api/pull-translations/",
                data={"source_project": source_project},
                headers={"Authorization": f"Token {settings.DJ_POLYGLOT_KEY}"},
            )

            if response.status_code != 200:
                logger.info(f"Failed to receive translatable strings. Status code: {response.status_code}, {response.content}. Time: {time.time() - start_time:.2f} seconds.")
                return
        
            translations += response.json().get("translations", [])

        logger.info(f"Successfully received {len(translations)} translations from {source_project}")

        logger.info(
            f"Successfully received {len(translations)} translatable strings in {time.time() - start_time:.2f} seconds."
        )
        
        # Process translations for each locale
        logger.info("Adding translations to the PO files...")

        locale_mapping = {"zh-hans": "zh_HAns", "zh-hant": "zh_HAnt", "pt-pt": "pt_PT"}

        for locale in [code for code, _ in settings.LANGUAGES]:
            if locale == "en":
                continue

            # Map locale to specific format if necessary
            locale = locale_mapping.get(locale, locale)

            logger.info(f"Processing locale: {locale}")
            po_file_path = os.path.join(settings.BASE_DIR, "locale", locale, "LC_MESSAGES", "django.po")

            if not os.path.exists(po_file_path):
                logger.info(self.style.ERROR(f"File {po_file_path} not found"))
                continue

            # Open the PO file
            po_file = polib.pofile(po_file_path)

            # Update translations in PO file
            locale_translations = [t for t in translations if t.get("locale") == locale.lower()]
            for translation in locale_translations:
                msgid = translation.get("msgid")
                msgstr = translation.get("msgstr")
                entry = po_file.find(msgid)

                if entry:
                    entry.msgstr = msgstr
                else:
                    po_file.append(polib.POEntry(msgid=msgid, msgstr=msgstr))

            # Remove obsolete entries
            for entry in po_file.obsolete_entries():
                po_file.remove(entry)

            # Save the PO file
            po_file.save(po_file_path)

        logger.info("Translations successfully added to the PO files.")
        logger.info(f"Pulling translations completed in {time.time() - start_time:.2f} seconds.")
