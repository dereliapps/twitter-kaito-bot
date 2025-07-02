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
import re
# News monitoring imports kaldırıldı

# ------------------------------------------------------------
# Ortam Değişkenlerini .env dosyasından yükle ve UTF-8 çıktı ayarla
# ------------------------------------------------------------
import sys as _sys

# Konsol Unicode hatalarını önlemek için
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8")

# .env dosyasını yükle (python-dotenv varsa) yoksa basit fallback
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()
except ModuleNotFoundError:
    import pathlib
    env_path = pathlib.Path(__file__).with_name('.env')
    if env_path.exists():
        for _line in env_path.read_text(encoding='utf-8').splitlines():
            if '=' in _line and not _line.strip().startswith('#'):
                k, v = _line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

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

# API KEY KONTROLÜ - Production için sadece environment variables
import sys
if not all([api_key, api_secret, access_token, access_secret, openai_key]):
    print("❌ Gerekli environment variable'lar eksik!")
    print("🔧 Lütfen şu environment variable'ları ayarlayın:")
    print("   - TWITTER_API_KEY")
    print("   - TWITTER_API_SECRET") 
    print("   - TWITTER_ACCESS_TOKEN")
    print("   - TWITTER_ACCESS_SECRET")
    print("   - OPENAI_API_KEY")
    print("💡 Heroku'da: heroku config:set TWITTER_API_KEY=your_key")
    sys.exit(1)

print("✅ Tüm API anahtarları environment variable'lardan yüklendi!")

# Kaito projeleri - GERÇEKÇİ TÜRKÇE DATA
projects = {
    "anoma": {
        "mention": "@anoma", 
        "focus": "intent-centric blockchain", 
        "specialty": "kullanıcı deneyiminde radikal basitleştirme sunan intent-based mimari",
        "trends": ["intent-based mimariler gelişiyor", "kullanıcı deneyimi odaklı blockchain", "mahremiyet teknolojileri", "chain-agnostic çözümler"],
        "price_action": "mainnet öncesi geliştirme aşamasında", 
        "ecosystem": "Cosmos SDK tabanlı L1 blockchain",
        "personality": "teknik ve mahremiyet odaklı",
        "token_status": "pre_token",
        "tech_detail": "Intent-centric mimarisi, kullanıcıların 'ne yapmak istediklerini' belirtmesiyle yetinen sistem. Arka planda zincirler arası en uygun yolu otomatik hesaplıyor. zk-SNARKs teknolojisiyle entegre privacy özellikleri, geleneksel cross-chain çözümlerden ayrışıyor. Geliştirme sürecinde 3000+ TPS performans hedefini belirlemişler.",
        "performance_data": "3000+ TPS hedef performans",
        "development_stage": "geliştirme aşamasında (testnet henüz canlı değil)",
        "key_innovation": "zk-SNARKs entegreli privacy özellikleri"
    },
    "camp_network": {
        "mention": "@campnetwork", 
        "focus": "modüler blockchain yaklaşımı", 
        "specialty": "özelleştirilebilir execution layer ile öne çıkan modüler mimari",
        "trends": ["modüler blockchain çözümleri", "özelleştirilebilir execution layer", "validator ağı büyümesi", "developer tooling"],
        "price_action": "yaklaşan token dağıtım programı",
        "ecosystem": "Cosmos SDK tabanlı modüler blockchain",
        "personality": "kimlik ve sosyal odaklı",
        "token_status": "pre_token",
        "tech_detail": "Modüler blockchain yaklaşımıyla dört temel bileşen: Özelleştirilebilir execution layer, paylaşılan güvenlik modeli, cross-chain mesajlaşma protokolü, developer dostu SDK. Cosmos SDK tabanlı yapısıyla mevcut araçlarla uyumluluğu sağlıyor.",
        "validator_network": "Testnet sürecinde 150+ validator katılımı",
        "development_focus": "Developer dostu SDK",
        "development_stage": "testnet aşamasında (katılım devam ediyor)",
        "key_innovation": "Özelleştirilebilir execution layer"
    },
    "virtuals": {
        "mention": "@virtuals_io", 
        "focus": "AI agent pazarı", 
        "specialty": "yapay zeka ajanları tokenlaştırıp ekonomi oluşturan platform",
        "trends": ["AI ajan tokenları ilgi görüyor", "yapay zeka tokenlaştırması", "GameFi AI entegrasyonları", "AI agent pazarı büyüyor"],
        "price_action": "AI token sektöründe performans gösteriyor",
        "ecosystem": "AI agent ekonomisi ve pazaryeri",
        "personality": "AI ve tokenizasyon odaklı",
        "token_status": "active",
        "tech_detail": "AI agent pazarı: Farklı yeteneklerdeki yapay zeka ajanları tokenlaştırılıp pazarda işlem görüyor. Agent'lar sahipleri adına otomatik görevler yapıyor, kazandıkları gelir token ekonomisinde paylaşılıyor. Her agent'ın kendine özgü becerileri ve performans geçmişi var.",
        "development_update": "Yeni AI agent kategorileri ve daha fazla platform entegrasyonu geliyor",
        "performance_data": "1000+ aktif AI agent token'ı piyasada",
        "development_stage": "aktif proje (marketplace canlıda)",
        "key_innovation": "AI agent tokenizasyonu ve otomatik gelir paylaşımı"
    },
    "somnia": {
        "mention": "@somnia_network", 
        "focus": "virtual object standardı", 
        "specialty": "metaverse'ler arası varlık taşınabilirliği sorunu çözen teknik yaklaşım",
        "trends": ["gaming blockchain alanında çalışmalar", "metaverse interoperabilite", "virtual object standardı", "cross-platform gaming"],
        "price_action": "mainnet öncesi, hype artıyor",
        "ecosystem": "Metaverse ve gaming altyapısı",
        "personality": "performans ve gaming odaklı",
        "token_status": "pre_token",
        "tech_detail": "Virtual object standardı, Unity tabanlı oyunda kazanılan eşyanın Polygon tabanlı metaverse'de, Unreal Engine'le geliştirilmiş sosyal platformda kullanılabilmesini sağlıyor. Universal rendering sistemi ve metadata şeması kullanıyor.",
        "use_cases": "Çoklu platform oyun eşyası transferi",
        "technical_stack": "Unity, Unreal Engine uyumluluğu",
        "development_stage": "geliştirme aşamasında (mainnet öncesi)",
        "key_innovation": "Universal rendering sistemi"
    },
    "union": {
        "mention": "@union_build", 
        "focus": "zk interoperabilite", 
        "specialty": "sıfır bilgi köprüleri",
        "trends": ["zk köprü teknolojisinde ilerlemeler", "çapraz zincir güvenlik çözümleri", "interoperabilite araştırmaları", "IBC protokolü geliştirmeleri"],
        "price_action": "airdrop beklentisi çok yüksek",
        "ecosystem": "Çapraz zincir altyapısı",
        "personality": "teknik ve köprü odaklı",
        "token_status": "pre_token",
        "tech_detail": "Zero-knowledge köprüler: Blockchain'ler arası geçişlerde zk-proof kullanarak güvenliği artırır. Klasik köprülerdeki trust assumption'ları ortadan kaldırır, matematiksel olarak kanıtlanabilir güvenlik sağlar.",
        "development_stage": "geliştirme aşamasında (airdrop öncesi)"
    },
    "mitosis": {
        "mention": "@mitosis", 
        "focus": "likidite fragmentasyonu çözümü", 
        "specialty": "DeFi alanında yeni standart oluşturmayı hedefleyen likidite protokolü",
        "trends": ["likidite protokolü geliştirmeleri", "otomatik pazar yapıcılığı", "çapraz zincir likidite", "DeFi yield optimizasyonu"],
        "price_action": "TVL hızla büyüyor, governance aktivitesi artıyor",
        "ecosystem": "Yeni nesil DeFi protokolü",
        "personality": "DeFi ve yield odaklı",
        "token_status": "pre_token",
        "tech_detail": "Likidite fragmentasyonu sorununa üç yenilikçi mekanizma: Dinamik arbitraj botları, çoklu zincir slippage optimizasyonu ve akıllı likidite routing algoritmaları. Ethereum ve Layer 2'ler arasında %40'a varan gas tasarrufu sağlıyor.",
        "performance_data": "%40'a varan gas tasarrufu",
        "governance_update": "Ekosistem fonlarının %15'i developer ödüllerine ayrıldı",
        "development_stage": "beta aşamasında (TVL büyüyor)",
        "key_innovation": "Dinamik arbitraj botları ve slippage optimizasyonu"
    },
    "pharos": {
        "mention": "@pharosnetwork",
        "focus": "Layer-1 blockchain altyapısı",
        "specialty": "EVM uyumlu hızlı blockchain ile DeFi ve RWA odaklı ekosistem",
        "trends": ["Layer-1 rekabeti artıyor", "EVM uyumluluk standart", "RWA tokenization büyüyor", "airdrop programları"],
        "price_action": "testnet canlı, airdrop programı aktif",
        "ecosystem": "DeFi, RWA ve DePIN uygulamaları",
        "personality": "performans ve RWA odaklı",
        "token_status": "pre_token",
        "tech_detail": "EVM uyumlu Layer-1 blockchain: 1 saniye finality süresi, düşük depolama maliyetleri, AsyncBFT consensus algoritması. Ethereum geliştiricileri mevcut araçlarını kullanabilirken yüksek performans ve güvenlik sağlıyor.",
        "development_update": "Testnet incentive programı devam ediyor",
        "performance_data": "1 saniye finality süresi",
        "development_stage": "testnet aşamasında (airdrop aktif)",
        "key_innovation": "AsyncBFT consensus ve unified account sistemi"
    },
    "zama": {
        "mention": "@zama_fhe",
        "focus": "Fully Homomorphic Encryption (FHE)",
        "specialty": "blockchain üzerinde tam gizlilik sağlayan FHE teknolojisi",
        "trends": ["privacy teknolojileri öne çıkıyor", "FHE adoption artıyor", "confidential smart contracts", "private DeFi"],
        "price_action": "teknoloji geliştirme aşamasında, yatırımcı ilgisi yüksek",
        "ecosystem": "Privacy-focused blockchain protokolü",
        "personality": "gizlilik ve kripto odaklı",
        "token_status": "pre_token",
        "tech_detail": "Fully Homomorphic Encryption: Verileri decrypt etmeden işleme olanak sağlar. fhEVM ile Solidity'de private smart contract yazılabiliyor. Encrypted state updates, threshold FHE ile validator güvenliği.",
        "development_update": "fhEVM v0.7 testnet canlı",
        "performance_data": "~5 TPS şu an, FHE ASIC'ler ile 1000+ TPS hedef",
        "development_stage": "testnet aşamasında (confidential blockchain protocol)",
        "key_innovation": "FHE ile tam gizli smart contract'lar"
    }
}

# Tweet uzunluk kategorileri - THREAD DESTEĞİ İLE
TWEET_LENGTHS = {
    "short": {"weight": 35, "min": 200, "max": 350, "style": "punch"},      # %35 - Kısa & Punch
    "medium": {"weight": 45, "min": 350, "max": 500, "style": "normal"},    # %45 - Normal 
    "long": {"weight": 15, "min": 500, "max": 650, "style": "analysis"},    # %15 - Uzun analiz
    "thread": {"weight": 5, "min": 2000, "max": 3000, "style": "thread"}    # %5 - Thread (2-3k karakter)
}

# TWEET TİPLERİ - DOĞAL VE ÇEŞİTLİ İNSAN GİBİ
TWEET_TYPES = {
    "tech_deep": {
        "weight": 20,
        "style": "Teknoloji odaklı derinlemesine açıklama",
        "tone": "Teknik ama anlaşılır, bilgi paylaşan"
    },
    "casual_discovery": {
        "weight": 18,
        "style": "Rastgele keşfetmiş gibi doğal",
        "tone": "Meraklı, keşfeden, samimi"
    },
    "daily_metaphor": {
        "weight": 15,
        "style": "Günlük hayat metaforlarıyla teknik açıklama",
        "tone": "Eğlenceli ama öğretici, Türk kültürü referansları"
    },
    "market_perspective": {
        "weight": 12,
        "style": "Piyasa analizi ve görüş",
        "tone": "Analitik ama kişisel görüş"
    },
    "comparison": {
        "weight": 12,
        "style": "Başka projelerle karşılaştırma", 
        "tone": "Karşılaştırmalı, objektif"
    },
    "quote_commentary": {
        "weight": 12,
        "style": "Proje tweet'ine yorum yapma",
        "tone": "Yorumlayıcı, kişisel görüş ekleyen"
    },
    "crypto_meme": {
        "weight": 8,
        "style": "Eğlenceli meme tarzı",
        "tone": "Mizahi ama bilgili, crypto insider"
    },
    "experience_share": {
        "weight": 8,
        "style": "Kişisel deneyim paylaşımı",
        "tone": "Deneyim odaklı, samimi"
    },
    "question_wonder": {
        "weight": 6,
        "style": "Merak ve soru sorma",
        "tone": "Meraklı, düşündürücü"
    },
    "future_prediction": {
        "weight": 4,
        "style": "Gelecek tahmini",
        "tone": "Spekülatif ama mantıklı"
    }
}

# Tweet sistemi - günde 9 tweet sabah 8 gece yarısı arası (Avrupa saati)
last_tweet_time = None
MINIMUM_INTERVAL = 1.8 * 60 * 60  # 1.8 saat (saniye) - günde 9 tweet (16 saat ÷ 9 = 1.8 saat)
DAILY_TWEET_COUNT = 9
TWEET_START_HOUR = 8   # sabah 8 (Avrupa saati)
TWEET_END_HOUR = 24    # gece yarısı (00:00)
current_project_index = 0  # Proje rotasyonu için

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
    
    print(f"🔑 OAuth params: {oauth_params}")
    print(f"📋 Extra params: {params}")
    
    # Tüm parametreleri birleştir (POST body params dahil)
    all_params = {**oauth_params, **params}
    
    # Signature oluştur
    signature = create_oauth_signature(method, url, all_params, api_secret, access_secret)
    oauth_params['oauth_signature'] = signature
    
    print(f"✍️ Generated signature: {signature}")
    
    # Authorization header oluştur
    auth_parts = []
    for key, value in sorted(oauth_params.items()):
        auth_parts.append(f'{key}="{urllib.parse.quote(str(value), safe="")}"')
    
    return f"OAuth {', '.join(auth_parts)}"

def search_twitter_sentiment(project_key):
    """Twitter'da proje hakkında son tweet'leri ara ve sentiment analizi yap"""
    try:
        project = projects[project_key]
        
        # Bearer token ile Twitter API v2 search
        url = "https://api.twitter.com/2/tweets/search/recent"
        
        # Search query oluştur - proje ismi ve mention kullan
        project_name = project['mention'].replace('@', '')
        query_parts = [f'"{project_name}"', f'"{project_key}"']
        
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

def find_recent_project_tweet(project_key):
    """Proje hesabından son tweet'leri bul quote tweet için"""
    try:
        project = projects[project_key]
        username = project['mention'].replace('@', '')
        
        # Twitter API v2 kullanarak proje hesabının son tweet'lerini al
        url = f"https://api.twitter.com/2/tweets/search/recent"
        
        params = {
            'query': f'from:{username} -is:retweet',
            'max_results': 10,
            'tweet.fields': 'created_at,public_metrics,text',
            'sort_order': 'recency'
        }
        
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            tweets = data.get('data', [])
            
            if tweets:
                # En uygun tweet'i seç (son 24 saat içinde, announcement/update gibi)
                for tweet in tweets:
                    text = tweet['text'].lower()
                    
                    # Announcement/update tweet'lerini öncelikle al
                    announcement_keywords = ['launch', 'announce', 'update', 'release', 'new', 'coming', 'excited', 'partnership']
                    if any(keyword in text for keyword in announcement_keywords):
                        return {
                            'id': tweet['id'],
                            'text': tweet['text'][:100] + "..." if len(tweet['text']) > 100 else tweet['text'],
                            'username': username
                        }
                
                # Announcement yoksa en son tweet'i al
                return {
                    'id': tweets[0]['id'],
                    'text': tweets[0]['text'][:100] + "..." if len(tweets[0]['text']) > 100 else tweets[0]['text'],
                    'username': username
                }
        
        print(f"🔍 {username} için son tweet bulunamadı")
        return None
        
    except Exception as e:
        print(f"🔍 Proje tweet arama hatası: {e}")
        return None

def get_time_based_tone():
    """Saate göre tweet tonu belirle - Özellik #12"""
    current_hour = datetime.now().hour
    
    if 6 <= current_hour < 12:
        return {
            "tone": "energetic_morning",
            "modifier": "Sabah enerjisi ile, pozitif ve motivasyonel"
        }
    elif 12 <= current_hour < 17:
        return {
            "tone": "analytical_noon", 
            "modifier": "Öğle saatleri analitik yaklaşım, daha detaylı"
        }
    elif 17 <= current_hour < 22:
        return {
            "tone": "casual_evening",
            "modifier": "Akşam rahat atmosfer, daha samimi ve paylaşımcı"
        }
    else:
        return {
            "tone": "chill_night",
            "modifier": "Gece sakinliği, düşünceli ve derinlemesine"
        }

def choose_tweet_length():
    """Ağırlıklı rastgele tweet uzunluğu seç - thread desteği ile"""
    rand = random.randint(1, 100)
    if rand <= 35:
        return TWEET_LENGTHS["short"]
    elif rand <= 80:  # 35 + 45
        return TWEET_LENGTHS["medium"] 
    elif rand <= 95:  # 35 + 45 + 15
        return TWEET_LENGTHS["long"]
    else:  # 5% - Thread
        return TWEET_LENGTHS["thread"]

def choose_tweet_type():
    """Ağırlıklı rastgele tweet tipi seç - doğal çeşitlilik için"""
    total_weight = sum(t["weight"] for t in TWEET_TYPES.values())
    rand = random.randint(1, total_weight)
    
    current_weight = 0
    for type_name, type_data in TWEET_TYPES.items():
        current_weight += type_data["weight"]
        if rand <= current_weight:
            return type_name, type_data
    
    # Fallback
    return "casual_discovery", TWEET_TYPES["casual_discovery"]

def get_enhanced_ai_tweet(project_key, sentiment_data, target_length, tweet_type, type_config):
    """Enhanced AI tweet - önceden seçilmiş tweet tipi ile DOĞAL İNSAN GİBİ"""
    import random
    project = projects[project_key]
    length_config = target_length
    
    # Saate göre ton ayarla (Özellik #12)
    time_tone = get_time_based_tone()
    
    # Quote tweet için proje tweet'i bul
    quoted_tweet = None
    if tweet_type == "quote_commentary":
        quoted_tweet = find_recent_project_tweet(project_key)
        if not quoted_tweet:
            # Quote tweet bulunamazsa fallback tip seç
            tweet_type = random.choice(["tech_deep", "casual_discovery", "market_perspective"])
    
    # Gelişmiş İçerik Stratejisi - Profesyonel Prompt Sistemi
    
    # Başlangıç hook'ları
    hooks = [
        "Son dönemde dikkat çeken",
        "Yakından incelenmesi gereken", 
        "Ekosistem için önemli bir adım olan",
        "Teknoloji alanında öne çıkan",
        "Geliştiriciler tarafından izlenen"
    ]
    
    selected_hook = random.choice(hooks)
    
    # Proje ismini hazırla (underscore'ları boşluğa çevir)
    clean_project_name = project['mention'].replace('@', '').replace('_', ' ').title()
    
    type_prompts = {
        "tech_deep": f"""{clean_project_name} hakkında {"uzun makale tarzı" if length_config['style'] == 'thread' else f"{length_config['min']}-{length_config['max']} karakter"} tweet at. Crypto insanı gibi konuş.

PROJE: {project['focus']} - {project['specialty']}
TEKNİK: {project.get('tech_detail', '')}
İNOVASYON: {project.get('key_innovation', '')}
DURUM: {project.get('development_stage', project['price_action'])}

{"UZUN MAKALE MODU (2000-3000 karakter):" if length_config['style'] == 'thread' else ""}

ZAMAN TONU: {time_tone['modifier']}

YAPMA BUNLARI:
- "ekosistem için önemli", "göz önünde bulundurulmalı" gibi AI dili
- "derinlemesine analiz", "profesyonel yaklaşım" gibi buzzword'ler  
{"- Çok teknik jargon, ama detaylı açıklama yap" if length_config['style'] == 'thread' else "- Çok uzun cümleler"}

YAP BUNLARI:
- "lan bu teknoloji bayağı cool", "gerçekten işe yarayabilir"  
- "henüz erken ama potansiyeli var", "şu kısmı çok zekice yapılmış"
- Samimi, arkadaşça ton - sanki bir arkadaşına anlatıyorsun
{f"- Makale gibi yapılandır: Giriş-Teknik detay-Kullanım alanları-Sonuç" if length_config['style'] == 'thread' else "- Kısa, net cümleler"}
{f"- Her paragraf ayrı bir konuya odaklan" if length_config['style'] == 'thread' else ""}

TON: {time_tone['tone']} + teknik bilgili crypto insanı

{"UZUN MAKALE YAPISI (ÖRNEK):" if length_config['style'] == 'thread' else "ÖRNEKLER:"}
{f'''
Giriş paragrafı - Projeyi tanıt ve neden ilginç olduğunu açıkla

Teknik paragraf - Teknolojinin nasıl çalıştığını samimi dille anlat  

Kullanım paragrafı - Gerçek hayatta nerelerde kullanılacağını söyle

Karşılaştırma paragrafı - Diğer projelerle kıyasla

Sonuç paragrafı - Gelecek ve potansiyel hakkında düşünceler''' if length_config['style'] == 'thread' else '''
"X projesinin şu özelliği gerçekten akıllıca. Böyle yaklaşımları seviyorum..."
"Araştırırken fark ettim, X'in teknolojisi diğerlerinden farklı..."
"X'in yaklaşımı ilginç. Şu sorunu çözmesi hoşuma gitti..."'''}

Sadece tweet yaz, açıklama yapma.""",

        "casual_discovery": f"""{clean_project_name} hakkında {length_config['min']}-{length_config['max']} karakter casual tweet at.

DURUM: {project.get('development_stage', project['price_action'])}
ÖZELLIK: {project['specialty']}

STIL: Yeni keşfetmiş bir crypto meraklısı gibi konuş

YAPMA:
- "dikkatimi çekti", "araştırırken karşıma çıktı" klişe başlangıçlar
- "incelemesi gereken", "önemli bir adım" resmi dil

YAP:  
- "bugün {clean_project_name} ile tanıştım, ilginç..."
- "rastgele {clean_project_name} gördüm, bayağı cool..."
- "daha önce duymamıştım ama {clean_project_name}..."
- "hmm {clean_project_name} ne lan diye baktım..."

TON: Samimi, meraklı, biraz şaşırmış ama ilgili
ÖRNEKLER:
"Bugün ilk defa X diye bir şey duydum, ne olduğuna baktım..."
"X'i hiç bilmiyordum ama şu özelliği bayağı mantıklı geldi..."
"Rastgele X'e denk geldim, henüz yeni galiba ama..."

Sadece tweet yaz.""",

        "market_perspective": f"""{clean_project_name} piyasa durumu hakkında {length_config['min']}-{length_config['max']} karakter tweet at.

DURUM: {project['token_status']} - {project['price_action']}
SEKTÖR: {project['ecosystem']}

YAPMA:
- "piyasa perspektifi", "analiz odakları", "yatırım timing'i" 
- "volatilite riski göz önünde bulundurulmalı" AI dili

YAP:
- "şu an {clean_project_name} için iyi zamanlama olabilir..."
- "token durumu fena değil, ama..."
- "sektör genel hareketli, {clean_project_name} da..."
- "henüz erken ama momentum var gibi..."

TON: Piyasa takip eden ama gösterişsiz biri
ÖRNEKLER:
"X'in token durumu fena değil, sektör de hareketli son zamanlarda..."
"X henüz erken sayılır ama momentum yakalamış gibi görünüyor..."
"Bu dönemde X'e bakmak mantıklı olabilir, çünkü..."

Risk uyarısı yapma, sadede gel. Tweet yaz.""",

        "comparison": f"""{clean_project_name} vs diğer projeler hakkında {length_config['min']}-{length_config['max']} karakter tweet at.

PROJE FARKLIĞI: {project.get('key_innovation', project['specialty'])}
ALAN: {project['focus']}

YAPMA:
- "sektörel analiz", "karşılaştırmalı değerlendirme" resmi dil
- "diğer çözümlerden üstün" abartı

YAP:
- "{clean_project_name} diğerlerinden farklı çünkü..."
- "bu alanda genelde şöyle oluyor ama {clean_project_name}..."
- "klasik yöntemlere kıyasla {clean_project_name}..."
- "mesela diğer projeler şöyle yapıyor, ama bu..."

TON: Objektif ama meraklı karşılaştırma yapan biri
ÖRNEKLER:
"Bu alanda genelde şöyle çözümler görüyoruz ama X farklı bir yaklaşım izliyor..."
"X'in en ilginç yanı, klasik yöntemlerden ayrılışı..."
"Diğer projeler genelde şöyle yaparken X..."

Sadece tweet yaz.""",

        "daily_metaphor": f"""{clean_project_name} hakkında {"uzun makale tarzı" if length_config['style'] == 'thread' else f"{length_config['min']}-{length_config['max']} karakter"} tweet at. Günlük hayat metaforlarıyla teknik konuları açıkla.

PROJE: {project['focus']} - {project['specialty']}
TEKNİK: {project.get('tech_detail', '')}
İNOVASYON: {project.get('key_innovation', '')}

{"UZUN MAKALE MODU - Günlük hayat metaforlarıyla detaylı açıklama:" if length_config['style'] == 'thread' else ""}

STIL: Verdiğim örneklerdeki gibi günlük hayat metaforları kullan

ÖRNEK STİL (AYNEN BÖYLE YAP):
1. "Anoma, "intent" (niyet) odaklı yapısıyla geleneksel zincir üstü işlem modelini değiştiriyor. Kullanıcılar ne yapmak istediklerini tanımlar, nasıl yapılacağı çözücülere bırakılır..."

2. "Anoma'da olay şöyle: "Evlenmek istiyorum" diye intent atıyorsun. Düğün salonu, takıcı, nikâh memuru... bunları sen ayarlamıyorsun. Çözücüler devreye giriyor, uygun adayla eşleşiyorsun, evlilik tek işlemde onchain oluyor 😄 Ne düğün masrafı, ne kaynana baskısı!"

YAPMA:
- Sıradan teknik açıklama
- Çok ciddi ton  
- Yabancı referanslar

YAP BUNLARI:
- Türk günlük hayatından metaforlar (evlilik, aile, akrabalar, komşular, çarşı-pazar)
- Türk kültürü referansları (TV programları, gelenekler, durumlar)
- Eğlenceli ama öğretici açıklamalar
- "şöyle:" "olay şu:" gibi samimi başlangıçlar
- Emoji kullan (😄 gibi)
{f"- Her paragrafta farklı günlük hayat metaforu kullan" if length_config['style'] == 'thread' else ""}
{f"- Uzun hikaye gibi anlat, karakterler oluştur" if length_config['style'] == 'thread' else ""}

TON: Eğlenceli öğretmen, karmaşık şeyleri basit metaforlarla anlatan

TÜRK KÜLTÜRÜ REFERANSLARİ:
- "Kısmetse Olur", "Gelin Evi", "Kim Milyoner Olmak İster"  
- "kaynana", "enişte", "baldız", "görümce"
- "muhtarlık", "kahvehane", "bakkal", "esnaf"
- "bayram", "düğün", "nişan", "kına gecesi"

GÜNLÜK HAYAT METAFORLARİ:
- Evlilik işlemleri (nişan, düğün, nikah)
- Aile ilişkileri (kaynana-gelin, enişte-baldız)
- Alışveriş (pazarlık, bargain)
- Komşuluk (dedikodu, yardımlaşma)

{f'''UZUN MAKALE YAPISI (Metaforlarla):
Giriş - Projeyi tanıdık bir durum/kişiyle karşılaştır
Teknik kısım - Karmaşık teknolojiyikomşu-akraba ilişkileriyle açıkla  
Avantajlar - "Ne kazanıyoruz" sorusunu günlük hayat örnekleriyle
Rakipler - Diğer çözümlerle kıyaslama (başka ev/dükkanlarlayarışır gibi)
Sonuç - Gelecekle ilgili eğlenceli tahmin''' if length_config['style'] == 'thread' else ""}

Sadece tweet yaz, böyle eğlenceli metaforlarla açıkla!""",

        "quote_commentary": f"""ÖZEL: Bu tweet quote tweet olacak. {clean_project_name} projesinin resmi hesabından bir tweet'e yorum yapıyormuş gibi {length_config['min']}-{length_config['max']} karakter tweet yaz.

QUOTED TWEET: "{quoted_tweet['text'] if quoted_tweet else 'Proje güncellemesi paylaştı'}"
PROJE FOCUS: {project['focus']}
ÖZELLIK: {project['specialty']}

ZAMAN TONU: {time_tone['modifier']}

SENARYO: {clean_project_name} resmi hesabı bir güncelleme/duyuru paylaştı ve sen yorum yapıyorsun

YAPMA:
- "quote tweet yazdım", "şu tweet'e yorum" meta referans
- Çok formal yorum

YAP:
- "bu güzel bir gelişme, çünkü..."
- "tam da beklediğim haber, {clean_project_name}..."
- "ilginç yaklaşım, özellikle şu kısım..."
- "bu {clean_project_name} için mantıklı bir adım..."

TON: Projeyi takip eden, bilgili ama samimi biri + {time_tone['tone']}
ÖRNEKLER:
"Bu güzel bir gelişme, özellikle şu özellik çok mantıklı..."
"Tam da beklediğim türden bir güncelleme..."
"X ekibi gerçekten düşünmüş, bu yaklaşım ilginç..."

Quote tweet yapıyormuş gibi tweet yaz.""",

        "crypto_meme": f"""{clean_project_name} hakkında {length_config['min']}-{length_config['max']} karakter eğlenceli meme tweet at.

PROJE: {project['focus']}
İNOVASYON: {project.get('key_innovation', project['specialty'])}
PROBLEM: {project.get('tech_detail', '')}

ZAMAN TONU: {time_tone['modifier']}

MEME FORMAT SEÇENEKLERİ:
1. "Nobody: 
   {clean_project_name}: [özelliği açıklama]"

2. "Me trying to understand blockchains
   {clean_project_name}: [basit açıklama]
   Me: wait, that actually makes sense"

3. "Other projects: [karmaşık yaklaşım]
   {clean_project_name}: [basit yaklaşım]
   Crypto Twitter: 👁️👄👁️"

4. "Dev 1: How do we make this work?
   Dev 2: Just add more complexity
   {clean_project_name} team: Actually..."

5. "Everyone: blockchain is hard
   {clean_project_name}: what if we just [basit çözüm]
   Users: why didn't we think of that"

YAPMA:
- Çok teknik jargon
- Anlaşılmaz insider reference'lar
- Projeyi kötüleme
- Fazla karmaşık format

YAP:
- Format'lardan birini seç ve o şekilde yaz
- Proje özelliğini komik şekilde vurgula
- Basit, anlaşılır crypto mizah
- Community'nin anlayacağı referanslar

TON: {time_tone['tone']} + crypto meme lord

ÖRNEK OUTPUT:
"Nobody:

Anoma: what if users just describe what they want and we figure out the rest automatically

Blockchain Twitter: 🤯"

Sadece tweet yaz, format seç ve uygula.""",

        "experience_share": f"""{clean_project_name} deneyimi hakkında {length_config['min']}-{length_config['max']} karakter tweet at.

DURUM: {project.get('development_stage', 'geliştirme aşaması')}
NE VAR: {project['specialty']}

ÖNEMLİ: GERÇEK duruma uygun yaz!
- Eğer "geliştirme" -> araştırma/takip deneyimi
- Eğer "testnet" -> test deneyimi  
- Eğer "mainnet" -> kullanım deneyimi
- OLMAYAN ŞEYİ DENEDİM DEME!

YAPMA:
- "deneyim paylaşımı", "kişisel değerlendirmem" formal dil
- Olmayan şeyleri kullandım iddiası

YAP:
- "bir süredir {clean_project_name} takip ediyorum..."
- "{clean_project_name} hakkında araştırma yaparken..."
- "şu ana kadar {clean_project_name} ile ilgili gözlemim..."

TON: Samimi, deneyimli ama abartısız
ÖRNEKLER:
"Bir süredir X'i takip ediyorum, gelişmeler fena değil..."
"X'le ilgili araştırma yaparken şunu fark ettim..."
"Şu ana kadar X hakkında edindiğim izlenim..."

Tweet yaz.""",

        "question_wonder": f"""{clean_project_name} hakkında merak ettiğin şeyler - {length_config['min']}-{length_config['max']} karakter tweet.

TEKNOLOJI: {project['focus']}
ÖZELLIK: {project['specialty']}

YAPMA:
- "merak ettiğim konular", "düşündürücü sorular" klişe
- Çok teknik sorular

YAP:
- "acaba {clean_project_name} gerçekten..."
- "merak ediyorum, {clean_project_name}..."
- "{clean_project_name} nasıl çalışıyor ki?"
- "şu kısmını anlayamadım..."

TON: Samimi merak, soru soran arkadaş havası
ÖRNEKLER:
"Acaba X gerçekten bu sorunu çözebilir mi?"
"X'in şu özelliği nasıl çalışıyor, merak ediyorum..."
"X hakkında şunu anlamadım..."

Sadece tweet yaz.""",

        "future_prediction": f"""{clean_project_name} gelecek tahminleri - {length_config['min']}-{length_config['max']} karakter tweet.

ALAN: {project['focus']}
İNOVASYON: {project.get('key_innovation', project['specialty'])}

YAPMA:
- "vizyon odaklı analiz", "öngörü alanları" jargon
- "2025'te devrim yaratacak" abartı

YAP:
- "bence {clean_project_name} ilerleyen zamanlarda..."
- "önümüzdeki dönemde {clean_project_name}..."
- "eğer bu trend devam ederse {clean_project_name}..."
- "gelecekte böyle projeler..."

TON: Spekülatif ama mantıklı tahmin
ÖRNEKLER:
"Bence X önümüzdeki yıl daha çok konuşulur..."
"Eğer bu trend devam ederse X için iyi olabilir..."
"Gelecekte böyle projeler daha önemli hale gelecek..."

Tweet yaz."""
    }
    
    prompt = type_prompts.get(tweet_type, type_prompts["casual_discovery"])
    
    # ChatGPT API call
    headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
    
    # Uzun tweet'ler için daha fazla token
    max_tokens_value = 1500 if length_config['style'] == 'thread' else 500
    
    system_prompt = f"""Sen crypto takip eden samimi bir insansın. Twitter'da doğal konuşursun.

KURAL:
- {length_config['min']}-{length_config['max']} karakter tweet yaz
- {clean_project_name} ismini doğal şekilde kullan
- @ işareti, hashtag kullanma
- Samimi, arkadaşça konuş - sanki bir arkadaşına anlatıyorsun

İSTEDİĞİM TON: Crypto meraklısı, gerçek insan, abartısız"""

    if length_config['style'] == 'thread':
        system_prompt += f"""

ÖZEL: Bu uzun makale tarzı tweet (2000-3000 karakter)
- Detaylı analiz yap, birden fazla paragraf kullan
- Teknik konuları derinlemesine açıkla
- Twitter Blue uzun tweet formatında
- Makale gibi yapılandır ama samimi tondan çıkma
- Giriş-gelişme-sonuç yapısı kullan"""
    else:
        system_prompt += f"""

ÖRNEK İYİ CÜMLELER:
"X'in şu özelliği bayağı mantıklı geldi"
"henüz erken ama ilginç bir yaklaşım"  
"bu alanda böyle çözümler görmeye alıştık ama X farklı"

Sadece tweet yaz."""

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens_value,
        "temperature": 1.1
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
            
            # @ ile başlarsa düzelt (ana timeline'da gözükmez yoksa) + @ mention'ları temizle
            if tweet.startswith('@'):
                # @mention'ı bul ve tweet'i yeniden düzenle
                parts = tweet.split(' ', 1)
                if len(parts) > 1:
                    mention = parts[0]
                    rest = parts[1]
                    # @ mention'ını çıkar, proje ismini al
                    project_name = mention.replace('@', '').replace('_', ' ').title()
                    tweet = f"{project_name} {rest}"
                    print(f"🔧 @ ile başlıyordu, düzeltildi: {tweet}")
            
            # Tüm @ mention'larını proje ismiyle değiştir ve gereksiz kelimeleri temizle
            import re
            for project_key, project_data in projects.items():
                mention = project_data['mention']
                project_name = mention.replace('@', '').replace('_', ' ').title()
                # @ mention ve temiz isim olmayan varyasyonları da değiştir
                variations = [
                    mention,  # @campnetworkxyz
                    mention.replace('@', ''),  # campnetworkxyz
                    mention.replace('@', '').lower(),  # campnetworkxyz
                    mention.replace('@', '').capitalize(),  # Campnetworkxyz
                    mention.replace('@', '').upper()  # CAMPNETWORKXYZ
                ]
                for var in variations:
                    tweet = tweet.replace(var, project_name)
            
            # "şu, ya, nasıl bence" gibi gereksiz kelimeleri temizle
            unwanted_phrases = [
                "şu ", "ya ", "nasıl bence", "bence nasıl", 
                "nasıl ya", "ya nasıl", "şu proje", "bu proje"
            ]
            for phrase in unwanted_phrases:
                tweet = tweet.replace(phrase, "")
            
            # Çoklu boşlukları temizle ve düzelt
            tweet = re.sub(r'\s+', ' ', tweet).strip()
            
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
            # Fallback mekanizması kaldırıldı; None döndür
            return None
            
    except Exception as e:
        print(f"❌ AI request exception: {e}")
        print(f"❌ Exception type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        # Fallback mekanizması kaldırıldı
        return None

# retry_chatgpt fonksiyonu kaldırıldı - artık fallback yok

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

def send_tweet(content, quoted_tweet_id=None):
    """Tweet gönder - Rate limiting ile (Quote tweet desteği)"""
    global last_tweet_time
    
    # Rate limiting kontrolü
    current_time = time.time()
    if last_tweet_time:
        time_since_last = current_time - last_tweet_time
        if time_since_last < MINIMUM_INTERVAL:
            wait_time = MINIMUM_INTERVAL - time_since_last
            print(f"⏳ Rate limiting: {wait_time/60:.1f} dakika beklemek gerekiyor (2.5 saat kural)...")
            return False
    
    url = "https://api.twitter.com/2/tweets"
    
    # OAuth 1.0a kullan (POST body signature'a dahil edilmez)
    auth_header = create_oauth_header("POST", url)
    headers = {
        "Authorization": auth_header, 
        "Content-Type": "application/json"
    }
    
    # Tweet data hazırla
    data = {"text": content}
    
    # Quote tweet ise quoted_tweet_id ekle
    if quoted_tweet_id:
        data["quote_tweet_id"] = quoted_tweet_id
        print(f"💬 Quote tweet gönderiliyor: {quoted_tweet_id}")
    
    print(f"🔐 Auth Header: {auth_header[:50]}...")
    print(f"📤 Tweet Data: {data}")
    print(f"🌐 Request URL: {url}")
    print(f"📡 Request Headers: {headers}")
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📄 Response Text: {response.text}")
    print(f"📋 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 201:
        result = response.json()
        tweet_id = result['data']['id']
        last_tweet_time = current_time  # Başarılı tweet sonrası zamanı güncelle
        print(f"✅ Tweet gönderildi!")
        print(f"📝 İçerik: {content}")
        print(f"🔗 Tweet ID: {tweet_id}")
        if quoted_tweet_id:
            print(f"💬 Quote Tweet ID: {quoted_tweet_id}")
        print(f"📊 Uzunluk: {len(content)} karakter")
        return True
    elif response.status_code == 429:
        print(f"⚠️ Twitter API rate limit! 2.5 saat bekliyorum...")
        print("🔄 Bot otomatik olarak bekleyecek ve daha sonra dener")
        return False
    else:
        print(f"❌ Tweet gönderme hatası: {response.text}")
        return False

def get_recent_tweets():
    """Kendi son tweet'leri oku - hangi projelerden hangi açılarla bahsetmiş kontrol et"""
    try:
        url = "https://api.twitter.com/2/users/me/tweets"
        params = {
            'max_results': 20,  # Son 20 tweet
            'tweet.fields': 'created_at,text'
        }
        
        # OAuth 1.0a için GET parametreleri signature'a dahil edilmeli
        auth_header = create_oauth_header("GET", url, params)
        headers = {"Authorization": auth_header}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            tweets = data.get('data', [])
            
            project_tweet_types = {}  # {project_key: [tweet_types]}
            for tweet in tweets:
                text = tweet['text'].lower()
                
                # Hangi projeleri mention etmiş kontrol et
                for project_key, project_data in projects.items():
                    mention = project_data['mention'].lower()
                    if mention in text:
                        # Tweet tipini tahmin et (basit anahtar kelime analizi)
                        detected_type = detect_tweet_type(text)
                        
                        if project_key not in project_tweet_types:
                            project_tweet_types[project_key] = []
                        project_tweet_types[project_key].append(detected_type)
            
            print(f"📊 Son 20 tweet analizi: {len(tweets)} tweet")
            for project, types in project_tweet_types.items():
                print(f"   🎯 {project}: {types}")
            
            return project_tweet_types
        else:
            print(f"⚠️ Tweet geçmişi okunamadı: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Tweet geçmişi okuma hatası: {e}")
        return {}

def detect_tweet_type(text):
    """Tweet içeriğinden hangi tipte olduğunu tahmin et"""
    # Basit anahtar kelime analizi
    if any(word in text for word in ['nasıl çalışır', 'teknoloji', 'protokol', 'algorithm', 'architecture']):
        return 'tech_deep'
    elif any(word in text for word in ['yeni', 'keşfettim', 'denk geldim', 'ilk defa']):
        return 'casual_discovery' 
    elif any(word in text for word in ['fiyat', 'airdrop', 'token', 'yatırım', 'piyasa']):
        return 'market_perspective'
    elif any(word in text for word in ['karşılaştır', 'göre', 'farkı', 'benzer']):
        return 'comparison'
    elif any(word in text for word in ['denedim', 'kullandım', 'testnet', 'deneyim']):
        return 'experience_share'
    elif any(word in text for word in ['acaba', 'merak', 'nasıl', 'neden']):
        return 'question_wonder'
    elif any(word in text for word in ['gelecek', '2025', 'büyük olacak', 'potansiyel']):
        return 'future_prediction'
    else:
        return 'casual_discovery'  # Default

# NEWS MONITORING SİSTEMİ TAMAMEN KALDIRILDI
# Kaldırılan fonksiyonlar:
# - get_crypto_news()
# - calculate_news_relevance()
# - get_trending_topics()
# - find_related_project()
# - create_news_based_tweet()
# - create_trend_based_tweet()
# - news/trends/newstweet/trendtweet command'ları

# Haber ve trend fonksiyonları kaldırıldı

def get_tweet_performance(tweet_id):
    """Tweet performansını kontrol et - analytics için"""
    try:
        url = f"https://api.twitter.com/2/tweets/{tweet_id}"
        params = {
            'tweet.fields': 'public_metrics,created_at',
            'expansions': 'author_id'
        }
        
        auth_header = create_oauth_header("GET", url, params)
        headers = {"Authorization": auth_header}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            tweet_data = data.get('data', {})
            metrics = tweet_data.get('public_metrics', {})
            
            performance = {
                'tweet_id': tweet_id,
                'likes': metrics.get('like_count', 0),
                'retweets': metrics.get('retweet_count', 0),
                'replies': metrics.get('reply_count', 0),
                'quotes': metrics.get('quote_count', 0),
                'impressions': metrics.get('impression_count', 0),  # Eğer varsa
                'engagement_rate': 0,
                'check_time': datetime.now().isoformat()
            }
            
            # Basit engagement rate hesapla
            total_engagement = performance['likes'] + performance['retweets'] + performance['replies'] + performance['quotes']
            if performance['impressions'] > 0:
                performance['engagement_rate'] = (total_engagement / performance['impressions']) * 100
            
            return performance
        else:
            print(f"⚠️ Tweet performansı okunamadı: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Tweet analytics hatası: {e}")
        return None

def save_tweet_analytics(tweet_id, content, project_key, tweet_type):
    """Tweet analitiklerini dosyaya kaydet"""
    try:
        analytics_file = "tweet_analytics.json"
        
        # Mevcut dosyayı oku
        try:
            with open(analytics_file, 'r', encoding='utf-8') as f:
                analytics_data = json.load(f)
        except FileNotFoundError:
            analytics_data = {}
        
        # Yeni tweet kaydı
        analytics_data[tweet_id] = {
            'content': content,
            'project': project_key,
            'tweet_type': tweet_type,
            'sent_time': datetime.now().isoformat(),
            'initial_metrics': None,  # İlk kontrol için
            'day_1_metrics': None,    # 24 saat sonra
            'day_7_metrics': None     # 7 gün sonra
        }
        
        # Dosyaya kaydet
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics_data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Tweet analytics kaydedildi: {tweet_id}")
        
    except Exception as e:
        print(f"❌ Analytics kaydetme hatası: {e}")

def check_pending_analytics():
    """Bekleyen tweet analitiklerini kontrol et"""
    try:
        analytics_file = "tweet_analytics.json"
        
        try:
            with open(analytics_file, 'r', encoding='utf-8') as f:
                analytics_data = json.load(f)
        except FileNotFoundError:
            return  # Dosya yoksa yapacak bir şey yok
        
        current_time = datetime.now()
        updated = False
        
        for tweet_id, data in analytics_data.items():
            sent_time = datetime.fromisoformat(data['sent_time'])
            time_diff = current_time - sent_time
            
            # 1 saat sonra ilk kontrol (initial metrics)
            if time_diff.total_seconds() > 3600 and data['initial_metrics'] is None:
                metrics = get_tweet_performance(tweet_id)
                if metrics:
                    data['initial_metrics'] = metrics
                    updated = True
                    print(f"📈 1 saat sonra: {tweet_id} - {metrics['likes']} like, {metrics['retweets']} RT")
            
            # 24 saat sonra kontrol
            if time_diff.total_seconds() > 86400 and data['day_1_metrics'] is None:
                metrics = get_tweet_performance(tweet_id)
                if metrics:
                    data['day_1_metrics'] = metrics
                    updated = True
                    print(f"📈 24 saat sonra: {tweet_id} - {metrics['likes']} like, {metrics['retweets']} RT")
            
            # 7 gün sonra kontrol
            if time_diff.total_seconds() > 604800 and data['day_7_metrics'] is None:
                metrics = get_tweet_performance(tweet_id)
                if metrics:
                    data['day_7_metrics'] = metrics
                    updated = True
                    print(f"📈 7 gün sonra: {tweet_id} - {metrics['likes']} like, {metrics['retweets']} RT")
        
        # Güncellenmiş veriyi kaydet
        if updated:
            with open(analytics_file, 'w', encoding='utf-8') as f:
                json.dump(analytics_data, f, ensure_ascii=False, indent=2)
            print("📊 Analytics güncellendi!")
        
    except Exception as e:
        print(f"❌ Analytics kontrol hatası: {e}")

def create_thread_content(project_key, sentiment_data):
    """Thread (tweet zinciri) içeriği oluştur - uzun analiz için"""
    try:
        project = projects[project_key]
        
        # Thread için özel prompt
        thread_prompt = f"""Sen uzun crypto analizleri yapan bir uzmanısın. {project['mention'].replace('@', '').replace('_', ' ').title()} hakkında 2-3 tweet'lik bir thread (zincir) yazacaksın.

Proje Bilgileri:
- Focus: {project['focus']}
- Specialty: {project['specialty']}
- Tech Detail: {project.get('tech_detail', '')}
- Ecosystem: {project['ecosystem']}

Thread Yapısı:
Tweet 1 (Ana): Projeyi tanıt ve ilgi çek (280-450 karakter)
Tweet 2 (Derinlik): Teknik detaylar ve kullanım (280-450 karakter)  
Tweet 3 (Sonuç): Vizyon ve değerlendirme (280-450 karakter)

Her tweet'i [TWEET1], [TWEET2], [TWEET3] etiketleriyle ayır.

Yazım Kuralları:
- @ işareti kullanma
- "şu, ya, nasıl bence" gibi gereksiz kelimeler kullanma
- Hashtag kullanma
- Her tweet kendi başına anlamlı olmalı
- Proje ismini doğal şekilde geçir
- Akıcı, konuşma diline yakın ama profesyonel

Thread başlığı ile başla."""

        headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": thread_prompt}
            ],
            "max_tokens": 800,
            "temperature": 1.0
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            thread_content = result['choices'][0]['message']['content'].strip()
            
            # Thread'i parse et
            tweets = []
            for i in range(1, 4):
                tag = f"[TWEET{i}]"
                if tag in thread_content:
                    start = thread_content.find(tag) + len(tag)
                    if i < 3:
                        end = thread_content.find(f"[TWEET{i+1}]")
                        tweet_text = thread_content[start:end].strip()
                    else:
                        tweet_text = thread_content[start:].strip()
                    
                    # Tweet'i temizle
                    tweet_text = clean_tweet_text(tweet_text)
                    if tweet_text and len(tweet_text) > 50:  # Çok kısa değilse
                        tweets.append(tweet_text)
            
            if len(tweets) >= 2:
                print(f"🧵 Thread oluşturuldu: {len(tweets)} tweet")
                return tweets
            else:
                print(f"⚠️ Thread parse edilemedi, normal tweet olarak dönülüyor")
                return None
                
        else:
            print(f"❌ Thread AI hatası: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Thread oluşturma hatası: {e}")
        return None

def clean_tweet_text(text):
    """Tweet metnini temizle - @ mention, hashtag vs. sil"""
    import re
    
    # @ mention'ları proje ismiyle değiştir
    for project_key, project_data in projects.items():
        mention = project_data['mention']
        project_name = mention.replace('@', '').replace('_', ' ').title()
        variations = [
            mention,  # @campnetworkxyz
            mention.replace('@', ''),  # campnetworkxyz
            mention.replace('@', '').lower(),  # campnetworkxyz
            mention.replace('@', '').capitalize(),  # Campnetworkxyz
            mention.replace('@', '').upper()  # CAMPNETWORKXYZ
        ]
        for var in variations:
            text = text.replace(var, project_name)
    
    # Hashtag'leri sil
    text = re.sub(r'#\w+', '', text)
    
    # Gereksiz kelimeler
    unwanted_phrases = [
        "şu ", "ya ", "nasıl bence", "bence nasıl", 
        "nasıl ya", "ya nasıl", "şu proje", "bu proje"
    ]
    for phrase in unwanted_phrases:
        text = text.replace(phrase, "")
    
    # Çoklu boşlukları temizle
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def send_thread(tweets):
    """Thread gönder - her tweet'i zincir halinde"""
    try:
        if not tweets or len(tweets) < 2:
            return False
        
        thread_ids = []
        reply_to_id = None
        
        for i, tweet_content in enumerate(tweets):
            print(f"🧵 Thread {i+1}/{len(tweets)}: {tweet_content[:50]}...")
            
            # Tweet data hazırla
            tweet_data = {"text": tweet_content}
            if reply_to_id:
                tweet_data["reply"] = {"in_reply_to_tweet_id": reply_to_id}
            
            # Tweet gönder
            url = "https://api.twitter.com/2/tweets"
            auth_header = create_oauth_header("POST", url)
            headers = {
                "Authorization": auth_header,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=tweet_data)
            
            if response.status_code == 201:
                result = response.json()
                tweet_id = result['data']['id']
                thread_ids.append(tweet_id)
                reply_to_id = tweet_id  # Sonraki tweet bu tweet'e reply olacak
                
                print(f"✅ Thread {i+1} gönderildi: {tweet_id}")
                
                # Thread'ler arası 2 saniye bekle
                if i < len(tweets) - 1:
                    time.sleep(2)
            else:
                print(f"❌ Thread {i+1} hatası: {response.text}")
                return False
        
        print(f"🎉 Thread tamamlandı! {len(thread_ids)} tweet")
        return thread_ids
        
    except Exception as e:
        print(f"❌ Thread gönderme hatası: {e}")
        return False

def check_mentions_and_reply():
    """Mention'ları kontrol et ve otomatik yanıt ver"""
    try:
        # Son mention'ları al
        url = "https://api.twitter.com/2/users/me/mentions"
        params = {
            'max_results': 10,
            'tweet.fields': 'created_at,text,author_id,conversation_id',
            'expansions': 'author_id'
        }
        
        auth_header = create_oauth_header("GET", url, params)
        headers = {"Authorization": auth_header}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            mentions = data.get('data', [])
            users_data = data.get('includes', {}).get('users', [])
            
            # User ID'den username mapping
            user_mapping = {user['id']: user['username'] for user in users_data}
            
            for mention in mentions:
                tweet_id = mention['id']
                text = mention['text'].lower()
                author_id = mention['author_id']
                username = user_mapping.get(author_id, 'unknown')
                
                # Bu mention'a daha önce yanıt verilmiş mi kontrol et
                if check_already_replied(tweet_id):
                    continue
                
                # Basit yanıt logici - crypto sorularına yanıt ver
                reply_content = generate_auto_reply(text, username)
                
                if reply_content:
                    success = send_reply(tweet_id, reply_content)
                    if success:
                        mark_as_replied(tweet_id)
                        print(f"💬 @{username} kullanıcısına otomatik yanıt verildi")
        
        else:
            print(f"⚠️ Mention'lar okunamadı: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Mention kontrol hatası: {e}")

def generate_auto_reply(mention_text, username):
    """Mention'a otomatik yanıt oluştur"""
    try:
        # Basit yanıt kuralları
        crypto_keywords = ['anoma', 'mitosis', 'union', 'virtuals', 'camp', 'somnia', 'pharos', 'zama', 'crypto', 'blockchain', 'defi']
        
        # Crypto ile ilgili mi kontrol et
        if any(keyword in mention_text for keyword in crypto_keywords):
            
            # Proje spesifik sorular
            for project_key, project_data in projects.items():
                if project_key in mention_text or project_data['mention'].replace('@', '') in mention_text:
                    replies = [
                        f"Merhaba! {project_data['mention'].replace('@', '').replace('_', ' ').title()} gerçekten ilginç bir proje. {project_data['focus']} alanında öne çıkıyor.",
                        f"Bu projeyle ilgili detaylı araştırma yapmanı öneririm. {project_data['specialty']} açısından oldukça değerli.",
                        f"Kesinlikle takip etmeye değer bir proje! {project_data['ecosystem']} ekosistemine güzel bir katkı sağlıyor."
                    ]
                    return random.choice(replies)
            
            # Genel crypto yanıtları
            general_replies = [
                "Crypto dünyasında araştırma yapmak gerçekten önemli. DYOR prensibini hiç unutmamak lazım!",
                "Bu konuda daha detaylı araştırma yapmanı öneririm. Projerlerin roadmap'lerini incelemek iyi olur.",
                "Interessant soru! Crypto alanında sürekli yeni gelişmeler oluyor, takip etmek gerekiyor.",
                "Bu tür projeleri araştırırken tokenomics ve team'e bakmayı unutma!"
            ]
            return random.choice(general_replies)
        
        return None  # Crypto ile ilgili değilse yanıt verme
        
    except Exception as e:
        print(f"❌ Auto reply oluşturma hatası: {e}")
        return None

def send_reply(tweet_id, content):
    """Tweet'e yanıt gönder"""
    try:
        url = "https://api.twitter.com/2/tweets"
        tweet_data = {
            "text": content,
            "reply": {"in_reply_to_tweet_id": tweet_id}
        }
        
        auth_header = create_oauth_header("POST", url)
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=tweet_data)
        
        if response.status_code == 201:
            print(f"✅ Yanıt gönderildi: {content[:50]}...")
            return True
        else:
            print(f"❌ Yanıt gönderme hatası: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Reply gönderme hatası: {e}")
        return False

def check_already_replied(tweet_id):
    """Bu tweet'e daha önce yanıt verilmiş mi kontrol et"""
    try:
        replies_file = "replied_tweets.json"
        
        try:
            with open(replies_file, 'r', encoding='utf-8') as f:
                replied_data = json.load(f)
        except FileNotFoundError:
            replied_data = []
        
        return tweet_id in replied_data
        
    except Exception as e:
        print(f"❌ Yanıt kontrolü hatası: {e}")
        return False

def mark_as_replied(tweet_id):
    """Tweet'i yanıtlandı olarak işaretle"""
    try:
        replies_file = "replied_tweets.json"
        
        try:
            with open(replies_file, 'r', encoding='utf-8') as f:
                replied_data = json.load(f)
        except FileNotFoundError:
            replied_data = []
        
        if tweet_id not in replied_data:
            replied_data.append(tweet_id)
            
            # Son 100 tweet'i tut (dosya çok büyümesin)
            if len(replied_data) > 100:
                replied_data = replied_data[-100:]
            
            with open(replies_file, 'w', encoding='utf-8') as f:
                json.dump(replied_data, f, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"❌ Yanıt işaretleme hatası: {e}")

# ENHANCED send_tweet fonksiyonu - analytics ve quote tweet ile
def send_tweet_with_analytics(content, project_key=None, tweet_type=None, quoted_tweet_id=None):
    """Tweet gönder ve analytics kaydet (Quote tweet desteği)"""
    global last_tweet_time
    
    # Rate limiting kontrolü
    current_time = time.time()
    if last_tweet_time:
        time_since_last = current_time - last_tweet_time
        if time_since_last < MINIMUM_INTERVAL:
            wait_time = MINIMUM_INTERVAL - time_since_last
            print(f"⏳ Rate limiting: {wait_time/60:.1f} dakika beklemek gerekiyor (2.5 saat kural)...")
            return False
    
    url = "https://api.twitter.com/2/tweets"
    
    auth_header = create_oauth_header("POST", url)
    headers = {
        "Authorization": auth_header, 
        "Content-Type": "application/json"
    }
    data = {"text": content}
    
    # Quote tweet ise quoted_tweet_id ekle
    if quoted_tweet_id:
        data["quote_tweet_id"] = quoted_tweet_id
        print(f"💬 Quote tweet gönderiliyor: {quoted_tweet_id}")
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        result = response.json()
        tweet_id = result['data']['id']
        last_tweet_time = current_time
        
        print(f"✅ Tweet gönderildi!")
        print(f"📝 İçerik: {content}")
        print(f"🔗 Tweet ID: {tweet_id}")
        if quoted_tweet_id:
            print(f"💬 Quote Tweet ID: {quoted_tweet_id}")
        print(f"📊 Uzunluk: {len(content)} karakter")
        
        # Analytics kaydet
        if project_key and tweet_type:
            save_tweet_analytics(tweet_id, content, project_key, tweet_type)
        
        return tweet_id  # Tweet ID döndür
    elif response.status_code == 429:
        print(f"⚠️ Twitter API rate limit! 2.5 saat bekliyorum...")
        return False
    else:
        print(f"❌ Tweet gönderme hatası: {response.text}")
        return False

# ENHANCED create_enhanced_tweet - thread ve analytics desteği ile
def create_enhanced_tweet_v2():
    """Enhanced tweet v2 - thread ve analytics desteği"""
    try:
        # Son tweet'leri analiz et
        project_tweet_types = get_recent_tweets()
        
        # Proje ve tweet tipi seçimi
        project_keys = list(projects.keys())
        all_tweet_types = list(TWEET_TYPES.keys())
        
        import random
        
        # Proje seçimi (önceki logic)
        unused_projects = [p for p in project_keys if p not in project_tweet_types]
        
        if unused_projects:
            selected_project = random.choice(unused_projects)
            available_types = all_tweet_types
            print(f"🎯 Yeni proje seçildi: {selected_project} (hiç mention edilmemiş)")
        else:
            project_counts = {p: len(types) for p, types in project_tweet_types.items()}
            selected_project = min(project_counts.keys(), key=lambda x: project_counts[x])
            
            used_types = project_tweet_types.get(selected_project, [])
            available_types = [t for t in all_tweet_types if t not in used_types]
            
            if not available_types:
                from collections import Counter
                type_counts = Counter(used_types)
                available_types = [min(all_tweet_types, key=lambda x: type_counts.get(x, 0))]
                
            print(f"🎯 Var olan proje seçildi: {selected_project}")
        
        selected_type = random.choice(available_types)
        type_config = TWEET_TYPES[selected_type]
        
        sentiment_data = search_twitter_sentiment(selected_project)
        
        print(f"🎯 Seçilen proje: {projects[selected_project]['mention']} - {projects[selected_project]['focus']}")
        print(f"🎭 Tweet tipi: {selected_type} - {type_config['style']}")
        
        # Direkt uzun tweet modu - Twitter Blue ile 4000 karaktere kadar
        length_config = choose_tweet_length()
        
        if length_config['style'] == 'thread':
            print("📝 Uzun makale tweet modu - Twitter Blue ile direkt uzun tweet...")
        
        tweet_content = get_enhanced_ai_tweet(selected_project, sentiment_data, length_config, selected_type, type_config)
        
        if tweet_content is None:
            print("❌ ChatGPT ile tweet oluşturulamadı! Bu çalışma geçiliyor.")
            return False
        
        print(f"💬 Tweet hazır: {tweet_content}")
        print(f"📊 Uzunluk: {len(tweet_content)} karakter")
        
        # Quote tweet için tweet ID'yi al
        quoted_tweet_id = None
        if selected_type == "quote_commentary":
            quoted_tweet = find_recent_project_tweet(selected_project)
            if quoted_tweet:
                quoted_tweet_id = quoted_tweet['id']
                print(f"💬 Quote tweet bulundu: {quoted_tweet['text'][:50]}...")
        
        # Tweet'i gönder
        if len(sys.argv) > 1 and sys.argv[1] == "test":
            print("🧪 TEST MODU: Tweet gönderilmiyor, sadece oluşturuluyor!")
            if quoted_tweet_id:
                print(f"💬 TEST: Quote tweet olacaktı: {quoted_tweet_id}")
            success = True
        else:
            tweet_id = send_tweet_with_analytics(tweet_content, selected_project, selected_type, quoted_tweet_id)
            success = bool(tweet_id)
        
        if success:
            print("🎉 Tweet başarıyla gönderildi!")
        else:
            print("❌ Tweet gönderme başarısız!")
            
        return success
        
    except Exception as e:
        print(f"❌ Enhanced tweet v2 hatası: {e}")
        return False

# ENHANCED auto_tweet fonksiyonu
def auto_tweet_v2():
    """Enhanced otomatik tweet v2 - analytics ve community features ile"""
    current_time = datetime.now()
    current_hour = current_time.hour
    
    print(f"⏰ {current_time.strftime('%Y-%m-%d %H:%M:%S')} - Enhanced otomatik tweet v2 başlatılıyor...")
    
    # Analytics kontrol et (her çalıştırmada)
    print("📊 Tweet analytics kontrol ediliyor...")
    check_pending_analytics()
    
    # Community interaction kontrol et (%30 olasılıkla)
    if random.randint(1, 100) <= 30:
        print("💬 Mention'lar kontrol ediliyor...")
        check_mentions_and_reply()
    
    # Saat kontrolü - sadece 10:00-22:00 arası tweet at
    if current_hour < TWEET_START_HOUR or current_hour >= TWEET_END_HOUR:
        print(f"🌙 Gece saati ({current_hour}:00) - Tweet atılmıyor (sadece {TWEET_START_HOUR}:00-{TWEET_END_HOUR}:00)")
        return False
    
    # Rate limiting kontrolü
    global last_tweet_time
    if last_tweet_time:
        time_since_last = time.time() - last_tweet_time
        if time_since_last < MINIMUM_INTERVAL:
            wait_time = MINIMUM_INTERVAL - time_since_last
            print(f"⏳ Rate limiting aktif: {wait_time/60:.1f} dakika daha beklemeli (2.5 saat kural)")
            return False
    
    success = create_enhanced_tweet_v2()
    if success:
        print("✅ Enhanced otomatik tweet v2 tamamlandı!")
    else:
        print("❌ Enhanced otomatik tweet v2 başarısız!")
    
    return success

def main():
    """Ana fonksiyon"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🧪 Test modu - Tek tweet (Enhanced v2)")
        create_enhanced_tweet_v2()
    elif len(sys.argv) > 1 and sys.argv[1] == "quote":
        print("💬 Quote tweet testi")
        # Specific quote tweet test
        project_key = list(projects.keys())[0]  # İlk projeyi seç
        quoted_tweet = find_recent_project_tweet(project_key)
        if quoted_tweet:
            print(f"✅ Quote tweet bulundu: {quoted_tweet['text']}")
            # Test prompt
            sentiment_data = search_twitter_sentiment(project_key)
            length_config = choose_tweet_length()
            time_tone = get_time_based_tone()
            
            tweet_content = get_enhanced_ai_tweet(project_key, sentiment_data, length_config, "quote_commentary", TWEET_TYPES["quote_commentary"])
            if tweet_content:
                print(f"💬 Quote tweet içeriği: {tweet_content}")
                print(f"📋 Orijinal tweet: {quoted_tweet['text']}")
            else:
                print("❌ Quote tweet oluşturulamadı")
        else:
            print("❌ Proje tweet'i bulunamadı")
    elif len(sys.argv) > 1 and sys.argv[1] == "meme":
        print("😂 Meme tweet testi")
        # Specific meme test
        project_key = list(projects.keys())[0]  # İlk projeyi seç
        sentiment_data = search_twitter_sentiment(project_key)
        length_config = choose_tweet_length()
        
        tweet_content = get_enhanced_ai_tweet(project_key, sentiment_data, length_config, "crypto_meme", TWEET_TYPES["crypto_meme"])
        if tweet_content:
            print(f"😂 Meme tweet: {tweet_content}")
        else:
            print("❌ Meme tweet oluşturulamadı")
    elif len(sys.argv) > 1 and sys.argv[1] == "time":
        print("⏰ Zaman bazlı ton testi")
        # Test different time tones manually
        for hour in [8, 14, 19, 23]:
            current_hour = hour
            
            if 6 <= current_hour < 12:
                time_tone = {
                    "tone": "energetic_morning",
                    "modifier": "Sabah enerjisi ile, pozitif ve motivasyonel"
                }
            elif 12 <= current_hour < 17:
                time_tone = {
                    "tone": "analytical_noon", 
                    "modifier": "Öğle saatleri analitik yaklaşım, daha detaylı"
                }
            elif 17 <= current_hour < 22:
                time_tone = {
                    "tone": "casual_evening",
                    "modifier": "Akşam rahat atmosfer, daha samimi ve paylaşımcı"
                }
            else:
                time_tone = {
                    "tone": "chill_night",
                    "modifier": "Gece sakinliği, düşünceli ve derinlemesine"
                }
            
            print(f"Saat {hour}:00 - {time_tone['tone']}: {time_tone['modifier']}")
    elif len(sys.argv) > 1 and sys.argv[1] == "analytics":
        print("📊 Analytics raporu")
        check_pending_analytics()
    elif len(sys.argv) > 1 and sys.argv[1] == "mentions":
        print("💬 Mention kontrol")
        check_mentions_and_reply()
# Haber sistemi command'ları kaldırıldı
    else:
        print("🤖 Enhanced Bot v2 modu")
        # Enhanced auto_bot
        print("🤖 Enhanced Kaito Twitter Bot v4.2 başlatılıyor...")
        
        # API testleri
        if not test_twitter():
            print("❌ Twitter API bağlantısı başarısız! Bot durduruluyor.")
            return
        
        if not test_openai():
            print("❌ OpenAI API çalışmıyor! Bot durduruluyor (sadece ChatGPT kullanılıyor).")
            return
        else:
            print("✅ Tüm API'ler çalışıyor!")
        
        print("⏰ İlk tweet schedule'da bekliyor (rate limiting güvenliği için)")
        
        # Enhanced schedule
        def scheduled_tweet_v2():
            print("📅 Enhanced Schedule kontrolü - tweet deneniyor...")
            return auto_tweet_v2()
        
        # Her 30 dakikada kontrol et
        schedule.every(30).minutes.do(scheduled_tweet_v2)
        
        print("⏰ Enhanced Bot schedule'ı ayarlandı:")
        print("   📊 Her 30dk: Analytics kontrol, mention yanıt (%30)")
        print("   📈 Otomatik: Tweet performans takibi")
        print("   🎯 Quote tweet (%15), Meme tweet (%10), Zaman bazlı ton")
        print("   🤖 Normal tweet modu (haber sistemi kaldırıldı)")
        print("🔄 Enhanced Bot çalışmaya başladı! Ctrl+C ile durdurun.")
        print("\nTest komutları:")
        print("   python bot.py test    - Normal tweet testi")
        print("   python bot.py quote   - Quote tweet testi")
        print("   python bot.py meme    - Meme tweet testi")
        print("   python bot.py time    - Zaman tonu testi")
        
        # Sonsuz döngü
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                print("\n⏹️ Enhanced Bot durduruldu!")
                break
            except Exception as e:
                print(f"❌ Enhanced Bot hatası: {e}")
                time.sleep(300)

if __name__ == "__main__":
    main()