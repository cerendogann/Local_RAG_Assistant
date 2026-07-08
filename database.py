import sqlite3
import os

DB_NAME = "knowledge_base.db"
DATA_FOLDER = "data"

def setup_database():
    print("Veri tabanı şeması güncelleniyor (Eski tablo silinip yenisi kuruluyor)...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # İŞTE ÇÖZÜM: Önce eski tabloyu tamamen siliyoruz
    cursor.execute('DROP TABLE IF EXISTS documents')
    
    # Şimdi yeni sütunumuzla (embedding) birlikte tertemiz sıfırdan kuruyoruz
    cursor.execute('''
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            content TEXT,
            embedding TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Vektör destekli veri tabanı tablosu hazır!")

def insert_documents():
    print("\nDokümanlar temizleniyor ve yeniden yükleniyor...")
    if not os.path.exists(DATA_FOLDER):
        return
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM documents')
        
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".txt"):
            filepath = os.path.join(DATA_FOLDER, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                text = file.read()
                
                # Yeni dokümanı eklerken embedding kısmını şimdilik boş (None) bırakıyoruz.
                # Akşam eve gidince yerel modelimizle bu boşlukları sayılarla dolduracağız!
                cursor.execute('''
                    INSERT INTO documents (filename, content, embedding)
                    VALUES (?, ?, ?)
                ''', (filename, text, None))
                print(f"- {filename} tabloya eklendi (Vektör alanı ayrıldı).")
    
    conn.commit()
    conn.close()
    print("\nİşlem başarılı!")

if __name__ == "__main__":
    setup_database()
    insert_documents()