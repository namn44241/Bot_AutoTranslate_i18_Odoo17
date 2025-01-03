from translation_replace_bot import TranslationReplaceBot

if __name__ == '__main__':
    # Street dẫn tới module của bạn
    MODULE_PATH = '../'  # Điều chỉnh đường dẫn nếu cần
    
    bot = TranslationReplaceBot(MODULE_PATH)
    bot.find_and_replace() 