# Super Mario Python Game

Một trò chơi Super Mario được viết bằng Python và Pygame.

## Tính năng

- Hệ thống đối thoại với NPC
- Giao diện tiếng Việt
- Hệ thống máu cho kẻ thù
- Hiển thị số damage khi tấn công
- Kẻ thù bị giết sẽ không tái sinh

## Cài đặt

1. Cài đặt Python 3.13 trở lên
2. Cài đặt các dependencies:
```bash
pip install -r requirements.txt
```

## Cách chạy

```bash
cd src
python main.py
```

## Điều khiển

- Phím mũi tên: Di chuyển
- Space: Nhảy / Tương tác hội thoại
- D/F: Lựa chọn trong hội thoại

## Cấu trúc project

```
src/
├── main.py              # File chính
├── assets/              # Tài nguyên game
│   ├── sounds/          # File âm thanh
│   ├── Character/       # Sprite nhân vật
│   ├── enemies/         # Sprite kẻ thù  
│   ├── fonts/           # Font chữ
│   └── ...
└── game/                # Module game
    ├── player.py        # Class Player
    ├── enemies.py       # Class Enemy
    ├── dialogue.py      # Hệ thống đối thoại
    └── ...
```

## Công nghệ sử dụng

- Python 3.13
- Pygame 2.6.1