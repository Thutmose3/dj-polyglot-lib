import os

import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command to extract all translatable strings and send them to an API endpoint."""

    help = __doc__.strip()

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-obsolete",
            action="store_true",
            help="Tell the API to delete obsolete translations",
        )
        parser.add_argument(
            "--auto-translate",
            action="store_true",
            help="Request machine-translation of new strings",
        )

    def handle(self, *args, **kwargs):
        """Handle the command."""
        import polib
        # Ensure that DJ_POLYGLOT_PROJECT and DJ_POLYGLOT_KEY are available
        if not getattr(settings, "DJ_POLYGLOT_PROJECT", None):
            raise ValueError("DJ_POLYGLOT_PROJECT is not set in the settings.")
        
        if not getattr(settings, "DJ_POLYGLOT_KEY", None):
            raise ValueError("DJ_POLYGLOT_KEY is not set in the settings.")

        translatable_strings = []

        locale_path = os.path.join(settings.BASE_DIR, "locale")

        # Iterate over all .po files in the locale directory
        for root, dirs, files in os.walk(locale_path):
            for file in files:
                self.stdout.write(f"Processing file: {file} in {root}")
                if file.endswith(".po"):
                    po_file_path = os.path.join(root, file)
                    po_file = polib.pofile(po_file_path)

                    for entry in po_file:
                        if entry.msgid:
                            translatable_strings.append(
                                {"msgid": entry.msgid, "locale": os.path.basename(root), "context": entry.msgctxt}
                            )

        self.stdout.write(
            self.style.NOTICE(f"Pusing {len(translatable_strings)} translatable strings to the API...")
        )

        data = {
            "translations": translatable_strings, 
            "source_project": settings.DJ_POLYGLOT_PROJECT,
            "no_obselete": kwargs.get("no_obsolete", False),
            "auto_translate": kwargs.get("auto_translate", False),
        }

        response = requests.post(
            url=f"https://dj-polyglot.com/api/push-translations/",
            json=data,
            headers={"Authorization": f"Token {settings.DJ_POLYGLOT_KEY}"},
        )

        if response.status_code == 200:
            self.stdout.write("Successfully pushed translatable strings.")
        else:
            self.stdout.write(f"Failed to push translatable strings")
            self.stdout.write(f"Status code: {response.status_code} - {response.headers} - {response.text}")
