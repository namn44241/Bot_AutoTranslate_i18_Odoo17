import os
import re

def check_and_add_import(content):
    """Kiểm tra và thêm import _ nếu chưa có"""
    if "from odoo import" in content:
        if ", _" not in content and "import _" not in content:
            content = content.replace("from odoo import", "from odoo import _, ")
    return content

def process_name_translations(content):
    """Xử lý các cụm 'name': 'text' thành 'name': _('text')"""
    patterns = [
        r"'name':\s*'([^']+)'",  # 'name': 'text'
        r'"name":\s*"([^"]+)"',  # "name": "text"
        r"'name':\s*\"([^\"]+)\"",  # 'name': "text"
        r'"name":\s*\'([^\']+)\'',  # "name": 'text'
    ]
    
    for pattern in patterns:
        content = re.sub(pattern, lambda m: f"'name': _('{m.group(1)}')", content)
    
    return content

def process_file(file_path):
    """Xử lý một file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        if "'name':" in content or '"name":' in content:
            # Thêm import _ nếu cần
            content = check_and_add_import(content)
            # Xử lý các cụm name
            content = process_name_translations(content)
            
            # Ghi lại file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Processed: {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def main():
    """Hàm chính để quét và xử lý các file"""
    # Đường dẫn tới thư mục module
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Quét tất cả các file .py trong module
    for root, dirs, files in os.walk(module_path):
        for file in files:
            # Bỏ qua __manifest__.py và các file trong thư mục i18n
            if (file.endswith('.py') and 
                file != '__manifest__.py' and 
                'i18n' not in root):
                file_path = os.path.join(root, file)
                process_file(file_path)

if __name__ == "__main__":
    main() 