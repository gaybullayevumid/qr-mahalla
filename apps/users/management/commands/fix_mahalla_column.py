"""
Fix database schema - add mahalla_id column
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Add mahalla_id column to users_user table"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                # Check if column exists
                cursor.execute(
                    """
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users_user' AND column_name='mahalla_id'
                """
                )

                if cursor.fetchone():
                    self.stdout.write(
                        self.style.WARNING("mahalla_id column already exists")
                    )
                    return

                # Add column
                self.stdout.write("Adding mahalla_id column...")
                cursor.execute(
                    'ALTER TABLE "users_user" ADD COLUMN "mahalla_id" integer NULL'
                )

                # Create index
                self.stdout.write("Creating index...")
                cursor.execute(
                    'CREATE INDEX "users_user_mahalla_id_de604765" ON "users_user" ("mahalla_id")'
                )

                self.stdout.write(
                    self.style.SUCCESS("✅ Successfully added mahalla_id column!")
                )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
