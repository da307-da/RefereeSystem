# In a file named accounts/management/commands/sync_referees.py
from django.core.management.base import BaseCommand
from accounts.views import fetch_and_sync_referees_from_api  # Adjust import path

class Command(BaseCommand):
    help = 'Synchronize referees from the API'

    def handle(self, *args, **options):
        try:
            self.stdout.write("About to call sync function...")
            result = fetch_and_sync_referees_from_api()
            self.stdout.write(self.style.SUCCESS(result))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            # Print traceback for more detailed error info
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))