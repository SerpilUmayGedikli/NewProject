from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Agent:
    name: str
    role: str
    system_prompt: str

    def respond(self, prompt: str) -> str:
        snippet = prompt[:180].replace("\n", " ")
        if self.role == "planner":
            return f"[{self.name}] Plan: 1) Analiz et 2) Çözüm üret 3) Kontrol et. Görev: {snippet}"
        if self.role == "critic":
            return f"[{self.name}] Eleştiri: Varsayımları doğrula, uç durumları ele al. İncelenen içerik: {snippet}"
        if self.role == "judge":
            return f"[{self.name}] Karar: Tutarlılık ve doğruluk yüksek cevabı seçiyorum."
        if self.role == "coder":
            return f"[{self.name}] Kod önerisi: modüler fonksiyonlar ve testlenebilir yapı önerilir."
        return f"[{self.name}] ({self.role}) Yanıt: {snippet}"
