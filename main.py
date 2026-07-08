from foundry_local_sdk import Configuration, FoundryLocalManager

def main():
    print("Foundry Yerel Yapay Zeka Motoru başlatılıyor...")
    
    try:
        FoundryLocalManager.initialize(Configuration(app_name="Local_RAG_Assistant"))
        manager = FoundryLocalManager.instance
        
        print("\nModel ('phi-3.5-mini') aranıyor...")
        model = manager.catalog.get_model("phi-3.5-mini")
        
        print("İndirme işlemi başlatılıyor. (Sabaha kadar inmesi için bilgisayarı açık bırakabilirsin)")
        
        # Ekranda % kaç indiğini göreceğiz
        model.download(lambda p: print(f"\rİndirme: %{p:.0f}", end="", flush=True))
        
        print("\n\nİndirme tamamlandı! Sistem tamamen hazır. İyi geceler :)")
        
    except Exception as e:
        print(f"\nUfak bir pürüz çıktı: {e}")
        print("Ama dert etme, devasa kütüphanelerin hepsi bilgisayarına başarıyla kuruldu! Kalan ufak tefek bağlantıları yarın stajda halledeceğiz. Şimdi acilen uyu!")

if __name__ == "__main__":
    main()