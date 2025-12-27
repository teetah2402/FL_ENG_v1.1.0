########################################################################
# FILE: patch_db.py
# Solusi buat benerin database yang "ketinggalan zaman" dibanding models.py
########################################################################
import sqlite3
import os

# Sesuaikan dengan path DB di Docker lu (biasanya /app/data/gateway.db)
# Di config.py lu pake path ini:
DB_PATH = "/app/data/gateway.db"

def run_patch():
    if not os.path.exists(DB_PATH):
        print(f"❌ File database gak ketemu di {DB_PATH}. Cek folder data lu!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🚀 Memulai patching database...")

    # List kolom yang harus ada biar gak "Error Semua"
    patches = [
        # Tabel Users
        ("users", "bio", "TEXT"),
        ("users", "avatar", "VARCHAR"),
        ("users", "preferences", "JSON DEFAULT '{}'"),
        # Tabel Registered Engines
        ("registered_engines", "internal_url", "VARCHAR"),
        # Tabel Episodes & Agent Sessions (Biar UI gak Error)
        ("episodes", "core_timeline_ptr", "VARCHAR"),
        ("agent_sessions", "finished_at", "TIMESTAMP")
    ]

    for table, column, col_type in patches:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type};")
            print(f"✅ Kolom '{column}' berhasil ditambahkan ke tabel '{table}'.")
        except sqlite3.OperationalError:
            print(f"ℹ️ Kolom '{column}' di tabel '{table}' udah ada, skipping.")

    conn.commit()
    conn.close()
    print("\n✨ Database udah sinkron sama models.py! Sekarang coba restart kontainernya.")

if __name__ == "__main__":
    run_patch()