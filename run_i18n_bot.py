# quan_ly_van_ban/tools/run_i18n_bot.py

from pathlib import Path
from i18n_log_van_ban_bot import I18nLogVanBanBot

def main():
    # Lấy đường dẫn tới module quan_ly_van_ban
    module_path = Path(__file__).parent.parent
    
    # Khởi tạo và chạy bot
    bot = I18nLogVanBanBot(module_path)
    bot.process_file()

if __name__ == "__main__":
    main()