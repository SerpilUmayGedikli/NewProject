# NLP Dönem Ödevi — LLM Tabanlı Çoklu-Ajan İşbirliği

Bu repo, verilen ödevdeki tüm bölümleri kapsayan çalışır bir Python + Web uygulaması içerir.

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Çalıştırma

### 1) Benchmark + değerlendirme
```bash
python -m bolum3_benchmark.benchmark_runner
python -m bolum4_degerlendirme.metrics
```

### 2) Web arayüzü (bahar temalı multi-agent dashboard)
```bash
python web/app.py
```
Ardından aşağıdaki adreslerden birini açın:
- `http://127.0.0.1:5000`
- `http://localhost:5000`

Eğer farklı host/port ile açmak isterseniz:
```bash
HOST=0.0.0.0 PORT=5001 python web/app.py
```

## İçerik
- Bölüm 1: Taksonomi modelleme + `classify()`
- Bölüm 2: Orkestrasyon motoru, 6 strateji
- Bölüm 3: 12 görevli mini benchmark
- Bölüm 4: TSR, TE, WCL, OQS, CEI, cost hesapları
- Bölüm 5: Analiz raporu (MD + PDF)
- Bonus: Web dashboard (dashboard, logs, analytics)

## Rapor
- Öğretim elemanı için rapor: `bolum5_rapor/rapor.md`
- PDF sürümü: `bolum5_rapor/rapor.pdf`
