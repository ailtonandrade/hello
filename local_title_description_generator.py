import random
import datetime
from collections import deque


class LocalTitleDescriptionGenerator:
    def __init__(self):
        self.recent_titles = deque(maxlen=30)

        self.templates = {
            "mentalidade_investidor": {
                "title_prefix": [
                    "💰", "📈", "🧠", "🔥", "👀", "🚀", "⚠️", "💥", "🎯", "🤯"
                ],
                "title_parts_a": [
                    "Decisão silenciosa",
                    "Erro que custa caro",
                    "Mentalidade que separa ricos da massa",
                    "Padrão que se repete na história",
                    "Escolha que muda o jogo",
                    "Atitude que poucos têm",
                    "Momento ignorado pela maioria",
                    "Comportamento que cria riqueza",
                    "Pensamento que atravessa gerações",
                    "Diferença entre reagir e planejar",
                    "O detalhe que ninguém observa",
                    "Quando o emocional decide tudo",
                    "A paciência venceu",
                    "O erro que todo iniciante comete",
                    "A vantagem de pensar diferente",
                    "O hábito que constrói fortuna",
                    "A armadilha mais comum",
                    "O preço da pressa",
                    "O poder de esperar",
                    "O jogo invisível do dinheiro"
                ],
                "title_parts_b": [
                    "em tempos de crise",
                    "quando todos entram em pânico",
                    "enquanto a maioria desiste",
                    "em ciclos que sempre se repetem",
                    "quando o mercado testa os fracos",
                    "nos momentos de incerteza",
                    "quando ninguém quer olhar",
                    "em decisões de longo prazo",
                    "enquanto o barulho domina",
                    "quando o medo fala mais alto",
                    "em fases de correção",
                    "quando o risco parece alto",
                    "nos bastidores da riqueza",
                    "quando poucos têm coragem",
                    "em momentos que definem destinos"
                ],
                "title_suffix": [
                    "| poucos entendem",
                    "| isso muda tudo",
                    "| pensa nisso",
                    "| não é sobre sorte",
                    "| repare nesse padrão",
                    "| a história prova",
                    "| quase ninguém percebe",
                    "| isso se repete sempre"
                ],
                "description_opening": [
                    "💰 Isso já aconteceu antes.",
                    "📈 A história não mente.",
                    "🧠 Pouca gente presta atenção nisso.",
                    "⚠️ Aqui está o erro mais comum.",
                    "👀 Olha esse padrão."
                ],
                "description_body": [
                    "Ao longo do tempo, o comportamento se repete.",
                    "Enquanto muitos reagem, poucos observam.",
                    "A diferença está na decisão silenciosa.",
                    "O dinheiro segue quem pensa no longo prazo.",
                    "O emocional cobra um preço alto.",
                    "A maioria age tarde demais.",
                    "Quem entende os ciclos age diferente.",
                    "O barulho distrai, a estratégia constrói.",
                    "Toda crise testa a mentalidade.",
                    "Não é sobre acertar sempre, é sobre sobreviver."
                ],
                "description_cta": [
                    "Isso faz sentido pra você? 👇",
                    "Você já percebeu esse padrão? 👇",
                    "Salva esse vídeo pra lembrar disso 🔖",
                    "Poucos falam sobre isso.",
                    "Segue o canal pra mais ideias reais 💰"
                ],
                "hashtags": [
                    "#mentalidademilionaria",
                    "#investidor",
                    "#educacaofinanceira",
                    "#riquezasilenciosa",
                    "#longoprazo",
                    "#dinheiro",
                    "#financas",
                    "#menteinvestidora",
                    "#liberdadefinanceira"
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