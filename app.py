import streamlit as st
import sqlite3
import json
import math
import os
from foundry_local_sdk import Configuration, FoundryLocalManager

DB_NAME = "knowledge_base.db"

# --- 1. SAYFA AYARLARI VE GÖRÜNÜM ---
st.set_page_config(page_title="Akıllı Doküman Asistanı", page_icon="🧠", layout="wide")

# Renk zorlamaları çıkarıldı, sadece şekil/animasyon makyajı bırakıldı
st.markdown("""
<style>
    /* Buton animasyonları (Temaya uyumlu) */
    div.stButton > button:first-child {
        border-radius: 8px;
        transition: all 0.3s ease;
        font-weight: 600;
        border: 1px solid #3498DB;
    }
    div.stButton > button:first-child:hover {
        box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3);
        transform: translateY(-2px);
        border: 1px solid #3498DB;
    }
    
    /* Özel başlık tasarımı (Renkler temaya göre otomatik değişecek) */
    .custom-title {
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        padding-bottom: 15px;
        margin-bottom: 30px;
        border-bottom: 3px solid #3498DB;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='custom-title'>🧠 Akıllı Doküman Analiz Asistanı</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-size: 1.1em;'>Yüklediğiniz metin dosyalarını derinlemesine analiz eden, yerel ve güvenli yapay zeka asistanınız.</p>", unsafe_allow_html=True)

with st.expander("ℹ️ Sistem Nasıl Çalışır? (Tıklayıp inceleyebilirsiniz)"):
    st.markdown("""
    1. **Dosya Yükleme:** Sol panelden `.txt` formatındaki belgelerinizi yükleyin.
    2. **Veri İşleme:** Sistem bu metinleri paragraflara böler ve yapay zekanın anlayabileceği matematiksel vektörlere dönüştürür.
    3. **Sorgulama:** Aşağıdaki sohbet kutusundan belgelerinizle ilgili istediğiniz soruyu sorun, anında kaynak göstererek cevaplasın!
    """)

# --- 2. YAPAY ZEKA MOTORU ---
@st.cache_resource
def kaynaklari_yukle():
    try:
        FoundryLocalManager.initialize(Configuration(app_name="Local_RAG_Assistant"))
    except: pass
    manager = FoundryLocalManager.instance
    embed_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embed_model.load()
    llm = manager.catalog.get_model("phi-3.5-mini")
    llm.load()
    return embed_model.get_embedding_client(), llm.get_chat_client()

embed_client, llm_client = kaynaklari_yukle()

def db_kur():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, content TEXT, embedding TEXT)")
    conn.commit()
    conn.close()

db_kur()

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# --- 3. SOL PANEL (SIDEBAR) ---
with st.sidebar:
    st.header("📁 Bilgi Tabanı Yönetimi")
    st.info("Aşağıdan analiz edilecek metinleri yükleyebilirsiniz.")
    
    uploaded_files = st.file_uploader(
        "Metin dosyaları (.txt) seçin", 
        type=["txt"], 
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}"
    )
    
    if st.button("🚀 Seçili Belgeleri İşle", use_container_width=True):
        if uploaded_files:
            with st.status("⏳ Belgeler sisteme işleniyor...", expanded=True) as status:
                st.write("Veritabanı bağlantısı kuruluyor...")
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                
                for f in uploaded_files:
                    st.write(f"📄 **{f.name}** okunuyor ve yapay zeka diline çevriliyor...")
                    text = f.getvalue().decode("utf-8")
                    chunks = [p.strip() for p in text.split("\n\n") if p.strip()]
                    
                    for p in chunks:
                        vec = embed_client.generate_embedding(p)
                        v = vec.data[0].embedding if hasattr(vec, 'data') else vec.embedding
                        cursor.execute("INSERT INTO documents (filename, content, embedding) VALUES (?, ?, ?)", (f.name, p, json.dumps(v)))
                
                conn.commit()
                conn.close()
                st.session_state.uploader_key += 1
                
                status.update(label="Tüm belgeler başarıyla hafızaya alındı! ✅", state="complete", expanded=False)
            st.rerun()

    st.divider()
    
    st.subheader("📚 Sistemdeki Dosyalar")
    conn = sqlite3.connect(DB_NAME)
    files = conn.execute("SELECT DISTINCT filename FROM documents").fetchall()
    conn.close()
    
    if files:
        for f in files: 
            st.caption(f"✅ {f[0]}")
    else:
        st.warning("Sistemde henüz kayıtlı belge yok.")
    
    st.divider()
    
    if st.button("🗑️ Veritabanını Temizle", use_container_width=True):
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        db_kur()
        st.session_state.messages = []
        st.rerun()

# --- 4. ANA SOHBET PANELİ ---
st.divider()

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    gırıs_mesaji = """
    Merhaba! Ben senin kişisel doküman analiz asistanınım. 👋
    
    Sol taraftaki paneli kullanarak belgelerini yükledikten sonra bana içerikleriyle ilgili her türlü soruyu sorabilirsin. Metinleri okumaya, özetlemeye ve sana en doğru bilgiyi kaynak göstererek sunmaya hazırım. 
    """
    st.session_state.messages = [{"role": "assistant", "content": gırıs_mesaji}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Yüklenen belgeler hakkında bir soru sorun..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT content, embedding, filename FROM documents").fetchall()
    conn.close()
    
    with st.chat_message("assistant"):
        if not rows:
            tam_cevap = "Henüz sistemde işlenmiş bir belge yok. Lütfen sol taraftan dosya yükleyip 'İşle' butonuna bas."
            st.markdown(tam_cevap)
        else:
            q_vec = embed_client.generate_embedding(prompt)
            q_vec = q_vec.data[0].embedding if hasattr(q_vec, 'data') else q_vec.embedding
            
            best_score, best_text, source = -1, "", ""
            for r in rows:
                vec = json.loads(r[1])
                dot = sum(a*b for a,b in zip(q_vec, vec))
                m1 = math.sqrt(sum(a*a for a in q_vec))
                m2 = math.sqrt(sum(a*a for a in vec))
                score = dot / (m1*m2) if m1*m2 > 0 else 0
                if score > best_score:
                    best_score, best_text, source = score, r[0], r[2]
            
            if best_score < 0.35:
                tam_cevap = "Yüklenen belgelerde sorduğunuz soruyla ilgili net bir bilgiye rastlayamadım."
                st.markdown(tam_cevap)
            else:
                sistem_mesaji = "Sen profesyonel ve yardımcı bir asistansın. Verilen metne sadık kalarak son derece doğal, samimi ve akıcı bir Türkçe ile cevap ver."
                stream = llm_client.complete_streaming_chat(messages=[
                    {"role": "system", "content": sistem_mesaji},
                    {"role": "user", "content": f"Bilgi: {best_text}\n\nSoru: {prompt}"}
                ])
                ans = st.write_stream(stream)
                
                kaynak_notu = f"\n\n*📌 Kaynak: {source}*"
                st.markdown(kaynak_notu)
                
                tam_cevap = ans + kaynak_notu
        
    st.session_state.messages.append({"role": "assistant", "content": tam_cevap})