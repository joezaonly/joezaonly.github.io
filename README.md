# ชั้นหนังสือแห่งความรู้ (Knowledge Shelf)

ห้องสมุดดิจิทัลส่วนตัว — คู่มือ AI, automation และธุรกิจออนไลน์ อ่านฟรีบนเว็บ

สร้างด้วยสคริปต์จาก `data/books.json` → `index.html` ผ่าน `templates/`

## โครงสร้าง

```
data/books.json         รายการหนังสือทั้งหมด (แหล่งความจริงหนึ่งเดียว)
books/<id>.html         หนังสือแต่ละเล่ม
scripts/build_shelf.py  สร้างหน้าหลัก (ใช้ --check เพื่อทดสอบ)
scripts/build_covers.py สร้างปก 600×900 อัตโนมัติ
templates/              แม่แบบหน้าเว็บ
tests/                  unit tests
AGENTS.md               กติกาสำหรับ AI ผู้ดูแล repo
```

## คำสั่งหลัก

```bash
python3 scripts/build_covers.py
python3 scripts/build_shelf.py
python3 scripts/build_shelf.py --check
python3 -m unittest discover -s tests -v
```
