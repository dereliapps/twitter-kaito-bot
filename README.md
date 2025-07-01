# 🤖 Enhanced Crypto Twitter Bot

Crypto projeler hakkında doğal ve insan gibi tweet atan otomatik bot.

## 🚀 Özellikler

- **6 Crypto Projesi**: Anoma, Camp Network, Virtuals, Somnia, Union, Mitosis
- **7 Tweet Tipi**: Teknik analiz, keşfetme, piyasa görüşü, karşılaştırma, deneyim, soru, gelecek tahmini
- **ChatGPT-4o-mini**: Doğal dil ile tweet üretimi
- **Rate Limiting**: Günde 5 tweet, 2.5 saat aralık
- **Analytics**: Tweet performans takibi
- **Auto Reply**: Mention'lara otomatik yanıt
- **Thread Support**: Uzun analiz zincirleri

## 📊 Tweet Örnekleri

**Önceki AI dili:**
> "Ekosistem için önemli bir adım olan Virtuals Io, volatilite riski göz önünde bulundurulmalı..."

**Yeni doğal dil:**
> "Bence Mitosis ilerleyen zamanlarda dikkat çekebilir. Merakla takip ediyorum!"

## ⚙️ Kurulum

### Lokal Geliştirme

1. Repository'yi klonla
```bash
git clone <repo-url>
cd crypto-twitter-bot
```

2. Dependencies yükle
```bash
pip install -r requirements.txt
```

3. Environment variables ayarla
```bash
# .env dosyası oluştur
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_token_secret
OPENAI_API_KEY=your_openai_key
```

4. Botu çalıştır
```bash
python bot.py              # Normal mod
python bot.py test          # Test mod (tweet atmaz)
python bot.py analytics     # Analytics raporu
```

### 🚀 Heroku Deployment

1. Heroku uygulaması oluştur
```bash
heroku create your-bot-name
```

2. Environment variables ayarla
```bash
heroku config:set TWITTER_API_KEY=your_key
heroku config:set TWITTER_API_SECRET=your_secret
heroku config:set TWITTER_ACCESS_TOKEN=your_token
heroku config:set TWITTER_ACCESS_SECRET=your_token_secret
heroku config:set OPENAI_API_KEY=your_openai_key
```

3. Deploy et
```bash
git push heroku main
```

4. Worker'ı başlat
```bash
heroku ps:scale worker=1
```

## 🔑 API Keys

### Twitter API
1. [Twitter Developer Portal](https://developer.twitter.com/)
2. App oluştur
3. API Key, Secret, Access Token al

### OpenAI API  
1. [OpenAI Platform](https://platform.openai.com/)
2. API Key oluştur
3. GPT-4o-mini erişimi olduğundan emin ol

## 🛠️ Yapılandırma

### Tweet Ayarları
```python
MINIMUM_INTERVAL = 2.5 * 60 * 60  # 2.5 saat
DAILY_TWEET_COUNT = 5              # Günlük limit
TWEET_START_HOUR = 10              # Başlangıç saati
TWEET_END_HOUR = 22                # Bitiş saati
```

### Proje Ekleme
```python
projects = {
    "yeni_proje": {
        "mention": "@yeni_proje",
        "focus": "teknoloji alanı",
        "specialty": "özel özellik",
        # ... diğer alanlar
    }
}
```

## 📈 Analytics

Bot otomatik olarak şu verileri toplar:
- Tweet performansı (1 saat, 24 saat, 7 gün)
- Engagement oranları
- Proje bazlı istatistikler

Veriler `tweet_analytics.json` dosyasında saklanır.

## 🔒 Güvenlik

- ✅ API keyler environment variables'da
- ✅ .env dosyası .gitignore'da
- ✅ Hard-coded secret yok
- ✅ Rate limiting ile API koruması

## 🎯 Kullanım Modları

```bash
python bot.py              # Otomatik sürekli çalışma
python bot.py test          # Test tweet oluştur (gönderme)
python bot.py analytics     # Performans raporu
python bot.py mentions      # Mention kontrolü
```

## 🤝 Katkıda Bulunma

1. Fork et
2. Feature branch oluştur (`git checkout -b feature/amazing-feature`)
3. Commit et (`git commit -m 'Add amazing feature'`)
4. Push et (`git push origin feature/amazing-feature`)
5. Pull Request aç

## 📄 Lisans

MIT License

## ⚠️ Uyarılar

- Twitter API rate limitlerini gözetle
- OpenAI usage limitlerini takip et
- Bot'u spam için kullanma
- Authentic engagement sağla

---

**Made with ❤️ for the crypto community** 