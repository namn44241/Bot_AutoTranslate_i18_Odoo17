import os
import re
from pathlib import Path
import logging
from tqdm import tqdm
import time

# Thiết lập logging
logging.basicConfig(
    filename='translation_replace.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class TranslationReplaceBot:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.po_file = self.module_path / 'i18n' / 'vi_VN.po'
        self.exclude_files = {str(self.po_file)}
        # Chỉ xử lý các file text
        self.allowed_extensions = {'.py', '.xml', '.csv', '.txt', '.html', '.js', '.css'}
        
    def parse_po_file(self):
        """Đọc và parse file PO thành các phần tử dịch"""
        current_block = {'module': '', 'model_terms': '', 'msgid': '', 'msgstr': ''}
        translation_blocks = []
        
        with open(self.po_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines[141:]:  # Bắt đầu từ dòng 141
            line = line.strip()
            if line.startswith('#. module:'):
                if current_block['msgid'] and current_block['msgstr']:
                    translation_blocks.append(dict(current_block))
                current_block = {'module': line, 'model_terms': '', 'msgid': '', 'msgstr': ''}
            elif line.startswith('#: model'):
                current_block['model_terms'] = line
            elif line.startswith('msgid '):
                current_block['msgid'] = self._extract_message(line)
            elif line.startswith('msgstr '):
                current_block['msgstr'] = self._extract_message(line)
                
        if current_block['msgid'] and current_block['msgstr']:
            translation_blocks.append(dict(current_block))
                
        return translation_blocks

    def _extract_message(self, line):
        """Trích xuất nội dung message từ dòng msgid/msgstr"""
        match = re.match(r'msg(?:id|str) "(.*)"', line)
        return match.group(1) if match else ''

    def find_and_replace(self):
        """Tìm và thay thế các cụm từ trong toàn bộ module"""
        translation_blocks = self.parse_po_file()
        total_blocks = len(translation_blocks)
        
        print(f"\nTổng số phần tử dịch: {total_blocks}")
        
        with tqdm(total=total_blocks, desc="Process") as pbar:
            for idx, block in enumerate(translation_blocks, 1):
                msgstr = block['msgstr']
                msgid = block['msgid']
                
                if not msgstr or not msgid:
                    logging.warning(f'Bỏ qua block không đầy đủ: {block}')
                    pbar.update(1)
                    continue
                
                # Hiển thị thông tin chi tiết
                print(f"\nĐang xử lý phần tử {idx}/{total_blocks}")
                print(f"msgstr: {msgstr}")
                print(f"msgid: {msgid}")
                
                # Tìm tất cả file trong module (trừ file loại trừ)
                for file_path in self._get_module_files():
                    try:
                        self._replace_in_file(file_path, msgstr, msgid)
                    except Exception as e:
                        logging.error(f'Lỗi khi xử lý file {file_path}: {str(e)}')
                
                pbar.update(1)
                time.sleep(0.01)  # Để progress bar hiển thị mượt hơn

    def _get_module_files(self):
        """Lấy danh sách tất cả file trong module (trừ những file loại trừ)"""
        for root, _, files in os.walk(self.module_path):
            for file in files:
                file_path = Path(root) / file
                # Chỉ xử lý các file có phần mở rộng cho phép
                if (file_path.suffix in self.allowed_extensions and 
                    str(file_path) not in self.exclude_files and
                    not str(file_path).endswith('.bak')):
                    yield file_path

    def _replace_in_file(self, file_path, search_text, replace_text):
        """Thay thế text trong một file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Tìm kiếm chính xác cụm từ trong dấu nháy đơn hoặc nháy kép
            pattern = r'["\']' + re.escape(search_text) + r'["\']'
            
            # Pattern cho text trong thẻ XML
            xml_pattern = r'>(' + re.escape(search_text) + r')<'
            
            # Pattern cho text trong thẻ bold 
            bold_pattern = r'<bold>\s*' + re.escape(search_text) + r'\s*</bold>'
            
            if re.search(pattern, content) or re.search(xml_pattern, content) or re.search(bold_pattern, content):
                # Xử lý text trong dấu nháy (giữ nguyên logic cũ)
                if "'" in replace_text:
                    new_content = re.sub(r'"' + re.escape(search_text) + r'"', 
                                      f'"{replace_text}"', content)
                    new_content = re.sub(r"'" + re.escape(search_text) + r"'",
                                      f'"{replace_text}"', new_content)
                else:
                    new_content = re.sub(r'"' + re.escape(search_text) + r'"', 
                                      f'"{replace_text}"', content)
                    new_content = re.sub(r"'" + re.escape(search_text) + r"'",
                                      f"'{replace_text}'", new_content)
                
                # Xử lý text trong thẻ XML
                new_content = re.sub(xml_pattern, f'>{replace_text}<', new_content)
                
                # Xử lý text trong thẻ bold
                new_content = re.sub(bold_pattern, f'<bold>{replace_text}</bold>', new_content)
                
                # Ghi file mới
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                logging.info(f'Đã thay thế "{search_text}" -> "{replace_text}" trong {file_path}')
                print(f"Đã thay thế trong file: {file_path}")
                
        except Exception as e:
            logging.error(f'Lỗi khi xử lý file {file_path}: {str(e)}')