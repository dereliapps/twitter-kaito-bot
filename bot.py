# coding: utf-8
import requests
import time
import random
import base64
import hmac
import hashlib
import urllib.parse
import schedule
from datetime import datetime, timedelta
import os
import json

# Enhanced Twitter Bot v4 - Ultra Natural Crypto Insider Style
# 🔒 GÜVENLİ: Tüm API keyler environment variables'dan alınıyor

# API Anahtarları - Environment variables'dan al
api_key = os.getenv('TWITTER_API_KEY')
api_secret = os.getenv('TWITTER_API_SECRET') 
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_secret = os.getenv('TWITTER_ACCESS_SECRET')
bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
openai_key = os.getenv('OPENAI_API_KEY')

# API key kontrolü
print(f"🔍 API Key Kontrolü:")
print(f"   Twitter API Key: {'✅' if api_key else '❌'} {f'({api_key[:10]}...)' if api_key else ''}")
print(f"   OpenAI Key: {'✅' if openai_key else '❌'} (uzunluk: {len(openai_key) if openai_key else 0})")
if openai_key:
    print(f"   OpenAI Key başı: {openai_key[:20]}...")
    print(f"   OpenAI Key sonu: ...{openai_key[-10:]}")

print(f"🌍 Environment Variables:")
for key in ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_SECRET', 'OPENAI_API_KEY']:
    value = os.getenv(key)
    print(f"   {key}: {'✅ SET' if value else '❌ MISSING'}")

if not all([api_key, api_secret, access_token, access_secret, openai_key]):
    print("❌ Environment variables eksik! Heroku Config Vars'ı kontrol edin.")
    print("Gerekli variables: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, OPENAI_API_KEY")
    exit(1)

# Kaito projeleri - GERÇEKÇİ TÜRKÇE DATA
projects = {
    "anoma": {
        "mention": "@anoma", 
        "focus": "mahremiyet protokolü", 
        "specialty": "niyet odaklı mahremiyet",
        "search_terms": ["anoma", "namada", "privacy blockchain", "intent architecture"],
        "trends": ["mahremiyet alanında gelişmeler var", "zkApp teknolojisinde ilerlemeler", "privacy odaklı çözümler ilgi görüyor", "niyet bazlı mimari araştırılıyor"],
        "price_action": "henüz token yok, pre-mainnet aşamada",
        "ecosystem": "Cosmos SDK tabanlı L1 blockchain",
        "personality": "teknik ve mahremiyet odaklı",
        "token_status": "pre_token"
    },
    "camp_network": {
        "mention": "@campnetworkxyz", 
        "focus": "web3 kimlik", 
        "specialty": "merkeziyetsiz kimlik",
        "search_terms": ["camp network", "web3 identity", "DID protocol", "decentralized identity"],
        "trends": ["web3 kimlik alanında çalışmalar", "merkezi olmayan kimlik çözümleri", "DID teknolojisinde araştırmalar", "kimlik protokolleri gelişiyor"],
        "price_action": "token henüz çıkmadı, airdrop beklentisi var",
        "ecosystem": "Multi-chain kimlik katmanı",
        "personality": "kimlik ve sosyal odaklı",
        "token_status": "pre_token"
    },
    "virtuals": {
        "mention": "@virtuals_io", 
        "focus": "yapay zeka ajanları", 
        "specialty": "AI ajanlarını tokenlaştırma",
        "search_terms": ["virtuals protocol", "AI agents", "virtual gaming", "AI tokenization"],
        "trends": ["AI ajan tokenları ilgi görüyor", "yapay zeka tokenlaştırması", "GameFi AI entegrasyonları", "AI trading botları popüler"],
        "price_action": "AI token sektöründe performans gösteriyor",
        "ecosystem": "Sanal oyun metaverse'ü",
        "personality": "AI ve oyun odaklı",
        "token_status": "active"
    },
    "somnia": {
        "mention": "@somnia_network", 
        "focus": "gerçek zamanlı blockchain", 
        "specialty": "400 bin TPS performans",
        "search_terms": ["somnia network", "real-time blockchain", "gaming blockchain", "high performance"],
        "trends": ["gaming blockchain alanında çalışmalar", "gerçek zamanlı blockchain teknolojisi", "yüksek performans odaklı geliştirme", "oyun odaklı çözümler"],
        "price_action": "mainnet öncesi, hype artıyor",
        "ecosystem": "Yüksek performanslı gaming blockchain",
        "personality": "performans ve gaming odaklı",
        "token_status": "pre_token"
    },
    "union": {
        "mention": "@union_build", 
        "focus": "zk interoperabilite", 
        "specialty": "sıfır bilgi köprüleri",
        "search_terms": ["union build", "zk interoperability", "zero knowledge bridges", "cross chain"],
        "trends": ["zk köprü teknolojisinde ilerlemeler", "çapraz zincir güvenlik çözümleri", "interoperabilite araştırmaları", "IBC protokolü geliştirmeleri"],
        "price_action": "airdrop beklentisi çok yüksek",
        "ecosystem": "Çapraz zincir altyapısı",
        "personality": "teknik ve köprü odaklı",
        "token_status": "pre_token"
    },
    "mitosis": {
        "mention": "@mitosisorg", 
        "focus": "likidite protokolü", 
        "specialty": "programlanabilir likidite",
        "search_terms": ["mitosis protocol", "programmable liquidity", "defi protocol", "automated market making"],
        "trends": ["likidite protokolü geliştirmeleri", "otomatik pazar yapıcılığı", "çapraz zincir likidite", "DeFi yield optimizasyonu"],
        "price_action": "TVL hızla büyüyor",
        "ecosystem": "Yeni nesil DeFi protokolü",
        "personality": "DeFi ve yield odaklı",
        "token_status": "pre_token"
    }
}

# Tweet uzunluk kategorileri
TWEET_LENGTHS = {
    "short": {"weight": 25, "min": 300, "max": 500, "style": "punch"},    # %25 - Kısa & Punch
    "medium": {"weight": 50, "min": 500, "max": 1000, "style": "normal"},  # %50 - Normal 
    "long": {"weight": 25, "min": 1000, "max": 1500, "style": "analysis"}   # %25 - Uzun analiz
}

# Rate limiting için son tweet zamanı
last_tweet_time = None
MINIMUM_INTERVAL = 15 * 60  # 15 dakika (saniye)

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

def search_twitter_sentiment(project_key):
    """Twitter'da proje hakkında son tweet'leri ara ve sentiment analizi yap"""
    try:
        project = projects[project_key]
        search_terms = project['search_terms']
        
        # Bearer token ile Twitter API v2 search
        url = "https://api.twitter.com/2/tweets/search/recent"
        
        # Search query oluştur
        query_parts = []
        for term in search_terms[:2]:  # İlk 2 terimi kullan
            query_parts.append(f'"{term}"')
        
        query = f"({' OR '.join(query_parts)}) -is:retweet lang:en"
        
        params = {
            'query': query,
            'max_results': 20,
            'tweet.fields': 'created_at,public_metrics,text',
            'sort_order': 'recency'
        }
        
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            tweets = data.get('data', [])
            
            if tweets:
                # Sentiment analizi için tweet'leri analiz et
                recent_topics = []
                engagement_data = []
                
                for tweet in tweets:
                    text = tweet['text'].lower()
                    metrics = tweet['public_metrics']
                    
                    # Engagement hesapla (like + retweet*2 + reply*3)
                    engagement = metrics['like_count'] + (metrics['retweet_count'] * 2) + (metrics['reply_count'] * 3)
                    engagement_data.append(engagement)
                    
                    # Basit sentiment
                    positive_words = ['good', 'great', 'bullish', 'moon', 'pump', 'win', 'amazing', 'love']
                    negative_words = ['bad', 'dump', 'bearish', 'scam', 'rekt', 'down', 'crash', 'hate']
                    
                    pos_count = sum(1 for word in positive_words if word in text)
                    neg_count = sum(1 for word in negative_words if word in text)
                    
                    if pos_count > neg_count:
                        recent_topics.append("positive_sentiment")
                    elif neg_count > pos_count:
                        recent_topics.append("negative_sentiment") 
                    else:
                        recent_topics.append("neutral_news")
                
                # En yaygın sentiment
                if recent_topics:
                    sentiment = max(set(recent_topics), key=recent_topics.count)
                else:
                    sentiment = "neutral_news"
                
                # Engagement seviyesi
                avg_engagement = sum(engagement_data) / len(engagement_data) if engagement_data else 0
                if avg_engagement > 100:
                    engagement_level = "high"
                elif avg_engagement > 20:
                    engagement_level = "medium"
                else:
                    engagement_level = "low"
                
                return {
                    "sentiment": sentiment,
                    "engagement_level": engagement_level,
                    "topics": recent_topics[:3]
                }
        
        # Default fallback
        return {
            "sentiment": random.choice(["positive_sentiment", "neutral_news", "negative_sentiment"]),
            "engagement_level": random.choice(["low", "medium", "high"]),
            "topics": ["general_discussion"]
        }
        
    except Exception as e:
        print(f"🔍 Twitter sentiment arama hatası: {e}")
        return {
            "sentiment": random.choice(["positive_sentiment", "neutral_news"]),
            "engagement_level": "medium",
            "topics": ["general_discussion"]
        }

def choose_tweet_length():
    """Ağırlıklı rastgele tweet uzunluğu seç"""
    rand = random.randint(1, 100)
    if rand <= 25:
        return TWEET_LENGTHS["short"]
    elif rand <= 75:
        return TWEET_LENGTHS["medium"] 
    else:
        return TWEET_LENGTHS["long"]

def get_enhanced_ai_tweet(project_key, sentiment_data, target_length):
    """Enhanced AI tweet - güncel sentiment + hedef uzunluk ile - ULTRA NATURAL"""
    project = projects[project_key]
    length_config = target_length
    
    # SORU SORMA, BİLGİ VER!
    style_prompts = {
        "punch": f"""soru sorma! {project['mention']} hakkında {length_config['min']}-{length_config['max']} karakter tweet yaz.

ÖRNEK: "ya {project['mention']} baya ilginç proje aslında. {project['focus']} alanında çalışıyorlar, potansiyeli var bence"

küçük harf, samimi, bilgi ver!""",
        
        "normal": f"""soru sorma! {project['mention']} hakkında {length_config['min']}-{length_config['max']} karakter tweet yaz.

ÖRNEK: "bence {project['mention']} gerçekten farklı bir yerde duruyor. {project['focus']} alanında ciddi işler yapıyorlar. henüz mainstream değil ama gelecekte büyük olabilir gibi geliyor"

küçük harf, samimi, bilgi ver!""",
        
        "analysis": f"""soru sorma! {project['mention']} hakkında {length_config['min']}-{length_config['max']} karakter uzun analiz yaz.

ÖRNEK: "{project['mention']} son zamanlarda baya hareketli. {project['focus']} sektöründe büyüme gösteriyorlar. erken yatırımcılar için fırsat olabilir. teknolojileri sağlam duruyor, gelecekte büyük oyuncu olma ihtimali var"

küçük harf, samimi, spekülasyon yapabilirsin!"""
    }
    
    prompt = style_prompts[length_config['style']]
    
    # ChatGPT API call
    headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": f"""sen crypto'yla ilgilenen samimi bir türksün. arkadaşına konuşur gibi doğal ol.

YAPMA:
- hashtag kullanma
- soru sorma (kim takip ediyor, nasıl vs.)
- @ ile başlatma
- büyük harf kullanma çok

YAP:
- {length_config['min']}-{length_config['max']} karakter
- {project['mention']} mention et 
- bilgi ver, görüş paylaş
- küçük harf, samimi ton
- ara sıra spekülasyon

sadece tweet yaz!"""},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 400,
        "temperature": 1.0
    }
    
    try:
        print(f"🤖 ChatGPT API çağrısı yapılıyor...")
        print(f"🔑 API Key başı: {openai_key[:20]}..." if openai_key else "❌ API Key YOK!")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        
        print(f"📡 API Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            tweet = result['choices'][0]['message']['content'].strip()
            
            print(f"✅ ChatGPT Tweet: {tweet}")
            
            # HASHTAG VE UZUN ÇİZGİ TEMİZLİK
            tweet = tweet.replace('—', ' ')
            tweet = tweet.replace('–', ' ')
            tweet = tweet.replace('-', ' ')
            
            # Hashtag'leri temizle
            import re
            tweet = re.sub(r'#\w+', '', tweet)  # #bitcoin, #crypto vs. sil
            tweet = re.sub(r'\s+', ' ', tweet)  # Çoklu boşlukları tek yap
            tweet = tweet.strip()  # Baştan sondaki boşlukları sil
            
            # @ ile başlarsa düzelt (ana timeline'da gözükmez yoksa)
            if tweet.startswith('@'):
                # @mention'ı bul ve tweet'i yeniden düzenle
                parts = tweet.split(' ', 1)
                if len(parts) > 1:
                    mention = parts[0]
                    rest = parts[1]
                    # Mention'ı ortaya koy
                    tweet = f"şu {mention} nasıl bence? {rest}"
                    print(f"🔧 @ ile başlıyordu, düzeltildi: {tweet}")
            
            print(f"🧹 Temizlenmiş tweet: {tweet}")
            
            # Uzunluk kontrolü - eğer uygun değilse kısalt veya uzat
            if len(tweet) > length_config['max']:
                tweet = tweet[:length_config['max']-3] + "..."
                print(f"✂️ Tweet kısaltıldı: {len(tweet)} karakter")
            elif len(tweet) < length_config['min']:
                tweet += " takip etmeye değer bence."
                print(f"📏 Tweet uzatıldı: {len(tweet)} karakter")
            
            print(f"✅ ChatGPT tweet kullanılıyor!")
            return tweet
        else:
            print(f"❌ AI API hatası: {response.status_code}")
            print(f"❌ Response body: {response.text}")
            print(f"❌ Request data: {data}")
            # Tekrar dene, farklı prompt ile
            return retry_chatgpt(project_key, length_config, attempt=1)
            
    except Exception as e:
        print(f"❌ AI request exception: {e}")
        print(f"❌ Exception type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        # Tekrar dene
        return retry_chatgpt(project_key, length_config, attempt=1)

def retry_chatgpt(project_key, length_config, attempt):
    """ChatGPT'yi tekrar dene"""
    if attempt > 3:
        print(f"❌ 3 deneme başarısız! Basit tweet kullanılacak.")
        return f"kim takip ediyor {projects[project_key]['mention']}? bence ilginç proje."
    
    print(f"🔄 ChatGPT tekrar deneniyor... (deneme {attempt}/3)")
    
    # SORU SORMA RETRY
    simple_prompt = f"""soru sorma! bilgi ver!

{projects[project_key]['mention']} hakkında {length_config['min']}-{length_config['max']} karakter tweet yaz.

ÖRNEK: "ya {projects[project_key]['mention']} baya solid proje. potansiyeli var bence"

küçük harf, samimi ol!"""
    
    headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": simple_prompt}
        ],
        "max_tokens": 350,
        "temperature": 1.0
    }
    
    try:
        print(f"🔄 Retry API çağrısı yapılıyor...")
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        print(f"🔄 Retry Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            tweet = result['choices'][0]['message']['content'].strip()
            
            # RETRY TEMİZLİK
            tweet = tweet.replace('—', ' ').replace('–', ' ').replace('-', ' ')
            import re
            tweet = re.sub(r'#\w+', '', tweet)  # Hashtag'leri sil
            tweet = re.sub(r'\s+', ' ', tweet)  # Çoklu boşlukları tek yap
            tweet = tweet.strip()
            
            # @ ile başlarsa düzelt
            if tweet.startswith('@'):
                parts = tweet.split(' ', 1)
                if len(parts) > 1:
                    mention = parts[0]
                    rest = parts[1]
                    tweet = f"şu {mention} nasıl bence? {rest}"
                    print(f"🔧 Retry: @ ile başlıyordu, düzeltildi: {tweet}")
            
            print(f"✅ Retry başarılı (temizlenmiş): {tweet}")
            return tweet
        else:
            print(f"❌ Retry hatası: {response.status_code} - {response.text}")
            return retry_chatgpt(project_key, length_config, attempt + 1)
    except Exception as e:
        print(f"❌ Retry exception: {e}")
        return retry_chatgpt(project_key, length_config, attempt + 1)



def test_openai():
    """OpenAI API test"""
    headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ OpenAI API çalışıyor!")
            return True
        else:
            print(f"❌ OpenAI API hatası: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ OpenAI API exception: {e}")
        return False

def test_twitter():
    """Twitter API test"""
    url = "https://api.twitter.com/2/users/me"
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

def send_tweet(content):
    """Tweet gönder - Rate limiting ile"""
    global last_tweet_time
    
    # Rate limiting kontrolü
    current_time = time.time()
    if last_tweet_time:
        time_since_last = current_time - last_tweet_time
        if time_since_last < MINIMUM_INTERVAL:
            wait_time = MINIMUM_INTERVAL - time_since_last
            print(f"⏳ Rate limiting: {wait_time/60:.1f} dakika beklemek gerekiyor...")
            return False
    
    url = "https://api.twitter.com/2/tweets"
    auth_header = create_oauth_header("POST", url)
    headers = {"Authorization": auth_header, "Content-Type": "application/json"}
    data = {"text": content}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        result = response.json()
        tweet_id = result['data']['id']
        last_tweet_time = current_time  # Başarılı tweet sonrası zamanı güncelle
        print(f"✅ Tweet gönderildi!")
        print(f"📝 İçerik: {content}")
        print(f"🔗 Tweet ID: {tweet_id}")
        print(f"📊 Uzunluk: {len(content)} karakter")
        return True
    elif response.status_code == 429:
        print(f"⚠️ Twitter API rate limit! 15 dakika bekliyorum...")
        print("🔄 Bot otomatik olarak bekleyecek ve daha sonra dener")
        return False
    else:
        print(f"❌ Tweet gönderme hatası: {response.text}")
        return False

def create_enhanced_tweet():
    """Enhanced tweet oluştur ve gönder"""
    try:
        # Rastgele proje seç
        project_key = random.choice(list(projects.keys()))
        
        # Sentiment analizi yap
        sentiment_data = search_twitter_sentiment(project_key)
        
        # Tweet uzunluğu seç
        length_config = choose_tweet_length()
        
        print(f"🎯 Seçilen proje: {projects[project_key]['mention']} - {projects[project_key]['focus']}")
        print(f"📊 Sentiment: {sentiment_data['sentiment']} | Engagement: {sentiment_data['engagement_level']}")
        print(f"📏 Tweet stili: {length_config['style']} ({length_config['min']}-{length_config['max']} karakter)")
        
        # Enhanced AI tweet oluştur
        tweet_content = get_enhanced_ai_tweet(project_key, sentiment_data, length_config)
        
        print(f"💬 Tweet hazır: {tweet_content}")
        print(f"📊 Uzunluk: {len(tweet_content)} karakter")
        
        # Tweet'i gönder
        success = send_tweet(tweet_content)
        
        if success:
            print("🎉 Tweet başarıyla gönderildi!")
        else:
            print("❌ Tweet gönderme başarısız!")
            
        return success
        
    except Exception as e:
        print(f"❌ Tweet oluşturma hatası: {e}")
        return False

def auto_tweet():
    """Otomatik tweet fonksiyonu"""
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Otomatik tweet başlatılıyor...")
    
    # Rate limiting kontrolü
    global last_tweet_time
    if last_tweet_time:
        time_since_last = time.time() - last_tweet_time
        if time_since_last < MINIMUM_INTERVAL:
            wait_time = MINIMUM_INTERVAL - time_since_last
            print(f"⏳ Rate limiting aktif: {wait_time/60:.1f} dakika daha beklemeli")
            return False
    
    success = create_enhanced_tweet()
    if success:
        print("✅ Otomatik tweet tamamlandı!")
    else:
        print("❌ Otomatik tweet başarısız!")
    
    return success

def auto_bot():
    """7/24 otomatik bot"""
    print("🤖 Enhanced Kaito Twitter Bot v4 başlatılıyor...")
    
    # API testleri
    if not test_twitter():
        print("❌ Twitter API bağlantısı başarısız! Bot durduruluyor.")
        return
    
    if not test_openai():
        print("⚠️ OpenAI API çalışmıyor! Sadece basit template'ler kullanılacak.")
    else:
        print("✅ Tüm API'ler çalışıyor!")
    
    # İlk tweet'i hemen at
    print("🚀 İlk tweet atılıyor...")
    auto_tweet()
    
    # Schedule ayarla: Her 2-4 saatte bir rastgele (rate limiting ile)
    def safe_auto_tweet():
        if random.randint(1, 100) <= 30:
            print("🎲 Şans tuttu! Tweet deneniyor...")
            return auto_tweet()
        else:
            print("🎲 Bu sefer pas geçiliyor...")
            return False
    
    schedule.every().hour.do(safe_auto_tweet)
    
    print("⏰ Bot schedule'ı ayarlandı: Her saat %30 ihtimalle tweet (rate limiting korumalı)")
    print("🔄 Bot çalışmaya başladı! Ctrl+C ile durdurun.")
    
    # Sonsuz döngü
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et
        except KeyboardInterrupt:
            print("\n⏹️ Bot durduruldu!")
            break
        except Exception as e:
            print(f"❌ Bot hatası: {e}")
            time.sleep(300)  # 5 dakika bekle ve devam et

def main():
    """Ana fonksiyon"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🧪 Test modu - Tek tweet")
        create_enhanced_tweet()
    else:
        print("🤖 Otomatik bot modu")
        auto_bot()

if __name__ == "__main__":
    main()
