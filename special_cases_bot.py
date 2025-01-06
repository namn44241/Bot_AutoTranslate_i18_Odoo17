import re
from pathlib import Path
import logging
import ast
from lib2to3.fixer_base import BaseFix
from lib2to3.refactor import RefactoringTool

# Thiết lập logging
logging.basicConfig(
    filename='validation_message.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class ValidationMessageBot:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        
    def process_files(self):
        """Xử lý tất cả các file Python trong module"""
        python_files = self.module_path.rglob('*.py')
        
        print("\nBắt đầu xử lý các file Python...")
        for file_path in python_files:
            try:
                self._process_file(file_path)
            except Exception as e:
                logging.error(f'Lỗi khi xử lý file {file_path}: {str(e)}')
                
    def _process_file(self, file_path):
        """Xử lý một file Python"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Kiểm tra xem file có ValidationError không
        if 'ValidationError' not in content:
            return
            
        # Tìm các ValidationError message
        validation_pattern = r'raise\s+ValidationError\((.*?)\)'
        matches = re.finditer(validation_pattern, content, re.DOTALL)
        
        if not matches:
            return
            
        # Kiểm tra và thêm import _
        import_added = False
        new_content = content
        
        for match in matches:
            message = match.group(1)
            
            # Bỏ qua nếu đã có _() hoặc _lt()
            if '_(' in message or '_lt(' in message:
                continue
                
            # Thêm import _ nếu chưa có
            if not import_added:
                if 'from odoo import' in content:
                    if 'from odoo import _' not in content:
                        new_content = re.sub(
                            r'from odoo import (.*?)\n',
                            lambda m: f'from odoo import _, {m.group(1)}\n' if m.group(1) else 'from odoo import _\n',
                            new_content
                        )
                else:
                    new_content = 'from odoo import _\n' + new_content
                import_added = True
            
            # Xử lý message
            if message.startswith('f'):
                # f-string
                new_message = f'_(f{message[1:]})'
            else:
                # Normal string
                new_message = f'_({message})'
                
            # Thay thế trong content
            new_content = new_content.replace(
                f'raise ValidationError({message})',
                f'raise ValidationError({new_message})'
            )
            
        # Ghi file nếu có thay đổi
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Đã xử lý file: {file_path}")
            logging.info(f'Đã xử lý file: {file_path}') 