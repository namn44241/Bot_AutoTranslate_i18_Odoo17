import re
from pathlib import Path
import logging

logging.basicConfig(
    filename='i18n_log_van_ban.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class I18nLogVanBanBot:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.log_van_ban_path = self.module_path / 'models' / 'action_van_ban_den' / 'log_van_ban.py'
        
        # Các pattern cần xử lý
        self.html_patterns = [
            r'<b>(.*?)</b>',  # Text trong thẻ b
            r'<span>(.*?)</span>',  # Text trong thẻ span
            r'<p class="text-danger">(.*?)</p>'  # Text trong p có class
        ]
        
        self.notify_patterns = [
            r"title='(.*?)'",  # Text trong title dấu nháy đơn
            r'title="(.*?)"',  # Text trong title dấu nháy kép
            r"message='(.*?)'",  # Text trong message
            r'message="(.*?)"'  # Text trong message
        ]
        
        self.markup_patterns = [
            r'<span>(.*?):</span>',  # Text trong span có dấu :
            r'<b>(.*?):</b>'  # Text trong b có dấu :
        ]

    def process_file(self):
        """Xử lý file log_van_ban.py"""
        try:
            with open(self.log_van_ban_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Thêm import _ nếu chưa có
            content = self._add_odoo_import(content)

            # Xử lý các pattern
            content = self._process_direct_text(content)
            content = self._process_notify_text(content)
            content = self._process_markup_text(content)

            # Ghi lại file
            with open(self.log_van_ban_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logging.info('Đã xử lý xong file log_van_ban.py')
            print('Đã xử lý xong file log_van_ban.py')

        except Exception as e:
            logging.error(f'Lỗi khi xử lý file: {str(e)}')
            print(f'Lỗi khi xử lý file: {str(e)}')

    def _add_odoo_import(self, content):
        """Thêm import _ từ odoo nếu chưa có"""
        if 'from odoo import _' not in content:
            # Tìm dòng import từ odoo
            if 'from odoo import' in content:
                content = re.sub(
                    r'from odoo import (.*?)\n',
                    lambda m: f'from odoo import _, {m.group(1)}\n' if m.group(1) else 'from odoo import _\n',
                    content
                )
            else:
                # Thêm vào đầu file sau các comment
                content = 'from odoo import _\n' + content
            logging.info('Đã thêm import _ từ odoo')
        return content

    def _process_direct_text(self, content):
        """Xử lý text trực tiếp trong HTML tags"""
        for pattern in self.html_patterns:
            content = re.sub(
                pattern,
                lambda m: m.group(0).replace(m.group(1), f'{{_("{m.group(1)}")}}') 
                if self._is_vietnamese(m.group(1)) else m.group(0),
                content
            )
        return content

    def _process_notify_text(self, content):
        """Xử lý text trong notify"""
        for pattern in self.notify_patterns:
            content = re.sub(
                pattern,
                lambda m: m.group(0).replace(m.group(1), f'_("{m.group(1)}")') 
                if self._is_vietnamese(m.group(1)) else m.group(0),
                content
            )
        return content

    def _process_markup_text(self, content):
        """Xử lý text trong Markup"""
        # Tách riêng phần text tĩnh và phần động
        for pattern in self.markup_patterns:
            content = re.sub(
                pattern,
                lambda m: self._split_dynamic_content(m.group(1)),
                content
            )
        return content

    def _split_dynamic_content(self, text):
        """Tách phần text tĩnh và phần động"""
        # Tìm các biến động trong text (nằm trong {})
        dynamic_parts = re.findall(r'{.*?}', text)
        if dynamic_parts:
            # Tách text thành các phần
            parts = re.split(r'{.*?}', text)
            result = []
            # Xử lý từng phần text tĩnh
            for i, part in enumerate(parts):
                if self._is_vietnamese(part):
                    result.append(f'{{_("{part}")}}')
                else:
                    result.append(part)
                # Thêm lại phần động nếu còn
                if i < len(dynamic_parts):
                    result.append(dynamic_parts[i])
            return ''.join(result)
        else:
            # Nếu không có phần động, xử lý cả text
            return f'{{_("{text}")}}' if self._is_vietnamese(text) else text

    def _is_vietnamese(self, text):
        """Kiểm tra xem text có phải tiếng Việt không"""
        vietnamese_chars = set('áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ')
        text_lower = text.lower()
        return any(char in vietnamese_chars for char in text_lower)
