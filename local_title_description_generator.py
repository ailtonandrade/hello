import random
import datetime
from collections import deque


class LocalTitleDescriptionGenerator:
    def __init__(self):
        self.recent_titles = deque(maxlen=30)

        self.templates = {
            "universe_sleep": {
                "title_prefix": [
                    "🌌", "✨", "🌠", "🪐", "🔭", "🌙", "💫", "🛰️", "🌍", "☄️"
                ],
                "title_parts_a": [
                    "O universo explicado",
                    "Mistérios do cosmos",
                    "Viagem pelo espaço",
                    "Ciência do universo",
                    "Segredos do espaço profundo",
                    "O que existe além da Terra",
                    "Explorando o cosmos",
                    "Astronomia para relaxar",
                    "O infinito do universo",
                    "Fatos impressionantes do espaço",
                    "O silêncio do cosmos",
                    "O universo em detalhes",
                    "A imensidão do espaço",
                    "Ciência que acalma",
                    "O lado oculto do universo",
                    "Curiosidades espaciais",
                    "O universo à noite",
                    "O cosmos em perspectiva",
                    "Além das estrelas",
                    "A vastidão do infinito"
                ],
                "title_parts_b": [
                    "para relaxar",
                    "antes de dormir",
                    "em uma jornada cósmica",
                    "com ciência real",
                    "de forma simples",
                    "sem ficção exagerada",
                    "com explicação clara",
                    "em ritmo calmo",
                    "com narração suave",
                    "para acalmar a mente",
                    "para dormir melhor",
                    "com fatos científicos",
                    "em tom relaxante",
                    "para desacelerar",
                    "com curiosidades reais"
                ],
                "title_suffix": [
                    "| universo",
                    "| ciência",
                    "| espaço",
                    "| relaxante",
                    "| cosmos",
                    "| dormir melhor",
                    "| conhecimento",
                    "| astronômico"
                ],
                "description_opening": [
                    "🌌 Uma viagem tranquila pelo universo.",
                    "✨ Prepare a mente para explorar o cosmos.",
                    "🌙 Conteúdo calmo para relaxar antes de dormir.",
                    "🪐 Ciência, espaço e silêncio.",
                    "🔭 Um olhar profundo para o universo."
                ],
                "description_body": [
                    "Neste vídeo você embarca em uma jornada pelo universo.",
                    "Exploramos o espaço de forma simples e relaxante.",
                    "Fatos científicos explicados sem pressa.",
                    "Conteúdo ideal para acalmar a mente.",
                    "Astronomia apresentada de forma acessível.",
                    "Uma experiência tranquila e contemplativa.",
                    "Conhecimento que ajuda a desacelerar.",
                    "O universo como você nunca viu.",
                    "Ciência real, sem exageros.",
                    "Perfeito para ouvir antes de dormir."
                ],
                "description_cta": [
                    "Se isso te ajudou a relaxar, deixa o like 🌙\n\n📌 Conteúdo educativo baseado em ciência.\n\n",
                    "Segue o canal para mais viagens pelo universo ✨\n\n📌 Conteúdo educativo baseado em ciência.\n\n",
                    "Comenta qual parte do universo mais te impressiona 🌌\n\n📌 Conteúdo educativo baseado em ciência.\n\n",
                    "Salva esse vídeo para ouvir antes de dormir 🪐\n\n📌 Conteúdo educativo baseado em ciência.\n\n",
                    "Compartilha com quem ama ciência e espaço 🚀\n\n📌 Conteúdo educativo baseado em ciência.\n\n"
                ],
                "hashtags": [
                    "#universo",
                    "#espaco",
                    "#astronomia",
                    "#ciencia",
                    "#cosmos",
                    "#relaxar",
                    "#dormir",
                    "#universesleep"
                ]
            },
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
                    "Se isso te ajuda, deixa o like 👍 \n\n 📌 Conteúdo educacional. Não é recomendação financeira.\n\n",
                    "Segue o canal pra mais trades reais. \n\n 📌 Conteúdo educacional. Não é recomendação financeira.\n\n",
                    "Comenta se você faria diferente. \n\n 📌 Conteúdo educacional. Não é recomendação financeira.\n\n",
                    "Salva esse vídeo pra estudar depois. \n\n 📌 Conteúdo educacional. Não é recomendação financeira.\n\n",
                    "Compartilha com quem opera trade. \n\n 📌 Conteúdo educacional. Não é recomendação financeira.\n\n"
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
            },
            "pregacao": {
                "title_prefix": [
                    "📖", "🔥", "🕊️", "✝️", "🙏", "✨", "⏳", "🌿", "🧠", "📜"
                ],
                "title_parts_a": [
                    "Essa palavra é para você",
                    "Deus quer falar com você",
                    "Ouça isso com atenção",
                    "Uma verdade bíblica",
                    "Uma palavra direta do céu",
                    "Essa mensagem muda tudo",
                    "Poucos entendem essa passagem",
                    "Isso está na Bíblia",
                    "Essa revelação é profunda",
                    "Uma pregação necessária",
                    "Uma palavra de exortação",
                    "Uma palavra de consolo",
                    "Uma palavra de despertar",
                    "Uma palavra para este tempo",
                    "Uma verdade esquecida",
                    "Uma mensagem urgente",
                    "Uma lição espiritual",
                    "Uma palavra para os últimos dias",
                    "Uma reflexão bíblica",
                    "Uma palavra que confronta"
                ],
                "title_parts_b": [
                    "segundo a Palavra de Deus",
                    "à luz das Escrituras",
                    "baseada na Bíblia",
                    "que poucos pregam",
                    "que transforma vidas",
                    "para os dias de hoje",
                    "para fortalecer sua fé",
                    "para quem tem ouvidos para ouvir",
                    "para tempos difíceis",
                    "para quem está cansado",
                    "para quem está em dúvida",
                    "para quem busca a verdade",
                    "para quem quer crescer espiritualmente",
                    "para quem anda com Deus",
                    "para este tempo"
                ],
                "title_suffix": [
                    "| reflexão bíblica",
                    "| pregação curta",
                    "| palavra de Deus",
                    "| mensagem cristã",
                    "| estudo bíblico",
                    "| devocional",
                    "| ensino bíblico"
                ],
                "description_opening": [
                    "📖 A Palavra de Deus continua viva e eficaz.",
                    "🔥 Essa mensagem é forte, mas necessária.",
                    "🕊️ Que o Espírito Santo fale ao seu coração.",
                    "🙏 Ouça com atenção e coração aberto.",
                    "✨ Essa palavra pode mudar sua forma de ver as coisas."
                ],
                "description_body": [
                    "Nesta mensagem refletimos sobre um ensinamento bíblico essencial para a vida cristã.",
                    "A Bíblia nos mostra princípios que continuam válidos até hoje.",
                    "Essa palavra nos chama ao arrependimento, à fé e à obediência.",
                    "Aqui não há opinião humana, mas fundamento nas Escrituras.",
                    "Uma reflexão para alinhar nossa vida à vontade de Deus.",
                    "Essa mensagem confronta, exorta e edifica.",
                    "A Palavra de Deus revela, corrige e transforma.",
                    "Uma pregação simples, mas profunda.",
                    "Tudo deve ser analisado à luz da Bíblia.",
                    "Deus ainda fala por meio da Sua Palavra."
                ],
                "description_cta": [
                    "Se essa palavra falou com você, compartilhe 🙏",
                    "Deixe seu like para que essa mensagem alcance mais pessoas.",
                    "Comente o que Deus falou ao seu coração.",
                    "Salve esse vídeo para ouvir novamente.",
                    "Envie essa mensagem para alguém que precisa ouvir."
                ],
                "hashtags": [
                    "#biblia",
                    "#palavradedeus",
                    "#pregacao",
                    "#mensagembiblica",
                    "#fe",
                    "#jesus",
                    "#cristo",
                    "#evangelho",
                    "#devocional"
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
            + ""
            + hashtags
        )

        return {
            "title": title,
            "description": description
        }