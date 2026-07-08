import sqlite3
import json # Sayıları metne çevirip kaydetmek için lazım
from foundry_local_sdk import Configuration, FoundryLocalManager

DB_NAME = "knowledge_base.db"

def main():
    print("Kelimeleri Sayılara Çevirme (Embedding) İşlemi Başlıyor...")
    
    # 1. Yapay Zeka Sistemini Başlatıyoruz
    FoundryLocalManager.initialize(Configuration(app_name="Local_RAG_Assistant"))
    manager = FoundryLocalManager.instance
    
    # 2. Çevirmen Modeli İndirip Hazırlıyoruz
    print("Çevirmen model aranıyor (İlk seferde yaklaşık 600 MB inebilir)...")
    embed_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    
    # İndirme yüzdesini ekranda görmek için
    embed_model.download(lambda p: print(f"\rİndirme: %{p:.0f}", end="", flush=True))
    
    print("\nModel hafızaya alınıyor...")
    embed_model.load()
    client = embed_model.get_embedding_client()
    
    # 3. Veri tabanına (SQLite) bağlanıyoruz
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 4. Sadece vektörü (embedding'i) BOŞ olan dokümanları buluyoruz
    cursor.execute("SELECT id, filename, content FROM documents WHERE embedding IS NULL")
    rows = cursor.fetchall()
    
    if not rows:
        print("\nTüm dokümanların zaten vektörü var, işlem yapmaya gerek yok!")
        return
        
    print(f"\nToplam {len(rows)} adet doküman sayılara çevrilecek...")
    
    # 5. Bulduğumuz her bir dokümanı sırayla işliyoruz
    for row in rows:
        doc_id = row[0]
        filename = row[1]
        content = row[2]
        print(f"- '{filename}' işleniyor...")
        
        # Metni modele gönderip sayısal vektörünü istiyoruz
        response = client.generate_embedding(content)
        
        # Modelden gelen yüzlerce sayılık listeyi alıyoruz
        vector_data = response.data[0].embedding
        
        # Bu sayı listesini SQLite'a kaydedebilmek için JSON formatına çeviriyoruz
        vector_text = json.dumps(vector_data)
        
        # Veri tabanındaki o satırı güncelliyor ve boş hücreyi dolduruyoruz
        cursor.execute("UPDATE documents SET embedding = ? WHERE id = ?", (vector_text, doc_id))
        
    # Değişiklikleri kaydedip veri tabanını kapatıyoruz
    conn.commit()
    conn.close()
    print("\nHarika! Tüm metinler başarıyla vektöre çevrilip veri tabanına eklendi.")

if __name__ == "__main__":
    main()