import logging
import os

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to extract all translatable strings and send them to an API endpoint."""

    help = "Extracts all translatable strings and makes an API request with them."

    def add_arguments(self, parser):
        """Add arguments to the command."""

        parser.add_argument(
            "no_obselete",
            type=str,
            nargs="?",
            default=None,
            help="Remove obselete translations from the API.",
        )

        parser.add_argument(
            "auto_translate",
            type=str,
            nargs="?",
            default=None,
            help="Remove obselete translations from the API.",
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
                logger.info(f"Processing file: {file}")
                if file.endswith(".po"):
                    po_file_path = os.path.join(root, file)
                    po_file = polib.pofile(po_file_path)

                    for entry in po_file:
                        if entry.msgid:
                            translatable_strings.append(
                                {"msgid": entry.msgid, "locale": os.path.basename(root), "context": entry.msgctxt}
                            )

        logger.info(f"Pusing {len(translatable_strings)} translatable strings to the API...")

        data = {
            "translations": translatable_strings, 
            "source_project": settings.DJ_POLYGLOT_PROJECT,
            "no_obselete": kwargs["no_obselete"] if kwargs["no_obselete"] else False,
            "auto_translate": kwargs["auto_translate"] if kwargs["auto_translate"] else False,
        }

        response = requests.post(
            url=f"https://dj-polyglot.com/api/push-translations/",
            json=data,
            headers={"Authorization": f"Token {settings.DJ_POLYGLOT_KEY}"},
        )

        if response.status_code == 200:
            logger.info("Successfully pushed translatable strings.")
        else:
            logger.error(f"Failed to push translatable strings. Status code: {response.status_code} - {response.json()}")
