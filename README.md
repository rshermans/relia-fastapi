# RELIA 2.0 - Roteiro de Leitura Empática e Interativa com Agentes

Plataforma agêntica para mediação leitora no ensino secundário e investigação em **Ciências da Linguagem / Humanidades Digitais** (CEHUM / Universidade do Minho).

O projeto reorienta o sistema clássico para um ecossistema agêntico desacoplado, local-first, com **FastAPI**, **SQLite Local**, **Servidor MCP (Model Context Protocol)** e a formalização das **3 Skills Agênticas Fundamentais do Doutoramento**.

---

## 🏛️ Arquitetura das 3 Skills Agênticas Fundamentais

| Skill Agêntica | Competência Linguístico-Discursiva | Mecanismo de Execução Autónomo |
| :--- | :--- | :--- |
| **Skill 1: Extrator Discursivo** | Análise estilística e retórica de excertos de *Os Lusíadas* e *Sermão de Santo António*. | Identificação de figuras de estilo (anástrofe, antítese, metáfora, hipérbole), estruturas sintáticas e índices léxicos via spaCy/PLN. |
| **Skill 2: Formulador Socrático** | Geração de perguntas interpretativas graduadas pela Taxonomia de Bloom. | Invocação RAG sobre corpus de exames nacionais e excertos canónicos, formulando questões abertas que preservam a ambiguidade hermenêutica. |
| **Skill 3: Avaliador Metacognitivo** | Análise de respostas abertas dos alunos e feedback empático-formativo. | Cálculo de proximidade semântica (text embeddings), identificação de lacunas argumentativas e validação de leituras divergentes sustentadas. |

---

## 📂 Estrutura do Repositório (Monorepo Modular)

```
reliia/
├── backend/                      # API Backend FastAPI & Orquestrador Agêntico
│   ├── app/
│   │   ├── main.py               # Entrypoint FastAPI com CORS
│   │   ├── config.py             # Configurações e provedores de LLM
│   │   ├── database/             # Modelos SQLAlchemy e sessão SQLite local
│   │   │   ├── models.py
│   │   │   └── seed_database.py  # Sementeira das obras e roteiros
│   │   ├── api/                  # Endpoints REST (auth, obras, leitor, chat, checkpoints, admin)
│   │   ├── skills/               # As 3 Skills Agênticas
│   │   │   ├── extrator_discursivo.py
│   │   │   ├── formulador_socratico.py
│   │   │   └── avaliador_metacognitivo.py
│   │   ├── agents/               # Orquestrador Multi-Agente e Cliente MCP
│   │   └── services/             # LLM Service (Gemini, OpenAI, Claude, Ollama)
│   ├── tests/                    # Testes unitários com pytest
│   └── requirements.txt
├── mcp_servers/                  # Servidor MCP de Corpus Literário
│   └── corpus_server/
│       └── server.py             # Servidor FastMCP com ferramentas de obras e exames
├── data/                         # Bases de dados locais e corpus
│   ├── relia_local.db            # SQLite local
│   └── seed_corpus/              # Corpus canónico e itens de exames
├── frontend/                     # Interface Web Moderna (SPA)
│   ├── index.html
│   ├── style.css
│   └── app.js
└── docs/                         # Documentação científica do PhD
```

---

## 🚀 Como Executar

### Opção A: Modo Local (Scripts Automatizados)
* **Iniciar**: execute o ficheiro [Agente-Relia.bat](file:///d:/NOVAS-Aplicações/app-phd-mestrado/reliia/Agente-Relia.bat) (Windows) ou `Agente-Relia.sh` (Linux/macOS).
* **Parar**: execute o ficheiro [Parar-Relia.bat](file:///d:/NOVAS-Aplicações/app-phd-mestrado/reliia/Parar-Relia.bat) (Windows) ou `Parar-Relia.sh` (Linux/macOS).

### Opção B: Modo Docker Compose (Contentorizado)
* **Iniciar**: execute o ficheiro [Agente-Relia-Docker.bat](file:///d:/NOVAS-Aplicações/app-phd-mestrado/reliia/Agente-Relia-Docker.bat) ou `docker compose up -d --build`.
* **Parar**: execute o ficheiro [Parar-Relia-Docker.bat](file:///d:/NOVAS-Aplicações/app-phd-mestrado/reliia/Parar-Relia-Docker.bat) ou `docker compose down`.

---

## 🌐 Endereços de Acesso
- **Frontend SPA**: `http://localhost:3030`
- **Backend API**: `http://127.0.0.1:8000`
- **Documentação Swagger (OpenAPI)**: `http://127.0.0.1:8000/docs`

---

## 🧪 Executar a Suite de Testes
```bash
python -m pytest backend/tests/ -v
```
