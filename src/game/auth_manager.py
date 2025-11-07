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
            "score": 0,
            "coins": 0,
            "unlocked_weapons": [0],  # Vũ khí 0 (tay không) mở khóa mặc định
            "selected_weapon": 0,  # Vũ khí đang chọn
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
    
    def update_user_progress(self, score=None, coins=None):
        """Cập nhật tiến trình của user hiện tại (không còn dùng level và lives)."""
        if not self.current_user:
            return False
        
        user = self.find_user_by_username(self.current_user["username"])
        if not user:
            return False
        
        if score is not None:
            user["score"] = max(user["score"], score)  # Chỉ cập nhật nếu score cao hơn
        if coins is not None:
            user["coins"] = coins
        
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

    def add_score(self, points: int) -> bool:
        """Cộng thêm điểm vào tài khoản đang đăng nhập và lưu vào JSON.

        Trả về True nếu cập nhật thành công, False nếu chưa đăng nhập hoặc lỗi.
        """
        try:
            if not self.current_user:
                return False
            user = self.find_user_by_username(self.current_user["username"])
            if not user:
                return False
            # Bảo vệ kiểu dữ liệu
            current = int(user.get("score", 0) or 0)
            delta = int(points or 0)
            user["score"] = max(0, current + delta)
            self.current_user = user
            self.save_accounts()
            return True
        except Exception as _:
            return False

    def add_coins(self, amount: int) -> bool:
        """Cộng thêm xu vào tài khoản đang đăng nhập và lưu JSON ngay.

        Trả về True nếu thành công, False nếu chưa đăng nhập hoặc lỗi.
        """
        try:
            if not self.current_user:
                return False
            user = self.find_user_by_username(self.current_user["username"])
            if not user:
                return False
            current = int(user.get("coins", 0) or 0)
            delta = int(amount or 0)
            user["coins"] = max(0, current + delta)
            self.current_user = user
            self.save_accounts()
            return True
        except Exception:
            return False

    def unlock_weapon(self, weapon_id: int) -> tuple[bool, str]:
        """Mở khóa vũ khí bằng XU. Trả về (success, message)."""
        if not self.current_user:
            return False, "Chưa đăng nhập!"
        
        user = self.find_user_by_username(self.current_user["username"])
        if not user:
            return False, "Không tìm thấy tài khoản!"
        
        # Khởi tạo nếu chưa có
        if "unlocked_weapons" not in user:
            user["unlocked_weapons"] = [0]
        if "selected_weapon" not in user:
            user["selected_weapon"] = 0
        
        # Kiểm tra đã mở khóa chưa
        if weapon_id in user["unlocked_weapons"]:
            return False, "Vũ khí đã được mở khóa!"
        
        # Kiểm tra có đủ xu không
        coins = int(user.get("coins", 0) or 0)
        if coins < 1:
            return False, "Không đủ XU!"
        
        # Trừ xu và mở khóa
        user["coins"] = coins - 1
        user["unlocked_weapons"].append(weapon_id)
        self.current_user = user
        self.save_accounts()
        
        return True, f"Đã mở khóa vũ khí!"

    def select_weapon(self, weapon_id: int) -> bool:
        """Chọn vũ khí để sử dụng."""
        if not self.current_user:
            return False
        
        user = self.find_user_by_username(self.current_user["username"])
        if not user:
            return False
        
        if "unlocked_weapons" not in user:
            user["unlocked_weapons"] = [0]
        
        # Chỉ cho chọn vũ khí đã mở khóa
        if weapon_id not in user["unlocked_weapons"]:
            return False
        
        user["selected_weapon"] = weapon_id
        self.current_user = user
        self.save_accounts()
        return True

    def is_weapon_unlocked(self, weapon_id: int) -> bool:
        """Kiểm tra vũ khí đã được mở khóa chưa."""
        if not self.current_user:
            return weapon_id == 0  # Chỉ vũ khí 0 miễn phí
        
        user = self.find_user_by_username(self.current_user["username"])
        if not user:
            return weapon_id == 0
        
        if "unlocked_weapons" not in user:
            user["unlocked_weapons"] = [0]
            self.save_accounts()
        
        return weapon_id in user["unlocked_weapons"]

    def get_selected_weapon(self) -> int:
        """Lấy ID vũ khí đang được chọn."""
        if not self.current_user:
            return 0
        
        user = self.find_user_by_username(self.current_user["username"])
        if not user:
            return 0
        
        return user.get("selected_weapon", 0)