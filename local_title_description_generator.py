import random
import datetime
from collections import deque


class LocalTitleDescriptionGenerator:
    def __init__(self):
        self.recent_titles = deque(maxlen=30)

        self.templates = {
            "trade": {
                "title_prefix": [
                    "🔥", "🚀", "⚡", "📉", "📈", "💥", "🎯", "🧠", "💰", "⏱️"
                ],
                "title_parts_a": [
                    "Trader iniciante",
                    "Trader profissional",
                    "Day trade na prática",
                    "Scalping insano",
                    "Trade ao vivo",
                    "Operação real",
                    "Setup simples",
                    "Estratégia vencedora",
                    "Trade psicológico",
                    "Gestão de risco",
                    "Trade consciente",
                    "Operação rápida",
                    "Trade inteligente",
                    "Trade disciplinado",
                    "Trade de alta probabilidade",
                    "Trade agressivo",
                    "Trade avançado",
                    "Trade sem achismo",
                    "Trade validado",
                    "Trade no limite"
                ],
                "title_parts_b": [
                    "no mini índice",
                    "no dólar futuro",
                    "no day trade",
                    "em mercado volátil",
                    "em tempo real",
                    "sem emoção",
                    "com leitura de fluxo",
                    "com price action",
                    "com gestão sólida",
                    "sem indicador mágico",
                    "sem promessa falsa",
                    "com estratégia clara",
                    "com foco total",
                    "sem overtrade",
                    "com disciplina extrema"
                ],
                "title_suffix": [
                    "| trade real",
                    "| sem achismo",
                    "| operação ao vivo",
                    "| psicológico forte",
                    "| execução limpa",
                    "| foco total",
                    "| sem enrolação",
                    "| vida real"
                ],
                "description_opening": [
                    "🚨 Operação real acontecendo agora.",
                    "⚠️ Isso é trade de verdade, não é simulação.",
                    "📊 Mercado aberto, decisão tomada.",
                    "🧠 Aqui a mente importa mais que o indicador.",
                    "🎯 Trade curto, rápido e direto."
                ],
                "description_body": [
                    "Neste vídeo você acompanha uma operação real no mercado financeiro.",
                    "Mostro exatamente como penso antes, durante e depois da entrada.",
                    "Nada de promessa de ganhos fáceis, apenas execução consciente.",
                    "Trade focado em probabilidade e gestão de risco.",
                    "Leitura de mercado aplicada em tempo real.",
                    "Controle emocional acima de tudo.",
                    "Operação sem pressa e sem ansiedade.",
                    "Execução baseada em cenário, não em achismo.",
                    "Processo completo de uma decisão no trade.",
                    "Trade realista, sem filtros."
                ],
                "description_cta": [
                    "Se isso te ajuda, deixa o like 👍",
                    "Segue o canal pra mais trades reais.",
                    "Comenta se você faria diferente.",
                    "Salva esse vídeo pra estudar depois.",
                    "Compartilha com quem opera trade."
                ],
                "hashtags": [
                    "#daytrade",
                    "#scalping",
                    "#trader",
                    "#mercadofinanceiro",
                    "#priceaction",
                    "#miniindice",
                    "#dolarfuturo",
                    "#trade"
                ]
            }
        }

    def _unique_title(self, build_func):
        for _ in range(20):
            title = build_func()
            if title not in self.recent_titles:
                self.recent_titles.append(title)
                return title
        return title

    def generate(self, theme: str):
        theme = theme.lower()

        if theme not in self.templates:
            return {
                "title": "Conteúdo em desenvolvimento",
                "description": "Tema ainda não configurado."
            }

        data = self.templates[theme]

        def build_title():
            prefix = random.choice(data["title_prefix"])
            part_a = random.choice(data["title_parts_a"])
            part_b = random.choice(data["title_parts_b"])
            suffix = random.choice(data["title_suffix"]) if random.random() > 0.4 else ""
            return f"{prefix} {part_a} {part_b} {suffix}".strip()

        title = self._unique_title(build_title)

        opening = random.choice(data["description_opening"])
        body = random.sample(data["description_body"], k=random.randint(2, 3))
        cta = random.choice(data["description_cta"])

        hashtags = " ".join(random.sample(data["hashtags"], k=5))
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        description = (
            f"{opening}\n\n"
            + " ".join(body)
            + f"\n\n{cta}\n\n"
            + f"⏱️ Gravado às {timestamp}\n\n"
            + "📌 Conteúdo educacional. Não é recomendação financeira.\n\n"
            + hashtags
        )

        return {
            "title": title,
            "description": description
        }
