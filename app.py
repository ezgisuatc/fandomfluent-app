import streamlit as st
import json
import os
from openai import OpenAI

# 1. API Şifresi (client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 2. Sayfa Tasarımı
st.set_page_config(page_title="Fandomfluent", page_icon="📚", layout="wide")

# ================= KULLANICI VERİTABANI (LOGİN) =================
# Buraya dilediğiniz kadar kullanıcı adı ve şifre ekleyebilirsiniz.
KULLANICILAR = {
    "ogrenci1": "sifre123",
    "ogrenci2": "okuma2026",
    "ezgi": "admin"
}

# ================= GİRİŞ SİSTEMİ (AUTHENTICATION) =================
if "giris_yapildi" not in st.session_state:
    st.session_state["giris_yapildi"] = False
    st.session_state["aktif_kullanici"] = ""

if not st.session_state["giris_yapildi"]:
    st.title("🔒 Fandomfluent Giriş")
    st.write("Lütfen devam etmek için kullanıcı adı ve şifrenizi girin.")
    
    kullanici_adi = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password") # type="password" şifreyi yıldızlar
    
    if st.button("Giriş Yap"):
        if kullanici_adi in KULLANICILAR and KULLANICILAR[kullanici_adi] == sifre:
            st.session_state["giris_yapildi"] = True
            st.session_state["aktif_kullanici"] = kullanici_adi
            st.rerun() # Sayfayı yenileyip ana uygulamaya geçer
        else:
            st.error("Hatalı kullanıcı adı veya şifre! Lütfen tekrar deneyin.")
            
    # Giriş yapılmadıysa alt satırlardaki hiçbir kodu çalıştırma (Uygulamayı burada durdurur)
    st.stop() 

# ================= HAFIZA (STATE) YÖNETİMİ =================
if "orijinal_seviye" not in st.session_state:
    st.session_state["orijinal_seviye"] = None
if "islenen_metin" not in st.session_state:
    st.session_state["islenen_metin"] = ""
if "metin_gonderildi" not in st.session_state:
    st.session_state["metin_gonderildi"] = False
if "mod_ciktisi" not in st.session_state:
    st.session_state["mod_ciktisi"] = ""
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "orijinal_url" not in st.session_state:
    st.session_state["orijinal_url"] = ""

# ================= DİL SEÇİMİ =================
# Hoşgeldin mesajı ile birlikte dil seçimi
st.success(f"Hoş geldin, {st.session_state['aktif_kullanici']}!")
secilen_dil = st.radio("🌐 Dil / Language:", ["Türkçe", "English"], horizontal=True)
lang = "TR" if secilen_dil == "Türkçe" else "EN"

# ================= ARAŞTIRMACI SÖZLÜĞÜNÜ DOSYADAN OKUMA (JSON) =================
@st.cache_data
def sozluk_yukle():
    dosya_yolu = "sozluk.json"
    if os.path.exists(dosya_yolu):
        with open(dosya_yolu, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return {"Hata": {"hata": {"TR": "sozluk.json dosyası bulunamadı!", "EN": "sozluk.json file not found!"}}}

sozluk_veri = sozluk_yukle()

fandom_dict_str = ""
for kategori, kelimeler in sozluk_veri.items():
    fandom_dict_str += f"[{kategori.upper()}]: "
    fandom_dict_str += ", ".join([f"{k.upper()}: {v['EN']}" for k, v in kelimeler.items()]) + " | "

# ================= SİTE METİNLERİ (SÖZLÜK YAPISI) =================
texts = {
    "TR": {
        "title": "Fandomfluent: L2 Reading Assistant",
        "desc": "Fanfiction metinlerini hedef CEFR seviyesine göre uyarlayan ve etkileşimli sohbet sunan yapay zeka asistanı.",
        "step1": "1. Aşama",
        "level_select": "Hedef İngilizce Seviyenizi Seçin:",
        "step2": "2. Aşama",
        "action_select": "Ne yapmak istersiniz?",
        "action_options": ["Fanfiction Önerisi Al", "Kendi Fanfiction'ımı Gireceğim"],
        "fandom_input": "Hangi fandom hakkında bir öneri istersiniz? (Örn: Stray Kids, BTS, Taylor Swift vs.)",
        "btn_recommend": "Bana Fanfiction Öner",
        "recommend_loading": "Öneriler hazırlanıyor...",
        "recommend_success": "Önerileriniz Hazır!",
        "recommend_warning": "Lütfen öneri alabilmek için bir fandom ismi yazın.",
        "text_input": "İşlenecek İngilizce Fanfiction Metnini Buraya Yapıştırın:",
        "url_input": "🔗 Orijinal Fanfiction Linkini (URL) Buraya Yapıştırın (Opsiyonel):",
        "btn_send": "Metni Gönder",
        "text_warning": "Lütfen boş bırakmayın, bir metin yapıştırın.",
        "text_success": "Fanfiction sisteme başarıyla kaydedildi!",
        "btn_measure": "Önce Metnin Orijinal CEFR Seviyesini Ölç",
        "measure_loading": "Orijinal metnin seviyesi analiz ediliyor...",
        "measure_result": "📊 **Analiz Sonucu:**",
        "adapt_title": "Şimdi Metni Hedef Seviyenize ({seviye}) Göre Uyarlayın:",
        "btn_mod1": "Mod 1: Yeniden Yaz (Krashen i+1)",
        "btn_mod2": "Mod 2: İskeleleme (Scaffolding)",
        "processing": "İşleniyor... Lütfen bekleyin.",
        "cta_title": "🌟 Yazarınızı Desteklemeyi Unutmayın!",
        "cta_desc": "Fanfiction'ı beğendiyseniz orijinal sitesine gidip **beğenmeyi (kudos), yorum yapmayı** ve diğer okuyucularla etkileşime girmeyi unutmayın! Ayrıca orijinal sitede okuyup da anlamadığınız bir yorum (comment) olursa, aşağıdaki sohbet kutusundan bana sorabilirsiniz.",
        "cta_link": "👉 Orijinal Metne Git",
        "chat_placeholder": "Sorulara yanıt verin veya anlamadığınız bir kısmı/yorumu sorun...",
        "ai_lang": "Türkçe",
        "dict_header": "📖 Sözlük & Fandom Jargonu",
        "dict_desc": "Genel İngilizce kelimeleri veya fandom kısaltmalarını buradan arayabilirsiniz.",
        "dict_search": "Kelime Ara (Örn: au, canon, stay):",
        "dict_not_found": "Bu kelime sözlükte bulunamadı."
    },
    "EN": {
        "title": "Fandomfluent: L2 Reading Assistant",
        "desc": "An AI assistant that adapts fanfiction texts to the target CEFR level and provides interactive chat.",
        "step1": "Stage 1",
        "level_select": "Select Your Target English Level:",
        "step2": "Stage 2",
        "action_select": "What would you like to do?",
        "action_options": ["Get Fanfiction Recommendations", "I Will Enter My Own Fanfiction"],
        "fandom_input": "Which fandom would you like recommendations for? (e.g., Stray Kids, BTS, Taylor Swift, etc.)",
        "btn_recommend": "Recommend Fanfiction",
        "recommend_loading": "Preparing recommendations...",
        "recommend_success": "Your Recommendations Are Ready!",
        "recommend_warning": "Please enter a fandom name to get recommendations.",
        "text_input": "Paste the English Fanfiction Text Here:",
        "url_input": "🔗 Paste the Original Fanfiction Link (URL) Here (Optional):",
        "btn_send": "Submit Fanfiction",
        "text_warning": "Please do not leave it blank, paste a text.",
        "text_success": "Fanfiction successfully saved to the system!",
        "btn_measure": "Measure Original CEFR Level of Text First",
        "measure_loading": "Analyzing the original text's level...",
        "measure_result": "📊 **Analysis Result:**",
        "adapt_title": "Now Adapt the Text to Your Target Level ({seviye}):",
        "btn_mod1": "Mode 1: Rewrite (Krashen i+1)",
        "btn_mod2": "Mode 2: Scaffolding",
        "processing": "Processing... Please wait.",
        "cta_title": "🌟 Don't Forget to Support the Author!",
        "cta_desc": "If you liked the fanfiction, don't forget to go to the original site to **leave a like (kudos), comment**, and interact with other readers! Also, if there is a comment on the original site that you don't understand, you can ask me using the chat box below.",
        "cta_link": "👉 Go to Original Text",
        "chat_placeholder": "Answer the questions or ask about a part/comment you didn't understand...",
        "ai_lang": "İngilizce",
        "dict_header": "📖 Dictionary & Fandom Jargon",
        "dict_desc": "You can search for general English words or fandom acronyms here.",
        "dict_search": "Search Word (e.g., au, canon, stay):",
        "dict_not_found": "This word was not found in the dictionary."
    }
}
t = texts[lang]

# ================= SOL MENÜ (SADECE ARAMA VE ÇIKIŞ YAP) =================
with st.sidebar:
    st.header(t["dict_header"])
    st.write(t["dict_desc"])
    
    aranan_kelime = st.text_input(t["dict_search"]).strip().lower()
    
    if aranan_kelime:
        bulundu = False
        for kategori, kelimeler in sozluk_veri.items():
            if aranan_kelime in kelimeler:
                anlam = kelimeler[aranan_kelime][lang]
                st.success(f"**{aranan_kelime.upper()}** ({kategori})\n\n{anlam}")
                bulundu = True
                break
        if not bulundu:
            st.error(t["dict_not_found"])
            
    st.markdown("---")
    # Çıkış Yap Butonu
    if st.button("🚪 Çıkış Yap / Logout"):
        st.session_state["giris_yapildi"] = False
        st.session_state["aktif_kullanici"] = ""
        st.rerun()

# ================= ANA EKRAN =================
st.title(t["title"])
st.write(t["desc"])
st.markdown("---")

st.subheader(t["step1"])
seviye = st.selectbox(t["level_select"], ["A1", "A2", "B1", "B2", "C1"])

st.subheader(t["step2"])
islem = st.radio(t["action_select"], t["action_options"])

if islem == t["action_options"][0]:
    fandom = st.text_input(t["fandom_input"])
    if st.button(t["btn_recommend"]):
        if fandom:
            with st.spinner(t["recommend_loading"]):
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"Sen uzman bir İngilizce öğretmenisin. Öğrencinin seçtiği CEFR seviyesine ve verdiği fandom'a uygun İngilizce fanfiction önerileri sun. Her önerinin yanına tahmini CEFR seviyesini (Örn: CEFR B1) yaz. Cevabın tamamen İNGİLİZCE olmalıdır. Öğretmen Fandom Sözlüğü: {fandom_dict_str}"},
                        {"role": "user", "content": f"Seviyem {seviye}. Fandom: {fandom}. Lütfen okuma önerisi ver."}
                    ]
                )
                st.success(t["recommend_success"])
                st.write(resp.choices[0].message.content)
        else:
            st.warning(t["recommend_warning"])

elif islem == t["action_options"][1]:
    metin = st.text_area(t["text_input"], height=200)
    url_girdisi = st.text_input(t["url_input"])

    if metin != st.session_state["islenen_metin"]:
        st.session_state["orijinal_seviye"] = None
        st.session_state["islenen_metin"] = metin
        st.session_state["metin_gonderildi"] = False
        st.session_state["mod_ciktisi"] = ""
        st.session_state["chat_history"] = []

    if st.button(t["btn_send"]):
        if metin.strip() != "":
            st.session_state["metin_gonderildi"] = True
            st.session_state["orijinal_url"] = url_girdisi
            st.rerun()
        else:
            st.warning(t["text_warning"])

    if st.session_state["metin_gonderildi"]:
        st.success(t["text_success"])
        
        if st.button(t["btn_measure"]):
            with st.spinner(t["measure_loading"]):
                cefr_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"Verilen İngilizce metnin CEFR seviyesini belirle. Sadece seviyeyi ve nedenini açıklayan tek cümlelik kısa bir {t['ai_lang']} analiz yaz."},
                        {"role": "user", "content": metin}
                    ]
                )
                st.session_state["orijinal_seviye"] = cefr_resp.choices[0].message.content

        if st.session_state["orijinal_seviye"]:
            st.info(f"{t['measure_result']} {st.session_state['orijinal_seviye']}")
            st.markdown("---")
            st.markdown(f"### {t['adapt_title'].format(seviye=seviye)}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(t["btn_mod1"]):
                    with st.spinner(t["processing"]):
                        resp1 = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": f"Uzman İngilizce öğretmenisin. Verilen fanfiction'ı {seviye} seviyesindeki bir öğrenci için i+1 modeline göre yeniden yaz. Araştırmacının sağladığı Kategorize Fandom Sözlüğü: {fandom_dict_str}. Metnin sonuna okuduğunu anlama ile ilgili 2 İngilizce soru ekle. Cevabın tamamen İNGİLİZCE olmalı."},
                                {"role": "user", "content": metin}
                            ]
                        )
                        st.session_state["mod_ciktisi"] = resp1.choices[0].message.content
                        st.session_state["chat_history"] = [] 

            with col2:
                if st.button(t["btn_mod2"]):
                    with st.spinner(t["processing"]):
                        mod2_system_prompt = (
                            f"You are an expert English teacher. YOUR STRICT TASK is to scaffold the text for a {seviye} level student without changing the original sentence structure.\n\n"
                            "CRITICAL RULES:\n"
                            f"1. You MUST identify every single word that is above the {seviye} CEFR level.\n"
                            "2. You MUST underline these difficult words using HTML <u> tags and provide a simple English definition in parentheses right after it.\n"
                            "3. If you do not use the <u> and </u> tags, the system will break.\n\n"
                            "EXAMPLE FORMAT YOU MUST FOLLOW:\n"
                            "The <u>merchant</u> (seller) went to the <u>bustling</u> (very busy) market.\n\n"
                            f"Researcher's Categorized Fandom Dictionary: {fandom_dict_str}.\n"
                            "At the end of the text, add 2 English reading comprehension questions. Your entire response MUST be in English."
                        )

                        resp2 = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": mod2_system_prompt},
                                {"role": "user", "content": metin}
                            ]
                        )
                        st.session_state["mod_ciktisi"] = resp2.choices[0].message.content
                        st.session_state["chat_history"] = []

            # ================= İŞLENEN METİN, CTA VE SOHBET EKRANI =================
            if st.session_state["mod_ciktisi"]:
                st.markdown("---")
                st.markdown(st.session_state["mod_ciktisi"], unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                url_kismi = f"[{t['cta_link']}]({st.session_state['orijinal_url']})" if st.session_state['orijinal_url'] else ""
                st.info(f"**{t['cta_title']}**\n\n{t['cta_desc']}\n\n{url_kismi}")
                
                st.markdown("### 💬 L2 Reading Chat")
                for msg in st.session_state["chat_history"]:
                    st.chat_message(msg["role"]).write(msg["content"])
                
                user_msg = st.chat_input(t["chat_placeholder"])
                if user_msg:
                    st.session_state["chat_history"].append({"role": "user", "content": user_msg})
                    st.chat_message("user").write(user_msg)
                    
                    with st.spinner(t["processing"]):
                        chat_sys_prompt = (
                            f"You are an expert English teacher. The user just read a fanfiction adapted for their {seviye} level.\n"
                            f"Fandom Dictionary/Jargons compiled by the researcher: {fandom_dict_str}\n\n"
                            "STRICT GUARDRAILS & RULES:\n"
                            "1. The user will answer the comprehension questions you asked, OR ask about a reader comment they saw on the original site, OR ask about a jargon from the dictionary.\n"
                            "2. Respond encouragingly and correct major mistakes gently using the Krashen i+1 model.\n"
                            "3. KEEP IT RELEVANT: Only talk about the fanfiction, English language learning, or explaining reader comments/jargons.\n"
                            "4. NO INAPPROPRIATE CONTENT: If the user tries to talk about explicit/NSFW, illegal, or completely off-topic subjects, POLITELY REFUSE and redirect them back to the story.\n"
                            "5. Speak ONLY in English."
                        )
                        
                        chat_resp = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "system", "content": chat_sys_prompt}] + st.session_state["chat_history"]
                        )
                        
                        asistan_yaniti = chat_resp.choices[0].message.content
                        st.session_state["chat_history"].append({"role": "assistant", "content": asistan_yaniti})
                        st.chat_message("assistant").write(asistan_yaniti)