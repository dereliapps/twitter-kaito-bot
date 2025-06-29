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
    "short": {"weight": 25, "min": 120, "max": 250, "style": "punch"},    # %25 - Kısa & Punch
    "medium": {"weight": 50, "min": 250, "max": 300, "style": "normal"},  # %50 - Normal 
    "long": {"weight": 25, "min": 300, "max": 650, "style": "analysis"}   # %25 - Uzun analiz
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
    
    # Ultra doğal crypto insider prompts
    style_prompts = {
        "punch": f"""kim takip ediyor {project['mention']} projesini?

context: {random.choice(project['trends'])}
token status: {project['token_status']}

tarzın:
- gerçek crypto trader gibi casual türkçe
- "kim takip ediyor", "bence", "açıkçası" gibi doğal başlangıçlar
- {length_config['min']}-{length_config['max']} karakter
- sadece {project['mention']} mention et
- uzun çizgi (-) kullanma hiç
- thread değil tek tweet""",
        
        "normal": f"""{project['mention']} hakkında görüşlerini paylaş.

bilgiler:
- {random.choice(project['trends'])}
- {project['specialty']}
- {project['token_status']} durumda

nasıl yaz:
- gerçek crypto insider gibi türkçe
- kişisel görüş ver: "bence", "sanki", "gibi geliyor"
- {length_config['min']}-{length_config['max']} karakter
- sadece {project['mention']} mention
- uzun çizgi (-) kullanma
- casual ton, AI gibi formal değil""",
        
        "analysis": f"""{project['mention']} için daha uzun analiz tweet'i yaz.

detaylar:
- {project['specialty']}
- {project['ecosystem']}
- {project['price_action']}
- {random.choice(project['trends'])}

şartlar:
- gerçek crypto analyst gibi türkçe
- "anyone else tracking" tarzı casual başlangıçlar
- kişisel görüş: "bence bu", "açıkçası", "sanki"
- {length_config['min']}-{length_config['max']} karakter
- sadece {project['mention']} mention
- uzun çizgi (-) hiç kullanma
- doğal konuşma tonu, AI değil"""
    }
    
    prompt = style_prompts[length_config['style']]
    
    # ChatGPT API call
    headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": f"""sen crypto piyasasında olan sıradan bir türksün. yıllardır piyasayı takip ediyorsun.

nasıl tweet atacaksın:
- gerçek crypto insider gibi türkçe konuş
- "kim takip ediyor", "bence", "açıkçası", "sanki" gibi doğal kelimeler kullan
- {project['mention']} projesini mention et
- {length_config['min']}-{length_config['max']} karakter olsun
- uzun çizgi (-) hiç kullanma
- thread atma, tek tweet
- AI gibi formal değil, arkadaşına konuşuyormuş gibi
- hashtag kullanma

example style: "kim takip ediyor @project'i? açıkçası bence bu proje farklı bir yerde, sanki piyasa henüz fark etmedi."""},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.9
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            tweet = result['choices'][0]['message']['content'].strip()
            
            # Uzun çizgi kontrolü ve temizlik
            tweet = tweet.replace('—', ' ')
            tweet = tweet.replace('–', ' ')
            tweet = tweet.replace('-', ' ')
            
            # Uzunluk kontrolü
            if length_config['min'] <= len(tweet) <= length_config['max']:
                return tweet
            else:
                # Uzunluk uygun değilse fallback
                return create_fallback_tweet(project_key, length_config)
        else:
            print(f"❌ AI API hatası: {response.text}")
            return create_fallback_tweet(project_key, length_config)
            
    except Exception as e:
        print(f"❌ AI request hatası: {e}")
        return create_fallback_tweet(project_key, length_config)

def create_fallback_tweet(project_key, length_config):
    """AI çalışmazsa fallback tweet oluştur - ULTRA NATURAL"""
    project = projects[project_key]
    mention = project['mention']
    style = length_config['style']
    token_status = project['token_status']
    
    # Token durumuna göre farklı yaklaşım
    if token_status == "pre_token":
        fallback_templates = {
            "punch": [
                f"kim takip ediyor {mention} projesini? {random.choice(project['trends'])}",
                f"{mention} hâlâ radarın altında. {project['price_action']}",
                f"bence {mention} farklı bir yerde. {project['specialty']} alan kızışıyor",
                f"açıkçası {mention} henüz fark edilmedi. {random.choice(project['trends'])}",
                f"{mention} sessizce büyüyor gibi. {project['price_action']}",
                f"sanki {mention} henüz mainstream değil. {project['specialty']} alan patlamak üzere"
            ],
            
            "normal": [
                f"{mention} son durumu ilginç. {random.choice(project['trends'])} haberi {project['focus']} alanında güçlendiriyor onu. {project['price_action']} durum umut verici.",
                f"bence {mention} takip edilmeli. {project['specialty']} geliştirmeleri {project['price_action']} durumu ile uyumlu. {project['ecosystem']} alan değişiyor.",
                f"açıkçası {mention} hareketli günler geçiriyor. {random.choice(project['trends'])} gelişmesi {project['focus']} alanında öne çıkarıyor. {project['price_action']} mevcut durum.",
                f"sanki {mention} farklı bir momentum'da. {random.choice(project['trends'])} haberi pozisyonunu güçlendiriyor. {project['price_action']} hikayesi var.",
                f"kim takip ediyor {mention} son gelişmelerini? {project['specialty']} çalışmaları ile {project['price_action']} kombini potansiyel yaratıyor. {project['ecosystem']} geleceği parlak."
            ],
            
            "analysis": [
                f"kim takip ediyor {mention} gelişmelerini? {random.choice(project['trends'])} durumu {project['focus']} alanında ciddi momentum yaratıyor. {project['specialty']} yaklaşımı rakiplerinden ayrıştırıyor. {project['price_action']} durumu kurumsal ilgi demek. {project['ecosystem']} altyapısı uzun vadeli değer yaratabilir. erken aşama ama fundamentaller uyumlu gibi.",
                f"bence {mention} detaylı bakılması gereken projeler arasında. {project['ecosystem']} sektörü kızışıyor, {project['specialty']} ile iyi konumdalar. {random.choice(project['trends'])} gelişmesi güçlü icraat göstergesi. {project['price_action']} pazar tanınırlığı var. {project['focus']} hikayesi kurumsal oyuncular arasında ivme kazanıyor.",
                f"açıkçası {mention} teknik ve temel bakışta umut verici. {project['specialty']} teknoloji stack'i {project['focus']} alanındaki sorunları çözmeye odaklanmış. {random.choice(project['trends'])} gelişmesi ürün pazar uyumu ilerlemesi. {project['price_action']} erken biriktirme aşaması olabilir. {project['ecosystem']} pozisyonu genişleme fırsatları yaratıyor."
            ]
        }
    else:  # active token
        fallback_templates = {
            "punch": [
                f"{mention} şu an farklı bir momentumda. {random.choice(project['trends'])}",
                f"bence {mention} performans gösteriyor. {project['price_action']}",
                f"açıkçası {mention} rakiplerini geçti geçiyor. {project['specialty']} alanında",
                f"kim takip ediyor {mention} hareketlerini? {random.choice(project['trends'])}",
                f"sanki {mention} ivme kazandı. {project['price_action']}",
                f"{mention} bu dönemde güçlü duruyor. {project['specialty']} dominantlığı"
            ],
            
            "normal": [
                f"{mention} piyasada güçlü hareket yapıyor. {random.choice(project['trends'])} gelişmesi {project['focus']} sektöründeki liderliğini pekiştiriyor. {project['price_action']} mevcut trendi yansıtıyor.",
                f"bence {mention} takip etmeye değer. {project['specialty']} alanındaki ilerlemeler {project['price_action']} ile destekleniyor. {project['ecosystem']} ekosistemi olgunlaşıyor.",
                f"açıkçası {mention} son durum iyi. {random.choice(project['trends'])} bu momentum {project['focus']} alanında güçlü konumunu gösteriyor. {project['price_action']} hikayeyi doğruluyor.",
                f"kim takip ediyor {mention} son performansını? {project['specialty']} geliştirmeleri {project['price_action']} ile uyumlu ilerliyor. {project['ecosystem']} büyüme gösteriyor."
            ],
            
            "analysis": [
                f"kim analiz ediyor {mention} son durumunu? {random.choice(project['trends'])} gelişmesi {project['focus']} piyasasında güçlü pozisyonu doğruluyor. {project['specialty']} stratejisi rekabet avantajı sağlıyor. {project['price_action']} kurumsal kabul yansıtıyor. {project['ecosystem']} altyapısı sürdürülebilir büyüme için sağlam temel.",
                f"bence {mention} piyasa görünümü güçlü. {project['ecosystem']} sektöründe güçlü trend, {project['specialty']} ile rekabetçi avantaj var. {random.choice(project['trends'])} gelişmesi operasyonel mükemmellik gösteriyor. {project['price_action']} piyasa tanınırlığı yansıtıyor. {project['focus']} hikayesi ana akım benimseme kazanıyor.",
                f"açıkçası {mention} kapsamlı değerlendirmede umut verici. {project['specialty']} teknoloji stack'i {project['focus']} alanındaki kritik ihtiyaçları karşılıyor. {random.choice(project['trends'])} gelişmesi pazar penetrasyonu artışı gösteriyor. {project['price_action']} değer keşfi süreci yansıtıyor. {project['ecosystem']} pozisyonu organik büyüme fırsatları yaratıyor."
            ]
        }
    
    selected_template = random.choice(fallback_templates[style])
    
    # Uzun çizgi temizlik
    selected_template = selected_template.replace('—', ' ')
    selected_template = selected_template.replace('–', ' ')
    selected_template = selected_template.replace('-', ' ')
    
    # Uzunluk kontrolü ve ayarlama
    if len(selected_template) < length_config['min']:
        # Çok kısa ise rastgele detay ekle
        random_additions = [
            f" {project['focus']} alan iyice kızışıyor.",
            f" bu projeyi takip etmek lazım.",
            f" {project['specialty']} konusu trending.",
            f" piyasa henüz fark etmedi.",
            f" yakında büyük hareket olabilir."
        ]
        selected_template += random.choice(random_additions)
    elif len(selected_template) > length_config['max']:
        # Çok uzun ise kısalt
        selected_template = selected_template[:length_config['max']-3] + "..."
    
    return selected_template

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
    """Tweet gönder"""
    url = "https://api.twitter.com/2/tweets"
    auth_header = create_oauth_header("POST", url)
    headers = {"Authorization": auth_header, "Content-Type": "application/json"}
    data = {"text": content}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        result = response.json()
        tweet_id = result['data']['id']
        print(f"✅ Tweet gönderildi!")
        print(f"📝 İçerik: {content}")
        print(f"🔗 Tweet ID: {tweet_id}")
        print(f"📊 Uzunluk: {len(content)} karakter")
        return True
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
    success = create_enhanced_tweet()
    if success:
        print("✅ Otomatik tweet tamamlandı!")
    else:
        print("❌ Otomatik tweet başarısız!")

def auto_bot():
    """7/24 otomatik bot"""
    print("🤖 Enhanced Kaito Twitter Bot v4 başlatılıyor...")
    
    # Twitter API testi
    if not test_twitter():
        print("❌ Twitter API bağlantısı başarısız! Bot durduruluyor.")
        return
    
    # İlk tweet'i hemen at
    print("🚀 İlk tweet atılıyor...")
    auto_tweet()
    
    # Schedule ayarla: Her 2-4 saatte bir rastgele
    schedule.every().hour.do(lambda: auto_tweet() if random.randint(1, 100) <= 30 else None)
    
    print("⏰ Bot schedule'ı ayarlandı: Her saat %30 ihtimalle tweet")
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