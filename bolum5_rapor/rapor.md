# LLM Tabanlı Çoklu-Ajan İşbirliği Sistemleri: Tasarım, Uygulama ve Değerlendirme

## 1. Giriş
Bu çalışma, tek-ajan ve çoklu-ajan orkestrasyon stratejilerini aynı görev havuzu üzerinde kıyaslayarak hangi yaklaşımın hangi problem sınıfında daha verimli olduğunu göstermeyi amaçlar. Temel motivasyon, yalnızca doğruluk değil; aynı zamanda token maliyeti, gecikme ve işbirliği verimliliğini birlikte değerlendirmektir.

## 2. Yöntem ve Sistem Tasarımı
### 2.1 Stratejiler
Uygulanan stratejiler:
- Solo (S1)
- Solo + Self-Refinement (S1+)
- Sequential Chain (S3)
- Hierarchical (S4)
- Debate (S5)
- Majority Voting (S6)

### 2.2 Orkestrasyon Motoru
`Orchestrator`, seçilen stratejiye göre ajanları konfigüre eder, görevi çalıştırır, her tur mesajını loglar ve `OrchestratorResult` üretir.

### 2.3 Benchmark Seti
Toplam 12 görev kullanılmıştır (T1–T4; tier başına 3 görev):
- T1: atomik, kesin cevaplı
- T2: çok adımlı bileşik
- T3: çelişkili bilgi ve kritik düşünme
- T4: yaratıcı/açık uçlu

## 3. Değerlendirme Metrikleri
- **TSR:** Task Success Rate
- **TE:** Token Expenditure
- **WCL:** Wall-Clock Latency
- **OQS:** Output Quality Score (1–10)
- **CEI:** Collaboration Efficiency Index

CEI formülü:

`CEI = w1*TSR_norm + w2*OQS_norm - w3*TE_norm - w4*WCL_norm`

Ağırlık profilleri:
1. Dengeli: (0.25, 0.25, 0.25, 0.25)
2. Kalite odaklı: (0.4, 0.3, 0.15, 0.15)
3. Maliyet odaklı: (0.2, 0.2, 0.3, 0.3)

## 4. Deney Sonuçları
Çalıştırma çıktılarından özet:
- **Balanced CEI:** Solo ve Sequential Chain yüksek skor aldı.
- **Quality CEI:** Hierarchical daha güçlü performans gösterdi.
- **Cost-focused CEI:** Solo en avantajlı strateji oldu.

Cost-per-success değerlendirmesinde düşük koordinasyon maliyeti nedeniyle Solo ve Majority Voting daha ekonomik davrandı.

## 5. Tartışma
1. **Hangi strateji hangi görevde iyi?**
   - T1/T2: Solo veya Sequential daha hızlı/ekonomik.
   - T3: Debate ve Hierarchical, çelişkili bilgi analizinde daha kontrollü.
   - T4: Hierarchical, rol dağılımı sayesinde daha bütünlüklü çıktı üretiyor.

2. **Debate etkisi:**
   Debate yaklaşımı kaliteyi artırsa da ek tur mesajlaşma token maliyetini ve gecikmeyi yükseltiyor.

3. **S1+ karşılaştırması:**
   Self-refinement bazı görevlerde çoklu-ajan kalitesine yaklaşsa da her iterasyon maliyeti artırdığı için maliyet odaklı senaryolarda dezavantaj oluşabiliyor.

4. **Maliyet-performans:**
   Uygulama çıktılarında en iyi maliyet-performans dengesi Solo / Sequential bileşiminde gözlendi.

## 6. Pratik Öneriler
- **Hızlı ve ucuz cevap:** Solo
- **Çok adımlı mühendislik işi:** Sequential Chain
- **Çelişkili kaynak sentezi:** Debate + Judge
- **Yaratıcı ve kapsamlı üretim:** Hierarchical
- **Bütçe kritik üretim ortamı:** Dinamik strateji seçimi (task-aware routing)

## 7. Sonuç
Çoklu-ajan mimariler, görev sınıfına bağlı olarak belirgin kazanç sağlayabilmektedir. Ancak bu kazanç, koordinasyon maliyeti ve latency ile birlikte düşünülmelidir. En iyi sonuç, tek bir stratejiye sabitlenmek yerine problem tipine göre strateji uyarlayan hibrit orkestrasyon yaklaşımıyla elde edilir.

## 8. AI Kullanım Beyanı
Bu projede taslak kod üretimi, doküman yapısı ve hızlı prototipleme için AI destekli araçlar kullanılmıştır. Nihai doğrulama, düzenleme ve raporlaştırma manuel olarak tamamlanmıştır.
