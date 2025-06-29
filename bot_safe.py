# coding: utf-8
import requests
import time
import random
import base64
import hmac
import hashlib
import urllib.parse
import schedule
from datetime import datetime

# Twitter Bot v2 - OAuth 1.0a Kullanımı (Environment Variables)
import os

# 🔒 API Anahtarları - Environment variables'dan al (GÜVENLİ)
api_key = os.getenv('TWITTER_API_KEY')
api_secret = os.getenv('TWITTER_API_SECRET') 
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_secret = os.getenv('TWITTER_ACCESS_SECRET')
bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
openai_key = os.getenv('OPENAI_API_KEY')

# API key kontrolü
if not all([api_key, api_secret, access_token, access_secret, openai_key]):
    print("❌ Environment variables eksik! Heroku Config Vars'ı kontrol edin.")
    print("Gerekli variables: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, OPENAI_API_KEY")
    exit(1)

# Kaito projeleri - GERÇEK TREND VERİLERİ
projects = {
    "anoma": {
        "mention": "@anoma", 
        "focus": "privacy protocol", 
        "specialty": "intent-centric privacy",
        "trends": ["$57.8M Series A fonlaması", "Namada testnet başlatıldı", "zkApp ekosistemi genişliyor", "Privacy coin düzenlemeleri sonrası alternatif çözüm"],
        "price_action": "son 30 günde %45 yükseliş",
        "ecosystem": "Cosmos SDK tabanlı L1 blockchain"
    },
    "camp_network": {
        "mention": "@campnetworkxyz", 
        "focus": "web3 identity", 
        "specialty": "decentralized identity",
        "trends": ["$25M Series A yatırımı aldı", "Web3 kimlik doğrulama standartları", "DID protokolü geliştiriyor", "Lens Protocol entegrasyonu"],
        "price_action": "pre-token aşamasında",
        "ecosystem": "Multi-chain identity layer"
    },
    "virtuals": {
        "mention": "@virtuals_io", 
        "focus": "ai agents", 
        "specialty": "tokenizing ai agents",
        "trends": ["AI agent tokenları pump ediyor", "$VIRTUAL token 150x yaptı", "GameFi AI entegrasyonları", "ChatGPT API entegrasyonu"],
        "price_action": "$2.1B market cap ulaştı",
        "ecosystem": "Virtual gaming metaverse"
    },
    "somnia": {
        "mention": "@somnia_network", 
        "focus": "real-time blockchain", 
        "specialty": "400k tps performance",
        "trends": ["$35M seed round tamamlandı", "Gaming odaklı L1 blockchain", "Unity Engine entegrasyonu", "Real-time multiplayer games"],
        "price_action": "mainnet öncesi hype artıyor",
        "ecosystem": "High-performance gaming blockchain"
    },
    "union": {
        "mention": "@union_build", 
        "focus": "zk interoperability", 
        "specialty": "zero-knowledge bridges",
        "trends": ["$16M fonlama aldı", "ZK bridge güvenlik sorunlarına çözüm", "Ethereum-Cosmos köprüsü", "IBC protokolü geliştirmeleri"],
        "price_action": "airdrop beklentisi yüksek",
        "ecosystem": "Cross-chain infrastructure"
    },
    "mitosis": {
        "mention": "@mitosisorg", 
        "focus": "liquidity protocol", 
        "specialty": "programmable liquidity",
        "trends": ["$7M seed round", "Automated market making", "Cross-chain liquidity", "DeFi yield farming 2.0"],
        "price_action": "TVL hızla artıyor",
        "ecosystem": "Next-gen DeFi protocol"
    }
}

def create_oauth_signature(method, url, params, consumer_secret, token_secret):
    """OAuth 1.0a signature oluştur"""
    # Parametreleri encode et ve sırala
    encoded_params = []
    for key, value in params.items():
        encoded_key = urllib.parse.quote(str(key), safe='')
        encoded_value = urllib.parse.quote(str(value), safe='')
        encoded_params.append((encoded_key, encoded_value))
    
    sorted_params = sorted(encoded_params)
    param_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    
    # Base string oluştur
    encoded_url = urllib.parse.quote(url, safe='')
    encoded_params_string = urllib.parse.quote(param_string, safe='')
    base_string = f"{method}&{encoded_url}&{encoded_params_string}"
    
    # Signing key oluştur
    encoded_consumer_secret = urllib.parse.quote(consumer_secret, safe='')
    encoded_token_secret = urllib.parse.quote(token_secret, safe='')
    signing_key = f"{encoded_consumer_secret}&{encoded_token_secret}"
    
    # Signature hesapla
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()
    
    return signature

def create_oauth_header(method, url, params=None):
    """OAuth 1.0a authorization header oluştur"""
    if params is None:
        params = {}
    
    # OAuth parametreleri
    oauth_params = {
        'oauth_consumer_key': api_key,
        'oauth_token': access_token,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(datetime.now().timestamp())),
        'oauth_nonce': str(random.randint(100000, 999999)),
        'oauth_version': '1.0'
    }
    
    # Tüm parametreleri birleştir
    all_params = {**oauth_params, **params}
    
    # Signature oluştur
    signature = create_oauth_signature(method, url, all_params, api_secret, access_secret)
    oauth_params['oauth_signature'] = signature
    
    # Authorization header oluştur
    auth_parts = []
    for key, value in sorted(oauth_params.items()):
        auth_parts.append(f'{key}="{urllib.parse.quote(str(value), safe="")}"')
    
    return f"OAuth {', '.join(auth_parts)}"

def test_twitter():
    """Twitter API test (OAuth 1.0a ile)"""
    url = "https://api.twitter.com/2/users/me"
    
    # OAuth 1.0a authorization header oluştur
    auth_header = create_oauth_header("GET", url)
    
    headers = {"Authorization": auth_header}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        username = data.get('data', {}).get('username', 'unknown')
        print(f"✅ Twitter API çalışıyor! Kullanıcı: @{username}")
        return True
    else:
        print(f"❌ Twitter API hatası: {response.text}")
        return False

def get_ai_tweet(prompt):
    """ChatGPT ile GERÇEK crypto influencer tweetı oluştur"""
    headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": """Sen deneyimli bir crypto trader ve influencer'sın. 
            Tweetlerin:
            - Gerçek piyasa analizi içermeli
            - Crypto slang kullan (pump, moon, gem, alpha, etc.)
            - Emojiler kullan ama abartma
            - 500-800 karakter arası uzun olabilir
            - AI'mış gibi değil, gerçek bir insan gibi yaz
            - Trend analizi, fiyat hareketleri, teknoloji gelişmeleri hakkında konuş
            - Bazen eleştirel, bazen bullish ol
            - Thread tarzında yazabilirsin"""},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.9
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    else:
        print(f"❌ AI API hatası: {response.text}")
        return None

def send_tweet(content):
    """Tweet gönder (OAuth 1.0a ile)"""
    url = "https://api.twitter.com/2/tweets"
    
    # OAuth 1.0a authorization header oluştur
    auth_header = create_oauth_header("POST", url)
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    data = {"text": content}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        result = response.json()
        tweet_id = result['data']['id']
        print(f"\n🐦 TWEET GÖNDERİLDİ!")
        print(f"📝 İçerik: {content}")
        print(f"🆔 ID: {tweet_id}")
        print(f"🔗 Link: https://twitter.com/i/web/status/{tweet_id}")
        return True
    else:
        print(f"❌ Tweet hatası: {response.text}")
        return False

def create_tweet():
    """GERÇEK crypto trader gibi trend odaklı tweet oluştur"""
    project_key = random.choice(list(projects.keys()))
    project = projects[project_key]
    mention = project["mention"]
    
    # Rastgele trend seç
    current_trend = random.choice(project["trends"])
    
    # Tweet türleri - GERÇEK crypto influencer tarzı
    tweet_styles = [
        "market_analysis",
        "trend_analysis", 
        "price_action",
        "ecosystem_update",
        "alpha_call",
        "critical_take"
    ]
    
    style = random.choice(tweet_styles)
    
    # Style'a göre prompt oluştur
    prompts = {
        "market_analysis": f"""
        {mention} hakkında market analizi yap. 
        Trend: {current_trend}
        Price action: {project['price_action']}
        Ecosystem: {project['ecosystem']}
        
        Gerçek bir crypto trader gibi piyasa durumunu analiz et. Technical analysis, fundamentals, ve market sentiment hakkında konuş.
        """,
        
        "trend_analysis": f"""
        {mention} projesindeki bu güncel gelişmeyi analiz et: {current_trend}
        
        Bu trend'in piyasaya etkisini, fırsatları ve riskleri crypto trader gözüyle değerlendir. Sonunda {mention} ekle.
        """,
        
        "price_action": f"""
        {mention} - {project['price_action']} 
        
        Bu fiyat hareketinin arkasındaki sebepleri analiz et. Chart analizi yap, destek/direnç seviyelerinden bahset. Crypto trader gözüyle bakış açısı sun.
        """,
        
        "ecosystem_update": f"""
        {project['ecosystem']} ekosisteminde önemli gelişme: {current_trend}
        
        Bu gelişmenin {mention} ve genel crypto piyasasına etkilerini değerlendir. Teknik detaylara gir.
        """,
        
        "alpha_call": f"""
        ALPHA: {mention} 
        
        {current_trend} - Bu gelişme neden önemli? Erken yatırımcı gözüyle potansiyeli analiz et. Risk/reward ratio'yu değerlendir.
        """,
        
        "critical_take": f"""
        {mention} hakkında objektif bakış açısı:
        
        Trend: {current_trend}
        
        Hype'ı bir kenara bırakıp gerçek fundamentalleri analiz et. Eleştirel yaklaş, hem pozitif hem negatif yönleri değerlendir.
        """
    }
    
    prompt = prompts[style]
    
    # AI ile tweet oluştur
    ai_tweet = get_ai_tweet(prompt)
    
    if ai_tweet and len(ai_tweet) >= 200:  # Minimum 200 karakter istiyoruz
        return ai_tweet
    else:
        # Fallback - Manuel trend tweet
        fallback_tweets = [
            f"📊 {mention} son durumda {project['price_action']}. {current_trend} gelişmesi piyasada ses getiriyor. {project['ecosystem']} ekosistemindeki bu hareket dikkat çekiyor. Fundamentallere baktığımızda...",
            
            f"🔥 {current_trend} - {mention} için game changer olabilir. {project['ecosystem']} alanında bu gelişme sadece başlangıç. Price action: {project['price_action']}. Early adopters için kritik seviyeler...",
            
            f"⚡ THREAD: {mention} analizi\n\n1/ {current_trend}\n2/ {project['price_action']}\n3/ {project['ecosystem']} potential massive\n\nDetaylı analiz comment'larda 👇"
        ]
        return random.choice(fallback_tweets)

def auto_tweet():
    """Otomatik tweet gönder"""
    tweet = create_tweet()
    success = send_tweet(tweet)
    if success:
        print(f"✅ Otomatik tweet gönderildi: {tweet[:50]}...")
    else:
        print("❌ Otomatik tweet gönderilemedi")
    return success

def show_menu():
    """Ana menüyü göster"""
    print("\n" + "="*50)
    print("🤖 KAITO TWITTER BOT v2")
    print("="*50)
    print("📱 Desteklenen Projeler:")
    for key, project in projects.items():
        print(f"   • {project['mention']} - {project['focus']}")
    print("\n📋 MENÜ:")
    print("1. 🔍 Twitter API Test Et")
    print("2. 📝 Tek Tweet Oluştur & Gönder")
    print("3. 🤖 Otomatik Bot Başlat (Her 3 saatte bir)")
    print("4. ⚡ Test Tweet Gönder")
    print("5. 📊 Proje Listesi Göster")
    print("6. ❌ Çıkış")
    print("="*50)

def auto_bot():
    """Otomatik bot - her 3 saatte bir tweet atar"""
    
    print("\n🚀 Otomatik bot başlatılıyor...")
    print("📅 Program: Her 3 saatte bir tweet")
    print("⏰ Saatler: 09:00, 12:00, 15:00, 18:00, 21:00")
    print("🛑 Durdurmak için Ctrl+C basın\n")
    
    # Schedule ayarla
    schedule.every().day.at("09:00").do(auto_tweet)
    schedule.every().day.at("12:00").do(auto_tweet)
    schedule.every().day.at("15:00").do(auto_tweet)
    schedule.every().day.at("18:00").do(auto_tweet)
    schedule.every().day.at("21:00").do(auto_tweet)
    
    # Test için şimdi bir tweet gönder
    print("🔥 İlk tweet gönderiliyor...")
    auto_tweet()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et
    except KeyboardInterrupt:
        print("\n🛑 Otomatik bot durduruldu!")

def main():
    """Ana program - Heroku'da otomatik, local'de menü"""
    print("🚀 Kaito Twitter Bot başlatılıyor...")
    
    # Twitter API test
    if not test_twitter():
        print("❌ Twitter API bağlantı hatası! Bot durduruluyor...")
        return
    
    # Heroku environment kontrol
    is_heroku = os.getenv('DYNO') or os.getenv('PORT') or os.getenv('HEROKU_APP_NAME')
    
    if is_heroku:
        print("🔥 Heroku'da çalışıyor - otomatik mod aktif!")
        auto_bot()  # Heroku'da otomatik çalış
        return
    
    # Local'de menü sistemi
    print("💻 Local'de çalışıyor - menü sistemi aktif!")
    
    while True:
        show_menu()
        choice = input("\n👉 Seçiminiz (1-6): ").strip()
        
        if choice == "1":
            print("\n🔍 Twitter API test ediliyor...")
            test_twitter()
            
        elif choice == "2":
            print("\n📝 Tweet oluşturuluyor...")
            tweet = create_tweet()
            print(f"\n💬 Oluşturulan Tweet:")
            print(f"📝 {tweet}")
            print(f"📏 Uzunluk: {len(tweet)} karakter")
            
            confirm = input("\n✅ Göndermek için 'y', iptal için Enter: ").strip().lower()
            if confirm == 'y':
                send_tweet(tweet)
            else:
                print("❌ Tweet gönderimi iptal edildi")
                
        elif choice == "3":
            auto_bot()
            
        elif choice == "4":
            test_tweet = "🤖 Bot test ediyor! Kaito projeleri ile ilgili tweetler yakında... #KaitoBot"
            print(f"\n⚡ Test Tweet: {test_tweet}")
            confirm = input("\n✅ Test tweet göndermek için 'y': ").strip().lower()
            if confirm == 'y':
                send_tweet(test_tweet)
            else:
                print("❌ Test tweet iptal edildi")
                
        elif choice == "5":
            print("\n📊 KAITO PROJELERİ:")
            print("-" * 40)
            for key, project in projects.items():
                print(f"🔹 {project['mention']}")
                print(f"   └ Alan: {project['focus']}")
                print(f"   └ Özellik: {project['specialty']}")
                print()
                
        elif choice == "6":
            print("\n👋 Bot kapatılıyor... Görüşürüz!")
            break
            
        else:
            print("❌ Geçersiz seçim! Lütfen 1-6 arası bir sayı girin.")
            
        input("\n↩️  Devam etmek için Enter'a basın...")

if __name__ == "__main__":
    main()