import json
import os
from datetime import datetime
import hashlib

class AuthManager:
    def __init__(self, accounts_file="data/accounts.json"):
        # Đảm bảo path tuyệt đối từ thư mục src
        if not os.path.isabs(accounts_file):
            src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.accounts_file = os.path.join(src_dir, accounts_file)
        else:
            self.accounts_file = accounts_file
        self.current_user = None
        self.ensure_data_directory()
        self.load_accounts()
    
    def ensure_data_directory(self):
        """Tạo thư mục data nếu chưa tồn tại"""
        data_dir = os.path.dirname(self.accounts_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def load_accounts(self):
        """Tải danh sách tài khoản từ file JSON"""
        try:
            if os.path.exists(self.accounts_file):
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    self.accounts_data = json.load(f)
            else:
                # Tạo file mới nếu chưa tồn tại
                self.accounts_data = {"users": []}
                self.save_accounts()
        except Exception as e:
            print(f"Lỗi khi tải file tài khoản: {e}")
            self.accounts_data = {"users": []}
    
    def save_accounts(self):
        """Lưu danh sách tài khoản vào file JSON"""
        try:
            full_path = os.path.abspath(self.accounts_file)
            print(f"Đang lưu file tài khoản tại: {full_path}")
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts_data, f, indent=4, ensure_ascii=False)
            print(f"Lưu thành công! Số user: {len(self.accounts_data['users'])}")
        except Exception as e:
            print(f"Lỗi khi lưu file tài khoản: {e}")
    
    def hash_password(self, password):
        """Mã hóa mật khẩu bằng SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_next_user_id(self):
        """Lấy ID tiếp theo cho user mới"""
        if not self.accounts_data["users"]:
            return 1
        return max(user["id"] for user in self.accounts_data["users"]) + 1
    
    def register(self, username, password, email=""):
        """Đăng ký tài khoản mới"""
        # Kiểm tra username đã tồn tại chưa
        if self.find_user_by_username(username):
            return False, "Tên đăng nhập đã tồn tại!"
        
        # Kiểm tra password có đủ mạnh không
        if len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự!"
        
        # Tạo user mới
        new_user = {
            "id": self.get_next_user_id(),
            "username": username,
            "password": password,  # Trong thực tế nên mã hóa: self.hash_password(password)
            "email": email,
            "level": 1,
            "score": 0,
            "coins": 0,
            "lives": 3,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": ""
        }
        
        self.accounts_data["users"].append(new_user)
        self.save_accounts()
        return True, "Đăng ký thành công!"
    
    def login(self, username, password):
        """Đăng nhập"""
        user = self.find_user_by_username(username)
        if not user:
            return False, "Tên đăng nhập không tồn tại!"
        
        # Kiểm tra mật khẩu
        if user["password"] != password:  # Trong thực tế: self.hash_password(password)
            return False, "Mật khẩu không đúng!"
        
        # Cập nhật thời gian đăng nhập
        user["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_user = user
        self.save_accounts()
        
        return True, f"Chào mừng {username}!"
    
    def logout(self):
        """Đăng xuất"""
        self.current_user = None
    
    def find_user_by_username(self, username):
        """Tìm user theo username"""
        for user in self.accounts_data["users"]:
            if user["username"] == username:
                return user
        return None
    
    def update_user_progress(self, level=None, score=None, coins=None, lives=None):
        """Cập nhật tiến trình của user hiện tại"""
        if not self.current_user:
            return False
        
        user = self.find_user_by_username(self.current_user["username"])
        if not user:
            return False
        
        if level is not None:
            user["level"] = max(user["level"], level)  # Chỉ cập nhật nếu level cao hơn
        if score is not None:
            user["score"] = max(user["score"], score)  # Chỉ cập nhật nếu score cao hơn
        if coins is not None:
            user["coins"] = coins
        if lives is not None:
            user["lives"] = lives
        
        self.current_user = user
        self.save_accounts()
        return True
    
    def get_user_data(self):
        """Lấy thông tin user hiện tại"""
        return self.current_user
    
    def is_logged_in(self):
        """Kiểm tra đã đăng nhập chưa"""
        return self.current_user is not None
    
    def get_leaderboard(self, limit=10):
        """Lấy bảng xếp hạng theo điểm số"""
        users = sorted(self.accounts_data["users"], key=lambda x: x["score"], reverse=True)
        return users[:limit]