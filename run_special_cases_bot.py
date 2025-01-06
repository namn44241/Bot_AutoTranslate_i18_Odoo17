from special_cases_bot import ValidationMessageBot

if __name__ == '__main__':
    # Đường dẫn tới module
    MODULE_PATH = '../'
    
    bot = ValidationMessageBot(MODULE_PATH)
    bot.process_files() 