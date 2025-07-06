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
# Tweet Geçmişi Takip Sistemi
# ------------------------------------------------------------
TWEET_HISTORY_FILE = "tweet_history.json"

def load_tweet_history():
    """Tweet geçmişini yükle"""
    try:
        if os.path.exists(TWEET_HISTORY_FILE):
            with open(TWEET_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "project_mentions": {},
                "total_tweets": 0,
                "last_tweet_date": None
            }
    except Exception as e:
        print(f"❌ Tweet history yüklenirken hata: {e}")
        return {
            "project_mentions": {},
            "total_tweets": 0,
            "last_tweet_date": None
        }

def save_tweet_history(history):
    """Tweet geçmişini kaydet"""
    try:
        with open(TWEET_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Tweet history kaydedilirken hata: {e}")

def update_project_mention_history(project_key, mention_type="general"):
    """Proje bahsetme geçmişini güncelle"""
    history = load_tweet_history()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if project_key not in history["project_mentions"]:
        history["project_mentions"][project_key] = {
            "count": 0,
            "last_mentioned": None,
            "mention_types": [],
            "first_mention_date": today
        }
    
    # Güncelle
    history["project_mentions"][project_key]["count"] += 1
    history["project_mentions"][project_key]["last_mentioned"] = today
    history["project_mentions"][project_key]["mention_types"].append(mention_type)
    
    # Son 10 mention type'ı tut (dosya şişmesin)
    if len(history["project_mentions"][project_key]["mention_types"]) > 10:
        history["project_mentions"][project_key]["mention_types"] = history["project_mentions"][project_key]["mention_types"][-10:]
    
    history["total_tweets"] += 1
    history["last_tweet_date"] = today
    
    save_tweet_history(history)
    print(f"📊 {project_key} mention history güncellendi: {history['project_mentions'][project_key]['count']} kez bahsedildi")

def get_project_mention_count(project_key):
    """Projeden kaç kez bahsedildiğini öğren"""
    history = load_tweet_history()
    if project_key in history["project_mentions"]:
        return history["project_mentions"][project_key]["count"]
    return 0

def get_days_since_last_mention(project_key):
    """Son bahsetmeden bu yana kaç gün geçti"""
    history = load_tweet_history()
    if project_key in history["project_mentions"] and history["project_mentions"][project_key]["last_mentioned"]:
        last_date = datetime.strptime(history["project_mentions"][project_key]["last_mentioned"], '%Y-%m-%d')
        today = datetime.now()
        return (today - last_date).days
    return 999  # Hiç bahsedilmemiş

def select_smart_opening_style(project_key):
    """Geçmişe bakarak akıllı başlangıç stili seç"""
    mention_count = get_project_mention_count(project_key)
    days_since = get_days_since_last_mention(project_key)
    
    if mention_count == 0:
        # İlk kez bahsediliyor
        return "first_discovery"
    elif mention_count == 1:
        # 2. kez bahsediliyor
        if days_since <= 7:
            return "recent_follow_up"
        else:
            return "rediscovery"
    elif mention_count >= 2:
        # 3. ve sonraki kez
        if days_since <= 3:
            return "frequent_update"
        elif days_since <= 14:
            return "regular_check"
        else:
            return "long_term_follow"
    
    return "general"  # fallback

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
gemini_key = os.getenv('GEMINI_API_KEY') or "AIzaSyBKUhepHbuVBiaYzkQkZEvnbfEO5MJEgJM"

# API key kontrolü
print(f"🔍 API Key Kontrolü:")
print(f"   Twitter API Key: {'✅' if api_key else '❌'} {f'({api_key[:10]}...)' if api_key else ''}")
print(f"   OpenAI Key: {'✅' if openai_key else '❌'} (uzunluk: {len(openai_key) if openai_key else 0})")
print(f"   Gemini Key: {'✅' if gemini_key else '❌'} (uzunluk: {len(gemini_key) if gemini_key else 0})")
if openai_key:
    print(f"   OpenAI Key başı: {openai_key[:20]}...")
    print(f"   OpenAI Key sonu: ...{openai_key[-10:]}")
if gemini_key:
    print(f"   Gemini Key başı: {gemini_key[:20]}...")
    print(f"   Gemini Key sonu: ...{gemini_key[-10:]}")

print(f"🌍 Environment Variables:")
for key in ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_SECRET', 'OPENAI_API_KEY', 'GEMINI_API_KEY']:
    value = os.getenv(key)
    print(f"   {key}: {'✅ SET' if value else '❌ MISSING'}")

# API KEY KONTROLÜ - Production için sadece environment variables
import sys
if not all([api_key, api_secret, access_token, access_secret]):
    print("❌ Gerekli Twitter API environment variable'ları eksik!")
    print("🔧 Lütfen şu environment variable'ları ayarlayın:")
    print("   - TWITTER_API_KEY")
    print("   - TWITTER_API_SECRET") 
    print("   - TWITTER_ACCESS_TOKEN")
    print("   - TWITTER_ACCESS_SECRET")
    print("💡 Heroku'da: heroku config:set TWITTER_API_KEY=your_key")
    sys.exit(1)

# AI API kontrolü - Gemini öncelikli, OpenAI fallback
if not gemini_key and not openai_key:
    print("❌ Hiçbir AI API key'i bulunamadı!")
    print("🔧 En az birini ayarlayın:")
    print("   - GEMINI_API_KEY (öncelikli)")
    print("   - OPENAI_API_KEY (fallback)")
    sys.exit(1)

if gemini_key:
    print("✅ Gemini API key bulundu! Primary AI olarak kullanılacak.")
elif openai_key:
    print("✅ OpenAI API key bulundu! Fallback AI olarak kullanılacak.")

print("✅ Tüm API anahtarları yüklendi!")

# Güncel Takip Edilen Projeler - 8 Proje
projects = {
    "infinitlabs": {
        "mention": "@infinitlabs", 
        "focus": "DeFi Infrastructure", 
        "specialty": "next-gen yield farming ve liquidity management protokolü",
        "trends": ["yield aggregation teknolojisi", "automated portfolio rebalancing", "cross-chain DeFi", "institutional DeFi araçları"],
        "price_action": "airdrop programı yaklaşıyor, TVL artıyor",
        "ecosystem": "Multi-chain DeFi protocol",
        "personality": "yield ve verimlilik odaklı",
        "token_status": "pre_token",
        "tech_detail": "Automated vault system ile yield farming stratejilerini optimize ediyor. Cross-chain liquidity routing, risk-adjusted returns, gas optimization algorithms. Institutional grade risk management tools."
    },
    "anoma": {
        "mention": "@anoma", 
        "focus": "intent-centric blockchain", 
        "specialty": "kullanıcı deneyiminde radikal basitleştirme sunan intent-based mimari",
        "trends": ["intent-based mimariler gelişiyor", "kullanıcı deneyimi odaklı blockchain", "mahremiyet teknolojileri", "chain-agnostic çözümler"],
        "price_action": "mainnet öncesi geliştirme aşamasında", 
        "ecosystem": "Intent-centric L1 blockchain",
        "personality": "teknik ve mahremiyet odaklı",
        "token_status": "pre_token",
        "tech_detail": "Intent-centric mimarisi ile kullanıcılar sadece ne yapmak istediklerini belirtiyor. zk-SNARKs entegreli privacy, 3000+ TPS hedef performans."
    },
    "memex": {
        "mention": "@MemeXprotocol",
        "focus": "meme coin infrastructure",
        "specialty": "meme coin oluşturma ve yönetim platformu",
        "trends": ["meme coin sezonu", "retail trader araçları", "automated meme trading", "social media entegrasyonu"],
        "price_action": "meme coin trend'iyle birlikte momentum kazandı",
        "ecosystem": "Meme coin creation platform",
        "personality": "sosyal ve eğlence odaklı", 
        "token_status": "active",
        "tech_detail": "One-click meme coin deployment, automated liquidity provision, social sentiment tracking, viral marketing tools integration."
    },
    "uxlink": {
        "mention": "@UXLINKofficial",
        "focus": "social infrastructure",
        "specialty": "Web3 sosyal ağ ve iletişim altyapısı",
        "trends": ["Web3 sosyal uygulamalar", "decentralized messaging", "social token economy", "community governance"],
        "price_action": "sosyal özellikler beta'da, kullanıcı artışı var",
        "ecosystem": "Web3 social protocol",
        "personality": "sosyal ve community odaklı",
        "token_status": "active",
        "tech_detail": "Decentralized messaging, social graph ownership, reputation systems, community reward mechanisms, cross-platform social identity."
    },
    "mitosis": {
        "mention": "@mitosis_org", 
        "focus": "likidite fragmentasyonu çözümü", 
        "specialty": "DeFi alanında yeni standart oluşturmayı hedefleyen likidite protokolü",
        "trends": ["likidite protokolü geliştirmeleri", "otomatik pazar yapıcılığı", "çapraz zincir likidite", "DeFi yield optimizasyonu"],
        "price_action": "TVL hızla büyüyor, governance aktivitesi artıyor",
        "ecosystem": "Yeni nesil DeFi protokolü",
        "personality": "DeFi ve yield odaklı",
        "token_status": "pre_token",
        "tech_detail": "Dinamik arbitraj botları, çoklu zincir slippage optimizasyonu, akıllı likidite routing. %40'a varan gas tasarrufu."
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
        "tech_detail": "AI agent marketplace, otomatik görev yürütme, gelir paylaşımı token ekonomisi, 1000+ aktif AI agent."
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
        "tech_detail": "EVM uyumlu L1, 1 saniye finality, AsyncBFT consensus, testnet incentive programı aktif."
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
        "tech_detail": "fhEVM v0.7 testnet canlı, Solidity'de private smart contracts, FHE ASIC'lerle 1000+ TPS hedef."
    }
}

# Tweet uzunluk kategorileri - ESNEK VE MANTIKLI
TWEET_LENGTHS = {
    "short": {"weight": 40, "min": 180, "max": 500, "style": "concise"},        # %40 - Kısa ve öz
    "medium": {"weight": 35, "min": 500, "max": 1200, "style": "normal"},       # %35 - Normal detaylı
    "long": {"weight": 20, "min": 1200, "max": 2500, "style": "analysis"},      # %20 - Uzun analiz
    "thread": {"weight": 5, "min": 2500, "max": 4000, "style": "thread"}        # %5 - Thread formatı
}

# TWEET TİPLERİ - DETAYLI ANALİZ ODAKLI
TWEET_TYPES = {
    "tech_deep": {
        "weight": 25,
        "style": "Teknoloji odaklı derinlemesine açıklama",
        "tone": "Teknik ama anlaşılır, bilgi paylaşan"
    },
    "market_perspective": {
        "weight": 20,
        "style": "Piyasa analizi ve görüş",
        "tone": "Analitik ama kişisel görüş"
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
    "comparison": {
        "weight": 12,
        "style": "Başka projelerle karşılaştırma", 
        "tone": "Karşılaştırmalı, objektif"
    },
    "quote_commentary": {
        "weight": 8,
        "style": "Proje tweet'ine yorum yapma",
        "tone": "Yorumlayıcı, kişisel görüş ekleyen"
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

# Tweet sistemi - günde 12 tweet sabah 8 gece yarısı arası (Avrupa saati)
last_tweet_time = None
MINIMUM_INTERVAL = 1.33 * 60 * 60  # 1.33 saat (saniye) - günde 12 tweet (16 saat ÷ 12 = 1.33 saat)
DAILY_TWEET_COUNT = 12
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
    """Ağırlıklı rastgele tweet uzunluğu seç - esnek ve mantıklı"""
    rand = random.randint(1, 100)
    if rand <= 40:
        return TWEET_LENGTHS["short"]
    elif rand <= 75:  # 40 + 35
        return TWEET_LENGTHS["medium"] 
    elif rand <= 95:  # 40 + 35 + 20
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

def clean_tweet(tweet, length_config, clean_project_name):
    """Tweet temizleme fonksiyonu - hem Gemini hem OpenAI için"""
    if not tweet:
        return None
        
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
    
    # Paragraf formatı düzelt - mantıklı paragraf geçişlerinde boş satır ekle
    if len(tweet) > 800:  # Sadece uzun tweet'lerde uygula
        # İlk olarak tweet'i cümlelere böl
        sentences = re.split(r'([.!?])\s+', tweet)
        formatted_sentences = []
        current_paragraph = ""
        
        for i in range(0, len(sentences)-1, 2):
            sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else "")
            current_paragraph += sentence + " "
            
            # Paragraf geçiş koşulları:
            # 1. 200+ karakter olmuşsa ve mantıklı bir geçiş varsa
            # 2. Konu değişimi gösteren anahtar kelimeler
            topic_changes = [
                "ama", "ancak", "fakat", "lakin", "diğer taraftan", 
                "bir diğer", "başka bir", "aynı zamanda", "öte yandan",
                "bunun yanında", "bu arada", "şimdi", "artık", "gelgelelim",
                "işte", "peki", "sonuç olarak", "kısacası", "özetle"
            ]
            
            if len(current_paragraph) > 200:
                # Sonraki cümleye bak, konu değişimi var mı?
                next_sentence_start = sentences[i+2] if i+2 < len(sentences) else ""
                if any(word in next_sentence_start.lower()[:50] for word in topic_changes):
                    formatted_sentences.append(current_paragraph.strip())
                    current_paragraph = ""
        
        # Kalan kısmı ekle
        if current_paragraph.strip():
            formatted_sentences.append(current_paragraph.strip())
        
        # Paragrafları boş satırla birleştir
        if len(formatted_sentences) > 1:
            tweet = "\n\n".join(formatted_sentences)
            print(f"📝 {len(formatted_sentences)} paragraf oluşturuldu")
        else:
            print(f"📝 Tek paragraf olarak bırakıldı")
    
    print(f"🧹 Temizlenmiş tweet: {tweet}")
    
    # Uzunluk kontrolü - eğer uygun değilse kısalt veya uzat
    if len(tweet) > length_config['max']:
        # Akıllı kısaltma - cümle sonunda kes
        max_length = length_config['max'] - 10  # 10 karakter buffer
        if max_length < len(tweet):
            # Son cümle sonunu bul
            cut_tweet = tweet[:max_length]
            last_period = cut_tweet.rfind('.')
            last_exclamation = cut_tweet.rfind('!')
            last_question = cut_tweet.rfind('?')
            
            # En son noktalama işaretini bul
            last_punct = max(last_period, last_exclamation, last_question)
            
            if last_punct > max_length - 200:  # Çok geride değilse
                tweet = tweet[:last_punct + 1]
                print(f"✂️ Tweet akıllı kısaltıldı (cümle sonunda): {len(tweet)} karakter")
            else:
                tweet = tweet[:max_length] + "..."
                print(f"✂️ Tweet zorla kısaltıldı: {len(tweet)} karakter")
        
    elif len(tweet) < length_config['min']:
        tweet += " Takip etmeye değer bence."
        print(f"📏 Tweet uzatıldı: {len(tweet)} karakter")
    
    print(f"✅ AI tweet kullanılıyor!")
    return tweet

def call_gemini_api(prompt, length_config, clean_project_name):
    """Gemini API call - 2.5 Pro model ile tweet oluştur (en güçlü reasoning + 2M context)"""
    try:
        # Uzunluk bazlı prompt
        is_short = length_config['style'] == 'concise'
        is_thread = length_config['style'] == 'thread'
        
        # Sistem promptu ile user promptu birleştir
        combined_prompt = f"""Sen crypto piyasasını takip eden sıradan bir insansın. AI değilsin, gerçek bir crypto meraklısısın.

KURAL:
- {length_config['min']}-{length_config['max']} karakter tweet yaz
- {clean_project_name} ismini doğal şekilde kullan (@ işareti kullanma)
- Hashtag kullanma hiç
- AI gibi formal değil, arkadaşça konuş
{f"- Kısa ve öz, direkt sadede gel" if is_short else "- Detaylı açıklama yap ama samimi tondan çıkma"}
{f"- Paragraflar arasında BOŞ SATIR bırak" if not is_short else ""}

YAPMA BUNLARI:
- "analiz ettiğimde", "değerlendirdiğimde", "incelediğimde" AI dili
- "ekosistem için önemli", "dikkat çekici gelişme" buzzword'ler
- "bugün X projesini inceledim" klişe başlangıçları
- Kendi başlangıç ifadesi uydurma, verilen başlangıcı kullan!

YAP BUNLARI:
- Tweet'e verilen prompt'taki akıllı başlangıçla başla
- Sonra devam et: "bayağı cool", "ilginç duruyor", "fena değil"
- "X'in şu kısmı bayağı cool"
- "henüz erken ama X..."

TON: Crypto takipçisi arkadaş, samimi, meraklı ama abartısız

{f"KISA TWEET STİLİ: Sadede gel, uzatma, direkt söyle ne düşündüğünü" if is_short else ""}
{f"THREAD STİLİ: Uzun makale formatı, paragraflar arası BOŞ SATIR" if is_thread else ""}

{prompt}

Sadece tweet yaz, başka hiçbir şey ekleme."""

        # Gemini API URL - 2.5 Pro model (en güçlü ve kaliteli)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={gemini_key}"
        
        # Request data
        data = {
            "contents": [{
                "parts": [{
                    "text": combined_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 1.1,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 12000 if length_config['style'] == 'thread' else 4000
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        print(f"🤖 Gemini 2.5 Pro API çağrısı yapılıyor...")
        print(f"🔑 API Key: {gemini_key[:20]}...{gemini_key[-10:]}")
        print(f"📝 Prompt uzunluğu: {len(combined_prompt)} karakter")
        
        response = requests.post(url, headers=headers, json=data)
        
        print(f"📡 Gemini Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                
                # Response yapısını kontrol et
                if 'content' in candidate and 'parts' in candidate['content']:
                    tweet = candidate['content']['parts'][0]['text'].strip()
                elif 'text' in candidate:
                    tweet = candidate['text'].strip()
                elif candidate.get('finishReason') == 'MAX_TOKENS':
                    print("⚠️ Gemini Pro MAX_TOKENS limitine takıldı, Flash'a geçiliyor...")
                    # Flash modele fallback yap
                    url_flash = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
                    flash_response = requests.post(url_flash, headers=headers, json=data)
                    
                    if flash_response.status_code == 200:
                        flash_result = flash_response.json()
                        if 'candidates' in flash_result and len(flash_result['candidates']) > 0:
                            flash_candidate = flash_result['candidates'][0]
                            if 'content' in flash_candidate and 'parts' in flash_candidate['content']:
                                tweet = flash_candidate['content']['parts'][0]['text'].strip()
                                print(f"✅ Flash fallback başarılı: {tweet[:50]}...")
                            else:
                                return None
                        else:
                            return None
                    else:
                        return None
                else:
                    print("❌ Beklenmedik Gemini Pro response yapısı")
                    print(f"Candidate keys: {candidate.keys()}")
                    print(f"FinishReason: {candidate.get('finishReason')}")
                    return None
                
                print(f"✅ Gemini Pro Tweet: {tweet}")
                
                # Usage metadata göster
                if 'usageMetadata' in result:
                    usage = result['usageMetadata']
                    print(f"📊 Token kullanımı: {usage.get('promptTokenCount', 0)} input + {usage.get('candidatesTokenCount', 0)} output = {usage.get('totalTokenCount', 0)} total")
                
                # Tweet temizleme işlemi
                return clean_tweet(tweet, length_config, clean_project_name)
            else:
                print("⚠️ Gemini yanıt aldı ama content yok")
                print(f"Response: {result}")
                return None
                
        elif response.status_code == 429:
            print("⚠️ Gemini rate limit! Biraz bekleyip tekrar dene.")
            return None
        else:
            print(f"❌ Gemini API hatası: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Gemini API exception: {e}")
        return None

def get_enhanced_ai_tweet(project_key, sentiment_data, target_length, tweet_type, type_config):
    """Enhanced AI tweet - önceden seçilmiş tweet tipi ile DOĞAL İNSAN GİBİ + AKILLI BAŞLANGIÇ"""
    import random
    project = projects[project_key]
    length_config = target_length
    
    # Tweet geçmişine göre akıllı başlangıç stili seç
    opening_style = select_smart_opening_style(project_key)
    mention_count = get_project_mention_count(project_key)
    days_since = get_days_since_last_mention(project_key)
    
    print(f"🧠 Akıllı başlangıç: {opening_style} (bahsetme sayısı: {mention_count}, son: {days_since} gün önce)")
    
    # Saate göre ton ayarla (Özellik #12)
    time_tone = get_time_based_tone()
    
    # Quote tweet için proje tweet'i bul
    quoted_tweet = None
    if tweet_type == "quote_commentary":
        quoted_tweet = find_recent_project_tweet(project_key)
        if not quoted_tweet:
            # Quote tweet bulunamazsa fallback tip seç
            tweet_type = random.choice(["tech_deep", "casual_discovery", "market_perspective"])
    
    # Akıllı başlangıç ifadeleri
    smart_openings = {
        "first_discovery": [
            "geçen {clean_project_name} gördüm, ilginç duruyor",
            "arkadaş {clean_project_name}'den bahsetti, baktım",
            "şansa {clean_project_name}'e denk geldim",
            "bugün {clean_project_name} ile tanıştım",
            "rastgele {clean_project_name} keşfettim",
            "daha önce duymamıştım ama {clean_project_name}"
        ],
        "recent_follow_up": [
            "daha önce {clean_project_name}'den bahsetmiştim, son durum",
            "{clean_project_name}'i tekrar inceledim",
            "{clean_project_name} hakkında güncelleme var",
            "geçen bahsettiğim {clean_project_name}",
            "{clean_project_name}'te yenilikler olmuş",
            "az önce {clean_project_name}'e baktım yine"
        ],
        "rediscovery": [
            "uzun zamandır {clean_project_name}'e bakmamıştım",
            "{clean_project_name}'e yeniden göz attım",
            "bir süre {clean_project_name}'i unutmuştum ama",
            "{clean_project_name}'i yeniden keşfettim",
            "aradan zaman geçti, {clean_project_name} nasıl",
            "{clean_project_name}'e geri döndüm"
        ],
        "frequent_update": [
            "yine {clean_project_name}'ten bahsedeyim",
            "{clean_project_name}'teki son durum",
            "{clean_project_name} sürekli gündemde",
            "bir kez daha {clean_project_name}",
            "{clean_project_name}'le ilgili yeni gelişme",
            "{clean_project_name}'te hareket var yine"
        ],
        "regular_check": [
            "{clean_project_name}'i düzenli takip ediyorum",
            "{clean_project_name} konusunda güncel durum",
            "her zamanki {clean_project_name} kontrolü",
            "{clean_project_name}'i gözden geçiriyorum",
            "{clean_project_name} takibini sürdürüyorum",
            "rutinimde {clean_project_name} var"
        ],
        "long_term_follow": [
            "uzun süredir takip ettiğim {clean_project_name}",
            "{clean_project_name}'le ilgili son gelişmeler",
            "{clean_project_name} macerası devam ediyor",
            "eskiden beri izlediğim {clean_project_name}",
            "{clean_project_name}'in hikayesi",
            "zamanında keşfettiğim {clean_project_name}"
        ]
    }
    
    # Proje ismini hazırla (underscore'ları boşluğa çevir)
    clean_project_name = project['mention'].replace('@', '').replace('_', ' ').title()
    
    # Akıllı başlangıç seç
    selected_opening = random.choice(smart_openings.get(opening_style, smart_openings["first_discovery"]))
    selected_opening = selected_opening.format(clean_project_name=clean_project_name)
    
    type_prompts = {
        "tech_deep": f"""{clean_project_name} hakkında {"uzun makale tarzı" if length_config['style'] == 'thread' else f"{length_config['min']}-{length_config['max']} karakter"} tweet at. Crypto insanı gibi konuş.

⚠️ FORMATLLAMA: Paragraflar arasında BOŞ SATIR bırak!

AKILLI BAŞLANGIÇ (MUTLAKA KULLAN): "{selected_opening}"

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
- Verilen başlangıçla başla: "{selected_opening}"
- "bu teknoloji bayağı cool", "gerçekten işe yarayabilir"  
- "henüz erken ama potansiyeli var", "şu kısmı çok zekice yapılmış"
- Samimi, arkadaşça ton - sanki bir arkadaşına anlatıyorsun
{f"- Makale gibi yapılandır: Giriş-Teknik detay-Kullanım alanları-Sonuç" if length_config['style'] == 'thread' else "- Kısa, net cümleler"}
{f"- Her paragraf ayrı bir konuya odaklan" if length_config['style'] == 'thread' else ""}

TON: {time_tone['tone']} + teknik bilgili crypto insanı

ÖRNEK YAPI:
"{selected_opening}. teknolojisi gerçekten farklı..."
"{selected_opening}, özellikle şu kısmı çok zekice..."

Sadece tweet yaz, açıklama yapma.""",

        "casual_discovery": f"""{clean_project_name} hakkında {length_config['min']}-{length_config['max']} karakter casual tweet at.

⚠️ FORMATLLAMA: Paragraflar arasında BOŞ SATIR bırak!

DURUM: {project.get('development_stage', project['price_action'])}
ÖZELLIK: {project['specialty']}

AKILLI BAŞLANGIÇ (MUTLAKA KULLAN): "{selected_opening}"

ÖNEMLİ: Bu başlangıçla tweet'e başla, sonra devam et!

STIL: Crypto meraklısı, samimi

YAPMA:
- "dikkatimi çekti", "araştırırken karşıma çıktı" klişe başlangıçlar  
- "incelemesi gereken", "önemli bir adım" resmi dil
- Verilen başlangıcı değiştirme!

YAP:  
- Verilen başlangıçla başla: "{selected_opening}"
- Sonra devam et: "bayağı cool...", "ilginç duruyor...", "fena değil..."
- Samimi ton kullan

TON: Samimi, meraklı
ÖRNEK YAPILAR:
"{selected_opening}. şu özelliği bayağı mantıklı geldi..."
"{selected_opening}, henüz yeni galiba ama..."
"{selected_opening}. teknolojisi ilginç duruyor..."

Sadece tweet yaz.""",

        "market_perspective": f"""{clean_project_name} piyasa durumu hakkında {length_config['min']}-{length_config['max']} karakter tweet at.

⚠️ FORMATLLAMA: Paragraflar arasında BOŞ SATIR bırak!

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

⚠️ FORMATLLAMA: Paragraflar arasında BOŞ SATIR bırak!

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

⚠️ FORMATLLAMA: Paragraflar arasında BOŞ SATIR bırak!

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

(BOŞ SATIR)

Teknik kısım - Karmaşık teknolojiyikomşu-akraba ilişkileriyle açıkla  

(BOŞ SATIR)

Avantajlar - "Ne kazanıyoruz" sorusunu günlük hayat örnekleriyle

(BOŞ SATIR)

Rakipler - Diğer çözümlerle kıyaslama (başka ev/dükkanlarlayarışır gibi)

(BOŞ SATIR)

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
    
    # AI API call - Gemini öncelikli, OpenAI fallback
    if gemini_key:
        # Gemini API call
        result_tweet = call_gemini_api(prompt, length_config, clean_project_name)
        if result_tweet:
            # Tweet başarılı, history'yi güncelle
            update_project_mention_history(project_key, opening_style)
        return result_tweet
    elif openai_key:
        # ChatGPT API call (fallback)
        headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
        
        # Uzun tweet'ler için daha fazla token (minimum 1000 karakter için)
        max_tokens_value = 3000 if length_config['style'] == 'thread' else 1500
        
        system_prompt = f"""Sen crypto takip eden samimi bir insansın. Twitter'da doğal konuşursun.

KURAL:
- {length_config['min']}-{length_config['max']} karakter tweet yaz (minimum 1000 karakter gerekli)
- {clean_project_name} ismini doğal şekilde kullan
- @ işareti, hashtag kullanma
- Samimi, arkadaşça konuş - sanki bir arkadaşına anlatıyorsun
- Detaylı ve derinlemesine analiz yap
- Paragraflar arasında BOŞ SATIR bırak (görsel olarak daha güzel görünsün)

FORMATLLAMA:
- Her ana fikri ayrı paragrafta yaz
- Paragraflar arasında bir satır boş bırak
- Uzun cümleri böl, okunabilir yap

İSTEDİĞİM TON: Crypto meraklısı, gerçek insan, abartısız ama detaylı"""

        if length_config['style'] == 'thread':
            system_prompt += f"""

ÖZEL: Bu uzun makale tarzı tweet (4000-8000 karakter)
- Detaylı analiz yap, birden fazla paragraf kullan
- Teknik konuları derinlemesine açıkla
- Twitter Blue uzun tweet formatında
- Makale gibi yapılandır ama samimi tondan çıkma
- Giriş-gelişme-sonuç yapısı kullan
- Her paragraf arasında BOŞ SATIR bırak (çok önemli!)
- Alt başlıklar kullanabilirsin (emoji ile)"""
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
                cleaned_tweet = clean_tweet(tweet, length_config, clean_project_name)
                if cleaned_tweet:
                    # Tweet başarılı, history'yi güncelle
                    update_project_mention_history(project_key, opening_style)
                return cleaned_tweet
            else:
                print(f"❌ OpenAI API hatası: {response.status_code}")
                print(f"❌ Response body: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ OpenAI request exception: {e}")
            return None
    else:
        print("❌ Hiçbir AI API key'i bulunamadı!")
        return None

# retry_chatgpt fonksiyonu kaldırıldı - artık fallback yok

def test_gemini():
    """Gemini API test"""
    if not gemini_key:
        print("⚠️ Gemini API key yok, test atlanıyor")
        return False
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={gemini_key}"
    data = {
        "contents": [{
            "parts": [{
                "text": "Merhaba! Bu bir test. Sadece 'Test başarılı' yaz."
            }]
        }],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 20
        }
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ Gemini API çalışıyor! Yanıt: {text.strip()}")
                return True
            else:
                print(f"⚠️ Gemini API yanıt verdi ama içerik yok")
                return False
        else:
            print(f"❌ Gemini API hatası: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Gemini API exception: {e}")
        return False

def test_openai():
    """OpenAI API test (fallback)"""
    if not openai_key:
        print("⚠️ OpenAI API key yok, test atlanıyor")
        return False
        
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
        
        # AI API testleri - Gemini öncelikli
        ai_working = False
        if gemini_key:
            if test_gemini():
                print("✅ Gemini API çalışıyor! Primary AI olarak kullanılacak.")
                ai_working = True
            else:
                print("⚠️ Gemini API çalışmıyor, OpenAI'ya geçiliyor...")
        
        if not ai_working and openai_key:
            if test_openai():
                print("✅ OpenAI API çalışıyor! Fallback AI olarak kullanılacak.")
                ai_working = True
            else:
                print("❌ OpenAI API de çalışmıyor!")
        
        if not ai_working:
            print("❌ Hiçbir AI API çalışmıyor! Bot durduruluyor.")
            return
        else:
            print("✅ AI API hazır!")
        
        print("⏰ İlk tweet schedule'da bekliyor (rate limiting güvenliği için)")
        
        # Enhanced schedule
        def scheduled_tweet_v2():
            print("📅 Enhanced Schedule kontrolü - tweet deneniyor...")
            return auto_tweet_v2()
        
        # Her 30 dakikada kontrol et
        schedule.every(30).minutes.do(scheduled_tweet_v2)
        
        print("⏰ Gemini Enhanced Bot schedule'ı ayarlandı:")
        print("   🧠 Gemini 2.5 Pro PRIMARY AI (en güçlü + 2M token)")
        print("   📊 Her 30dk: Analytics kontrol, mention yanıt (%30)")
        print("   📈 Otomatik: Tweet performans takibi")
        print("   🎯 Quote tweet, Detaylı analiz odaklı, Zaman bazlı ton")
        print("   🤖 Gemini tweet modu (OpenAI fallback)")
        print("🔄 Gemini Enhanced Bot çalışmaya başladı! Ctrl+C ile durdurun.")
        print("\nTest komutları:")
        print("   python bot.py test    - Normal tweet testi")
        print("   python bot.py quote   - Quote tweet testi")
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