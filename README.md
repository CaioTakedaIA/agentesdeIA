# Plataforma de Analise de Dados Groq + LangGraph
> Nivel Senior / Consultor - Solucao Over-Engineered

Plataforma unificada e robusta orientada a agentes autonomos para validacao, reparo e analise de datasets CSV. Construida em Arquitetura Hexagonal (Ports & Adapters) combinada com Domain-Driven Design (DDD), Server-sent Events (SSE) e paralelismo de CPU para alta performance.

---

## Decisoes Arquiteturais e Padroes (Over-Engineering)

O sistema foi meticulosamente projetado para ser escalavel, resiliente e de facil manutenibilidade:

1. **Clean Architecture & Ports/Adapters**: O dominio central (`models.py` e `ports.py`) e completamente isolado. A comunicacao com recursos externos (Groq LLM) e feita exclusivamente atraves de injecao de dependencia na camada de Adapters (`llm_service.py`), permitindo a troca transparente do motor de Inteligencia Artificial subjacente.
2. **LangGraph State Machine**: Em vez de fluxos imperativos lineares de LLM, o backend implementa um **Grafo Direcionado Aciclico (DAG)**. O grafo possui edge-routing condicional, avaliando o estado polimorfico gerado pelo `ValidatorAgent` para determinar iterativamente o desvio para o no de correcao (Fixer).
3. **Paralelismo por ThreadPool**: Considerando o gargalo de IO intenso durante o reparo assincrono do LLM, as rotinas de limpeza implementam submissao map/reduce e `ThreadPoolExecutor` (Node Concurrency), reduzindo a latencia da pipeline de "O(N)" arquivos de upload para quase O(1) de tempo de parede.
4. **Protecao Anti-Hallucination & RAG Reversa**: Ao inves do convencional vetor search (RAG) que e ineficaz para tabelas estritas, desenvolvemos a extracao de resumos estatisticos (via `Pandas`) mais uma modelagem de restricao amostral de LLM. O Chatbot foi calibrado com Guardrails hermeticos limitados pelo proprio contexto.
5. **Comunicacao Reactiva (Event-Bus SSE)**: O monolito REST puro foi transformado. As rotas HTTP convencionais ativam eventos via `asyncio.Queue` no servidor que empurram relatorios bidirecionais WebSocket/SSE para o React sem overhead de polling.

---

## Tecnologias Utilizadas

### Backend (Inteligencia & Orquestracao)
- **Python 3.11+** com Tipagem Forte
- **FastAPI / Uvicorn**: API de altissima performance para as rotas e WebSockets (SSE).
- **LangGraph**: Controle de fluxo de agentes em formato de grafo.
- **Groq API**: Interface ultra-rapida (LPU) consumindo modelo `llama-3.1-8b-instant`.
- **Pandas**: Motor de manipulacao em memoria para calculos analiticos de seguranca.

### Frontend (Dashboard Interativo)
- **React 18 + Vite**: Otimizacao maxima de bundle size e Hot-Module Replacement.
- **Tailwind CSS v3**: Estilizacao altamente customizavel com Design System sombrio, glassmorphism e responsividade profunda.
- **Lucide Icons**: Pacotes vetoriais consistentes.
- **Context API**: Gerenciamento de estado global otimizado evitando "prop-drilling" e mitigando rerenders nas abas.

---

## Como os Agentes Funcionam (O Pipeline LangGraph)

O backend é movido por um grafo dinâmico que orquestra 3 agentes autônomos. Quando você faz o upload de um CSV, o seguinte fluxo acontece na mesma hora:

1. **Agente Validador**: O porteiro inicial. Ele recebe o arquivo original bruto (em formato de texto) e tenta convertê-lo e validá-lo contra um schema rígido. 
   - Se o arquivo for perfeito e os valores baterem (*ex: apenas números em 'value'*), ele **valida** o documento e pula direto para o Fim, liberando o ChatBot.
   - Se os números estiverem com aspas embutidas, vírgulas invertidas ou datas estranhas, ele emite um alerta de "CSV Corrompido" e encaminha para o corretor.
2. **Agente Corretor**: O engenheiro de dados. Pega o relatório de falhas do Validador e limpa o dataset ativamente.
   - Ele conserta campos errados e arranca aspas literais invisíveis.
   - Aplica a **Política de Zero Descarte**: Nunca joga linhas fora. Nulos são substituídos por defaults para não perder métricas vitais.
   - Após as correções, manda os dados polidos de volta para...
3. **Revalidação**: O Agente Validador checa ativamente o resultado do trabalho do Agente Corretor e atesta que o arquivo sobreviveu ao processo, liberando o ChatBot.
4. **Agente Analista (ChatBot)**: Baseado estritamente nas linhas extraídas e higienizadas, ele se tranca na política de "Zero-Hallucination" (Alucinação Zero), respondendo no chat apenas perguntas sobre o dataset que foi recém parseado.

---

## Onde pegar os CSVs para testar?

Criamos arquivos propositais para você torturar e avaliar a máquina. Eles estão localizados na pasta `data/` na raiz deste projeto:

- `data/csv_correto.csv`: Totalmente limpo. Se você jogá-lo no Dashboard, passará instantaneamente pelo Agente Validador sem pestanejar.
- `data/csv_erroschema.csv`: Arquivo intencionalmente corrompido, com cabeçalhos bagunçados e formatações financeiras terríveis (`"""R$ 150,50"""`). Jogar isso na plataforma força o motor do Agente Corretor a suar a camisa para formatar os padrões sem descartar as linhas!

 Basta arrastar e soltar da sua pasta `data` direto pro navegador!

---

## Instrucoes de Deploy e Build

Para garantir a reproducao isolada do repositorio finalizado:

### 1. Requisitos Previos
* **Python** `>= 3.11`
* **Node.js** `>= 18` (e `npm`)
* Chave ativa da **Groq API** (Gratuita via console.groq.com)

### 2. Configuracao do Backend (FastAPI)
Abra um terminal na raiz do projeto e instale o ambiente virtual:
```bash
# Crie e ative o ambiente virtual
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale os requerimentos
pip install -r requirements.txt

# Configure as variaveis de ambiente
cp .env.example .env
# Edite o .env para adicionar sua GROQ_API_KEY
```

> **Para executar a aplicacao FastAPI:**
```bash
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

---

### 3. Configuracao do Frontend (Dashboard)
Em uma **nova aba** de terminal, acesse a pasta do frontend e instale as bibliotecas JavaScript:

```bash
cd dashboard
npm install

# Para rodar a Interface Grafica:
npm run dev
```

A aplicacao devera rodar perfeitamente em: `http://localhost:5173`. 
Qualquer upload de CSV pela aba de "Analise Interativa" sera transportado assincronamente e o estado da pipeline pode ser inspecionada no hub de "Monitoramento LangGraph".

---

## Integracao Continua e Validacao da Solucao

Como padrao de boas praticas focadas em integracao e design modular pre-implantacao, os testes automatizados da pasta dev (arquivos mock, stubs locais e caches) foram ejetados antes do empacotamento, resultando em repositorios menores e compativeis estritamente com dados reais do cliente e producao.

Como testar os limites do Grafo agora:
1. Acesse o **Frontend** na URL citada no Console.
2. Faca Upload de CSVs. Baseado na Arquitetura Orientada a Eventos a API orquestrara a conversacao via SSE validando Schemas faltantes na mesma hora.
3. Chatbot Interativo: O framework injetou as respostas LLM no context da aplicacao para conversacoes determinisitas sem risco de off-topics.





