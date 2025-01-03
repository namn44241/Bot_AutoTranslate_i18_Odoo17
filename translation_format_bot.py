import re
from pathlib import Path
import logging
from tqdm import tqdm
from googletrans import Translator
import time
from langdetect import detect

# Thiết lập logging
logging.basicConfig(
    filename='translation_format.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class TranslationFormatBot:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.po_file = self.module_path / 'i18n' / 'vi_VN.po'
        self.translator = Translator()
        
    def format_and_translate(self):
        """Định dạng lại và dịch file PO"""
        # Đọc toàn bộ file
        with open(self.po_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Phân tích thành các block dịch
        blocks = []
        current_block = []
        
        for line in lines:
            if line.startswith('#. module:'):
                if current_block:
                    blocks.append(current_block)
                current_block = [line]
            else:
                current_block.append(line)
                
        if current_block:
            blocks.append(current_block)
            
        # Xử lý từng block
        print(f"\nTổng số phần tử dịch: {len(blocks)}")
        
        with tqdm(total=len(blocks), desc="Đang xử lý") as pbar:
            for idx, block in enumerate(blocks, 1):
                try:
                    self._process_block(block)
                except Exception as e:
                    logging.error(f'Lỗi khi xử lý block {idx}: {str(e)}')
                pbar.update(1)
                time.sleep(0.01)
                
        # Ghi lại file
        with open(self.po_file, 'w', encoding='utf-8') as f:
            for block in blocks:
                f.writelines(block)
                
    def _process_block(self, block):
        """Xử lý một block dịch"""
        msgid = None
        msgstr = None
        msgid_line_idx = None
        msgstr_line_idx = None
        
        # Tìm vị trí và nội dung msgid và msgstr
        for i, line in enumerate(block):
            if line.startswith('msgid '):
                msgid = self._extract_message(line)
                msgid_line_idx = i
            elif line.startswith('msgstr '):
                msgstr = self._extract_message(line)
                msgstr_line_idx = i
                
        if msgid is None or msgid == '':
            return
            
        try:
            # Trường hợp 1: msgid là tiếng Việt -> dịch sang Anh
            if self._is_vietnamese(msgid):
                translation = self._translate_to_english(msgid)
                if translation:
                    # Chuyển msgid cũ xuống msgstr
                    block[msgstr_line_idx] = f'msgstr "{msgid}"\n'
                    # Đặt bản dịch làm msgid mới
                    block[msgid_line_idx] = f'msgid "{translation}"\n'
                    print(f"\nĐã dịch VI->EN: {msgid} -> {translation}")
                    logging.info(f'Đã dịch VI->EN: {msgid} -> {translation}')
            
            # Trường hợp 2: msgid là tiếng Anh và msgstr rỗng -> dịch sang Việt
            elif msgstr == '' and self._is_english(msgid):
                translation = self._translate_to_vietnamese(msgid)
                if translation:
                    # Chỉ cập nhật msgstr
                    block[msgstr_line_idx] = f'msgstr "{translation}"\n'
                    print(f"\nĐã dịch EN->VI: {msgid} -> {translation}")
                    logging.info(f'Đã dịch EN->VI: {msgid} -> {translation}')
                
        except Exception as e:
            logging.error(f'Lỗi khi xử lý block với msgid "{msgid}": {str(e)}')

    def _extract_message(self, line):
        """Trích xuất nội dung message từ dòng msgid/msgstr"""
        match = re.match(r'msg(?:id|str) "(.*)"', line)
        return match.group(1) if match else ''
        
    def _is_vietnamese(self, text):
        """Kiểm tra xem text có phải tiếng Việt không"""
        try:
            return detect(text) == 'vi'
        except:
            return False
            
    def _is_english(self, text):
        """Kiểm tra xem text có phải tiếng Anh không"""
        try:
            return detect(text) == 'en'
        except:
            return False

    def _translate_to_english(self, text):
        """Dịch text sang tiếng Anh, giữ nguyên format đặc biệt"""
        try:
            # Giữ lại các ký tự đặc biệt và số
            special_format = []
            pattern = r'(\d+/\d+\.|\d+\.)'
            
            # Tách và lưu format đặc biệt
            parts = re.split(pattern, text)
            for i, part in enumerate(parts):
                if re.match(pattern, part):
                    special_format.append((i, part))
                    
            # Dịch phần text
            translation = self.translator.translate(text, src='vi', dest='en').text
            
            # Khôi phục format đặc biệt
            for idx, format_str in special_format:
                parts = translation.split()
                if idx < len(parts):
                    parts[idx] = format_str
                translation = ' '.join(parts)
                
            return translation
            
        except Exception as e:
            logging.error(f'Lỗi khi dịch "{text}": {str(e)}')
            return None 

    def _translate_to_vietnamese(self, text):
        """Dịch text sang tiếng Việt, giữ nguyên format đặc biệt"""
        try:
            # Giữ lại các ký tự đặc biệt và số
            special_format = []
            pattern = r'(\d+/\d+\.|\d+\.)'
            
            # Tách và lưu format đặc biệt
            parts = re.split(pattern, text)
            for i, part in enumerate(parts):
                if re.match(pattern, part):
                    special_format.append((i, part))
                    
            # Dịch phần text
            translation = self.translator.translate(text, src='en', dest='vi').text
            
            # Khôi phục format đặc biệt
            for idx, format_str in special_format:
                parts = translation.split()
                if idx < len(parts):
                    parts[idx] = format_str
                translation = ' '.join(parts)
                
            return translation
            
        except Exception as e:
            logging.error(f'Lỗi khi dịch "{text}": {str(e)}')
            return None 