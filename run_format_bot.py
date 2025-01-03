from translation_format_bot import TranslationFormatBot

if __name__ == '__main__':
    # Đường dẫn tới module
    MODULE_PATH = '../'
    
    bot = TranslationFormatBot(MODULE_PATH)
    bot.format_and_translate() 