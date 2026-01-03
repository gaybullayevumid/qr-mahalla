"""
Delete all users except those with phone numbers starting with 085, 620, or 625.
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User


def delete_users_except_specific():
    """Delete users except those with phone numbers starting with 085, 620, 625."""

    # Get all users
    all_users = User.objects.all()
    total_count = all_users.count()

    # Users to keep (containing 085, 620, or 625)
    users_to_keep = User.objects.filter(
        models.Q(phone__contains="085")
        | models.Q(phone__contains="620")
        | models.Q(phone__contains="625")
    )

    keep_count = users_to_keep.count()
    delete_count = total_count - keep_count

    print("=" * 60)
    print("DELETE USERS (Keep only 085, 620, 625)")
    print("=" * 60)

    print(f"\n📊 Current status:")
    print(f"   Total users: {total_count}")
    print(f"\n✅ Users to KEEP (085, 620, 625):")
    for user in users_to_keep:
        print(f"   - {user.phone} ({user.role})")

    print(f"\n❌ Users to DELETE: {delete_count}")

    if delete_count == 0:
        print(f"\n✓ No users to delete.")
        return

    # Show users to be deleted
    users_to_delete = all_users.exclude(
        models.Q(phone__contains="085")
        | models.Q(phone__contains="620")
        | models.Q(phone__contains="625")
    )

    print(f"\n   Users to be deleted:")
    for user in users_to_delete:
        print(f"   - {user.phone} ({user.role})")

    confirm = input(f"\n⚠️  Delete {delete_count} users? (yes/no): ")

    if confirm.lower() in ["yes", "y", "ha"]:
        # Delete users
        deleted = users_to_delete.delete()

        remaining = User.objects.count()

        print(f"\n" + "=" * 60)
        print(f"✅ Successfully deleted {deleted[0]} users!")
        print(f"=" * 60)
        print(f"Remaining users: {remaining}")
        print(f"\nRemaining users:")
        for user in User.objects.all():
            print(f"   - {user.phone} ({user.role})")
    else:
        print("\n❌ Deletion cancelled.")


if __name__ == "__main__":
    from django.db import models

    delete_users_except_specific()
