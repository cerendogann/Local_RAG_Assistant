import sqlite3
import json
import math
from foundry_local_sdk import Configuration, FoundryLocalManager

DB_NAME = "knowledge_base.db"

# Matematiksel benzerliği ölçen fonksiyon (Kosinüs Benzerliği)
def get_cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)

def main():
    print("Sistem Hazırlanıyor...")
    FoundryLocalManager.initialize(Configuration(app_name="Local_RAG_Assistant"))
    manager = FoundryLocalManager.instance
    
    # 1. Çevirmen modeli yüklüyoruz
    embed_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embed_model.load()
    embed_client = embed_model.get_embedding_client()

    soru = "Kurye olmak için hangi evraklar gerekli?"
    print(f"\nSoru: {soru}")
    print("Soru veri tabanında aranıyor...")
    
    # Soruyu sayılara çevir
    response = embed_client.generate_embedding(soru)
    soru_vektoru = response.data[0].embedding if hasattr(response, 'data') else response.embedding

    # 2. Veri tabanında en benzer metni bul
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Hem metni (content) hem de sayıları (embedding) aynı anda istiyoruz
    cursor.execute("SELECT content, embedding FROM documents")
    
    en_iyi_skor = -1
    en_iyi_metin = ""

    for row in cursor.fetchall():
        content = row[0]
        db_vektor = json.loads(row[1])
        
        skor = get_cosine_similarity(soru_vektoru, db_vektor)
        if skor > en_iyi_skor:
            en_iyi_skor = skor
            en_iyi_metin = content
            
    conn.close()
    print("En alakalı belge bulundu. Yapay zeka cevap üretiyor...\n")
    
    # 3. Ana dil modelini (phi-3.5-mini) uyandırıyoruz
    llm = manager.catalog.get_model("phi-3.5-mini")
    llm.load()
    llm_client = llm.get_chat_client()
    
    # 4. Bulunan metni ve soruyu birleştirip yapay zekaya yönlendiriyoruz
    # 4. Bulunan metni ve soruyu birleştirip yapay zekaya yönlendiriyoruz
    sistem_mesaji = "Sen platformun yardımsever, cana yakın ama profesyonel asistanısın. Kullanıcılara doğal ve samimi bir dille cevap ver. Sadece sana verilen 'Bilgi' metnindeki gerçekleri kullan, bilgileri madde madde veya tam cümleler kurarak anlaşılır bir şekilde açıkla."
    kullanici_mesaji = f"Bilgi:\n{en_iyi_metin}\n\nSoru: {soru}"
    
    # Kütüphanenin içinden bulduğumuz o doğru komutu kullanıyoruz
    # Daktilo efekti (Streaming) ile kelime kelime ekrana yazdırma
    print("=" * 50)
    print("Asistan: ", end="", flush=True)
    
    chat_response = llm_client.complete_streaming_chat(
        messages=[
            {"role": "system", "content": sistem_mesaji},
            {"role": "user", "content": kullanici_mesaji}
        ]
    )
    
    # Gelen her kelimeyi bekletmeden anında ekrana basıyoruz
    for chunk in chat_response:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()