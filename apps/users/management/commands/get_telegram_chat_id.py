import requests
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Get Telegram chat ID for SMS notifications"

    def handle(self, *args, **options):
        bot_token = settings.TELEGRAM_BOT_TOKEN

        self.stdout.write(self.style.WARNING("\n📱 Getting Telegram Chat ID...\n"))

        # Get bot info
        try:
            bot_info_url = f"https://api.telegram.org/bot{bot_token}/getMe"
            bot_response = requests.get(bot_info_url, timeout=5)

            if bot_response.status_code == 200:
                bot_data = bot_response.json()
                if bot_data.get("ok"):
                    bot_username = bot_data["result"]["username"]
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Bot connected: @{bot_username}")
                    )
                    self.stdout.write(f"\n🔗 Bot link: https://t.me/{bot_username}\n")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error getting bot info: {e}"))

        # Get updates
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if data.get("ok") and data.get("result"):
                    updates = data["result"]

                    if updates:
                        latest_update = updates[-1]
                        chat_id = latest_update["message"]["chat"]["id"]
                        from_user = latest_update["message"]["from"]

                        self.stdout.write(
                            self.style.SUCCESS(f"\n✅ Chat ID found: {chat_id}")
                        )
                        self.stdout.write(
                            f"👤 User: {from_user.get('first_name', '')} {from_user.get('last_name', '')}"
                        )
                        self.stdout.write(
                            f"📱 Username: @{from_user.get('username', 'N/A')}\n"
                        )

                        self.stdout.write(
                            self.style.WARNING(f"\n📝 Add this to settings.py:\n")
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'TELEGRAM_CHAT_ID = "{chat_id}"\n')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                "\n⚠️ No messages found. Please:\n"
                                "1. Open your bot in Telegram\n"
                                "2. Send /start command\n"
                                "3. Run this command again\n"
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ API Error: {data.get('description')}")
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ HTTP Error: {response.status_code}\n{response.text}"
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
