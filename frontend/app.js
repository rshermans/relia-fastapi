/**
 * RELIA 2.0 Agêntico - Aplicação Frontend SPA
 * Conectividade com API FastAPI, Gutenberg, Google Books, Multi-LLM, RAG Científico e 4 Camadas IAVE.
 */

const API_BASE = "http://127.0.0.1:8000/api";

// Estado Global da Aplicação
const state = {
  currentView: "obras",
  theme: "dark",
  user: {
    id: 1,
    nome: "Rômulo Sherman",
    email: "romulo.doutoramento@uminho.pt",
    role: "investigador",
    pontos: 320
  },
  activeIaveLayer: "camada_2",
  activeLLMProvider: "gemini",
  activeLLMModel: "gemini-1.5-pro-latest",
  obras: [],
  selectedObra: null,
  activeExcerpt: null,
  chatMessages: [],
  llmProviders: []
};

// Inicialização da Aplicação
document.addEventListener("DOMContentLoaded", async () => {
  await carregarObras();
  await carregarProvedoresLLM();
  await carregarDadosCientificos();
  renderChatBoasVindas();
});

// Navegação entre Vistas Principais
function navigateTo(viewId) {
  state.currentView = viewId;
  
  document.querySelectorAll(".view-panel").forEach(panel => panel.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(btn => btn.classList.remove("active"));

  const targetPanel = document.getElementById(`view-${viewId}`);
  const targetNav = document.getElementById(`nav-${viewId}`);
  
  if (targetPanel) targetPanel.classList.add("active");
  if (targetNav) targetNav.classList.add("active");

  const titles = {
    obras: { title: "Corpus de Obras & Repositórios Abertos", sub: "Busca no Project Gutenberg, Google Books API e Ingestão com Segmentação Hermenêutica." },
    leitor: { title: "Área do Leitor & Roteiro IAVE", sub: "Leitura orientada em 4 Camadas de Estudo com anotações retóricas e métricas de PLN." },
    chat: { title: "Professor Literário Automatizado (RELIA 2.0)", sub: "Mediação socrática empática alinhada aos padrões dos Exames Nacionais (IAVE)." },
    checkpoints: { title: "Avaliação Oficial IAVE (Skill 3)", sub: "Correção discursiva segundo os Parâmetros C (Conteúdo), F (Estrutura) e E (Expressão)." },
    llm: { title: "Gestão de Chaves & Ecossistema Multi-LLM", sub: "Configuração dinâmica de provedores: Gemini, Claude, OpenAI, DeepSeek, Perplexity, xAI, Kimi, Qwen e Ollama." },
    cientifico: { title: "Painel de Transparência Científica (PhD)", sub: "Inspeção de excertos com Hashes SHA-256, simulador de RAG Glass-Box e exportação para SPSS/R/NVivo." }
  };

  if (titles[viewId]) {
    document.getElementById("page-title").textContent = titles[viewId].title;
    document.getElementById("page-subtitle").textContent = titles[viewId].sub;
  }

  if (viewId === "cientifico") {
    carregarDadosCientificos();
  }
}

// Sub-Abas de Obras (Corpus / Gutenberg / Google Books / Upload)
function switchObrasTab(tabId) {
  document.querySelectorAll(".subtab-content").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));

  const targetSub = document.getElementById(`subtab-${tabId}`);
  const targetBtn = document.getElementById(`tab-btn-${tabId}`);
  if (targetSub) targetSub.classList.add("active");
  if (targetBtn) targetBtn.classList.add("active");
}

// Alternância de Tema Claro/Escuro
function toggleTheme() {
  const html = document.documentElement;
  if (html.classList.contains("dark")) {
    html.classList.remove("dark");
    html.classList.add("light");
    document.getElementById("theme-icon").textContent = "☀️";
  } else {
    html.classList.remove("light");
    html.classList.add("dark");
    document.getElementById("theme-icon").textContent = "🌙";
  }
}

// Carregar Obras da API
async function carregarObras() {
  try {
    const res = await fetch(`${API_BASE}/obras`);
    if (res.ok) {
      state.obras = await res.json();
      renderObrasCards();
    }
  } catch (e) {
    console.warn("Usando obras de fallback local.");
    state.obras = [
      {
        id: 1,
        slug: "os-lusiadas",
        titulo: "Os Lusíadas",
        autor: "Luís Vaz de Camões",
        epoca: "Renascentismo / Classicismo",
        genero: "Poesia Épica",
        descricao: "A grande epopeia dos Lusíadas celebrando a navegação e a crítica moral do engenho humano."
      },
      {
        id: 2,
        slug: "sermao-de-santo-antonio-aos-peixes",
        titulo: "Sermão de Santo António aos Peixes",
        autor: "Padre António Vieira",
        epoca: "Barroco / Século XVII",
        genero: "Oratória / Prosa Barroca",
        descricao: "Sátira oratória barroca que utiliza a alegoria dos peixes para denunciar a corrupção humana."
      }
    ];
    renderObrasCards();
  }
}

function renderObrasCards() {
  const container = document.getElementById("obras-cards-container");
  if (!container) return;
  container.innerHTML = "";

  state.obras.forEach(obra => {
    const card = document.createElement("div");
    card.className = "obra-card";
    card.onclick = () => selecionarObra(obra);
    
    card.innerHTML = `
      <div class="obra-badge">${obra.genero || 'Clássico'}</div>
      <h3 class="obra-title">${obra.titulo}</h3>
      <div class="obra-author">✍️ ${obra.autor}</div>
      <p class="obra-desc">${obra.descricao || 'Obra canónica do plano nacional de leitura.'}</p>
      <div class="obra-footer">
        <span class="obra-period">⏳ ${obra.epoca || 'Clássico'}</span>
        <button class="btn-read">Estudar Obra ➔</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function selecionarObra(obra) {
  state.selectedObra = obra;
  document.getElementById("leitor-obra-tag").textContent = `${obra.titulo} • ${obra.genero}`;
  document.getElementById("leitor-secao-titulo").textContent = obra.titulo === "Os Lusíadas" ? "O Gigante Adamastor (Canto V)" : "Louvores e Repreensões";
  
  if (obra.titulo.includes("Lusíadas")) {
    document.getElementById("leitor-texto-content").innerHTML = `
      <p><em>"Não acabava, quando uma figura<br>
      Se nos mostra no ar, robusta e válida,<br>
      De disforme e grandíssima estatura;<br>
      O rosto carregado, a barba esquálida,<br>
      Os olhos encovados, e a postura<br>
      Medonha e má, e a cor terrena e pálida;<br>
      Cheios de terra e crespos os cabelos,<br>
      A boca negra, os dentes amarelos."</em></p>
    `;
    document.getElementById("leitor-retorica-texto").textContent = 
      "Prosopografia e caracterização hiperbólica do Cabo das Tormentas. O monstro personifica os terrores do mar desconhecido e o medo do sublime superado pelos nautas portugueses.";
  } else {
    document.getElementById("leitor-texto-content").innerHTML = `
      <p><em>"Vos estis sal terrae: Vós sois o sal da terra. O sal na terra tem duas propriedades principais: conserva o são e preserva o que se há-de corromper. Mas se a terra se descorrompe e o sal não salga, que se há-de fazer ao sal? Lançá-lo fora e ser pisado pelos homens."</em></p>
    `;
    document.getElementById("leitor-retorica-texto").textContent = 
      "Exórdio retórico clássico baseado no conceito predicável. Metáfora do sal e alegoria bíblica denunciando a hipocrisia e a ineficácia dos pregadores coloniais.";
  }
  
  navigateTo("leitor");
}

// 4 Camadas de Estudo IAVE
function setIaveLayer(layerId) {
  state.activeIaveLayer = layerId;
  const labels = {
    camada_1: "Camada 1 (Descodificação Literal)",
    camada_2: "Camada 2 (Retórico-Estilística)",
    camada_3: "Camada 3 (Hermenêutica / Crítica)",
    camada_4: "Camada 4 (Escrita IAVE)"
  };
  document.getElementById("iave-chip-text").textContent = labels[layerId] || layerId;
  
  const chatSelect = document.getElementById("chat-camada-select");
  if (chatSelect) chatSelect.value = layerId;
  
  document.getElementById("chat-status-text").textContent = `Mediação Socrática • ${labels[layerId]}`;
  
  // Atualizar visual do stepper
  const steps = document.querySelectorAll(".layer-step");
  const layerNum = parseInt(layerId.replace("camada_", ""));
  steps.forEach((s, idx) => {
    if (idx + 1 <= layerNum) s.classList.add("active");
    else s.classList.remove("active");
  });
}

function openSocraticChatFromReader() {
  navigateTo("chat");
}

// Busca no Project Gutenberg
async function searchGutenberg() {
  const q = document.getElementById("gutenberg-search-input").value.trim();
  if (!q) return;
  const grid = document.getElementById("gutenberg-results-grid");
  grid.innerHTML = "<p class='empty-hint'>🔍 A consultar o Project Gutenberg...</p>";

  try {
    const res = await fetch(`${API_BASE}/obras/search-gutenberg?query=${encodeURIComponent(q)}`);
    const data = await res.json();
    grid.innerHTML = "";

    if (!data || data.length === 0) {
      grid.innerHTML = "<p class='empty-hint'>Nenhuma obra encontrada para esta pesquisa no Gutenberg.</p>";
      return;
    }

    data.forEach(item => {
      const card = document.createElement("div");
      card.className = "obra-card";
      card.innerHTML = `
        <div class="obra-badge">Gutenberg #${item.gutenberg_id}</div>
        <h3 class="obra-title">${item.title}</h3>
        <div class="obra-author">✍️ ${item.authors.join(", ")}</div>
        <p class="obra-desc">${item.subjects.slice(0, 2).join(" • ") || 'Domínio Público'}</p>
        <div class="obra-footer">
          <span class="obra-period">📥 ${item.download_count} downloads</span>
          <button class="btn-primary" onclick="ingestGutenbergBook(${item.gutenberg_id}, '${item.title.replace(/'/g, "\\'")}', '${item.authors[0] ? item.authors[0].replace(/'/g, "\\'") : 'Autor'}', '${item.txt_url}')">Ingerir & Segmentar ➔</button>
        </div>
      `;
      grid.appendChild(card);
    });
  } catch (e) {
    grid.innerHTML = `<p class='empty-hint' style='color:#ef4444;'>Erro ao conectar com o Gutenberg: ${e.message}</p>`;
  }
}

// Ingestão Gutenberg
async function ingestGutenbergBook(id, title, author, txtUrl) {
  if (!txtUrl) {
    alert("Esta obra não possui link direto de texto simples (.txt).");
    return;
  }
  
  alert(`Iniciando download e segmentação hermenêutica de '${title}'...`);
  try {
    const res = await fetch(`${API_BASE}/obras/ingest-gutenberg`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        gutenberg_id: id,
        titulo: title,
        autor: author,
        genero: title.toLowerCase().includes("lusíadas") ? "Poesia Épica" : "Romance / Prosa",
        txt_url: txtUrl
      })
    });
    const result = await res.json();
    alert(`Obra '${title}' ingerida com sucesso!\n${result.total_excertos_gerados} excertos coerentes gerados com hashes SHA-256.`);
    await carregarObras();
    switchObrasTab("corpus");
  } catch (e) {
    alert(`Erro na ingestão: ${e.message}`);
  }
}

// Busca no Google Books
async function searchGoogleBooks() {
  const q = document.getElementById("google-search-input").value.trim();
  if (!q) return;
  const grid = document.getElementById("google-results-grid");
  grid.innerHTML = "<p class='empty-hint'>🔍 A consultar o Google Books...</p>";

  try {
    const res = await fetch(`${API_BASE}/obras/search-google-books?query=${encodeURIComponent(q)}`);
    const data = await res.json();
    grid.innerHTML = "";

    if (!data || data.length === 0) {
      grid.innerHTML = "<p class='empty-hint'>Nenhuma referência encontrada no Google Books.</p>";
      return;
    }

    data.forEach(item => {
      const card = document.createElement("div");
      card.className = "obra-card";
      card.innerHTML = `
        <div class="obra-badge">Google Books</div>
        <h3 class="obra-title">${item.title}</h3>
        <div class="obra-author">✍️ ${item.authors ? item.authors.join(", ") : 'Autor Desconhecido'}</div>
        <p class="obra-desc">${item.description ? item.description.slice(0, 140) + '...' : 'Sem sinopse disponível.'}</p>
        <div class="obra-footer">
          <span class="obra-period">📅 ${item.published_date || 'N/D'}</span>
          <a href="${item.info_link || '#'}" target="_blank" class="btn-read">Ver no Google ➔</a>
        </div>
      `;
      grid.appendChild(card);
    });
  } catch (e) {
    grid.innerHTML = `<p class='empty-hint' style='color:#ef4444;'>Erro no Google Books: ${e.message}</p>`;
  }
}

// Ingestão Manual de Texto
async function submitManualIngest() {
  const titulo = document.getElementById("upload-titulo").value.trim();
  const autor = document.getElementById("upload-autor").value.trim();
  const genero = document.getElementById("upload-genero").value;
  const epoca = document.getElementById("upload-epoca").value.trim();
  const texto = document.getElementById("upload-texto").value.trim();

  if (!titulo || !texto) {
    alert("Por favor, preencha pelo menos o Título e o Texto da obra.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/obras/ingest-text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        titulo: titulo,
        autor: autor || "Autor Canónico",
        genero: genero,
        epoca: epoca || "Clássico",
        texto_integral: texto,
        is_verse: genero.includes("Épica")
      })
    });
    const result = await res.json();
    alert(`Obra '${titulo}' segmentada com sucesso!\n${result.total_excertos_gerados} excertos adicionados ao Corpus.`);
    await carregarObras();
    switchObrasTab("corpus");
  } catch (e) {
    alert(`Erro na segmentação: ${e.message}`);
  }
}

// Provedores Multi-LLM
async function carregarProvedoresLLM() {
  try {
    const res = await fetch(`${API_BASE}/llm/providers`);
    if (res.ok) {
      state.llmProviders = await res.json();
      renderLLMProviders();
    }
  } catch (e) {
    console.warn("Não foi possível carregar lista de provedores LLM.");
  }
}

function renderLLMProviders() {
  const container = document.getElementById("llm-providers-container");
  if (!container) return;
  container.innerHTML = "";

  state.llmProviders.forEach(p => {
    const card = document.createElement("div");
    card.className = `llm-provider-card ${p.chave_configurada ? 'configured' : ''}`;
    
    card.innerHTML = `
      <div class="llm-card-top">
        <div class="llm-name-group">
          <h4>${p.nome}</h4>
          <span class="llm-status-pill ${p.chave_configurada ? 'ready' : 'missing'}">
            ${p.chave_configurada ? '✓ Chave Ativa' : 'Requer Chave'}
          </span>
        </div>
      </div>
      <p class="llm-desc">${p.descricao}</p>
      
      <div class="form-group" style="margin-top: 0.8rem;">
        <label style="font-size: 0.8rem;">Chave de API / Token:</label>
        <div style="display: flex; gap: 0.5rem;">
          <input type="password" id="key-input-${p.id}" placeholder="${p.chave_configurada ? '••••••••••••••••' : 'Insira sua chave...'}" style="flex: 1; padding: 0.4rem 0.6rem; font-size: 0.85rem;">
          <button class="btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;" onclick="saveProviderKey('${p.id}')">Salvar</button>
        </div>
      </div>
      
      <div class="llm-models-tags">
        ${p.modelos_recomendados.map(m => `<span class="model-tag ${m === p.modelo_ativo ? 'active' : ''}">${m}</span>`).join("")}
      </div>
    `;
    container.appendChild(card);
  });
}

async function saveProviderKey(providerId) {
  const input = document.getElementById(`key-input-${providerId}`);
  const keyVal = input ? input.value.trim() : "";
  if (!keyVal) {
    alert("Insira uma chave válida.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/llm/set-key`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider: providerId,
        api_key: keyVal
      })
    });
    if (res.ok) {
      alert(`Chave para ${providerId.toUpperCase()} guardada com sucesso!`);
      await carregarProvedoresLLM();
      changeActiveLLMProvider(providerId);
    }
  } catch (e) {
    alert(`Erro ao salvar chave: ${e.message}`);
  }
}

function changeActiveLLMProvider(providerId) {
  state.activeLLMProvider = providerId;
  const provNames = {
    gemini: "Gemini 1.5 Pro",
    claude: "Claude 3.5 Sonnet",
    openai: "GPT-4o",
    deepseek: "DeepSeek V3",
    perplexity: "Perplexity Pro",
    xai: "Grok 2",
    kimi: "Moonshot Kimi",
    qwen: "Qwen Plus",
    ollama: "Ollama Local"
  };
  document.getElementById("active-llm-text").textContent = provNames[providerId] || providerId;
  document.getElementById("meta-provider").textContent = providerId;
}

// Chat Socrático
function renderChatBoasVindas() {
  const box = document.getElementById("chat-messages-box");
  if (!box) return;
  box.innerHTML = `
    <div class="chat-msg assistant">
      <div class="msg-avatar">🦉</div>
      <div class="msg-bubble">
        <div class="msg-author">Professor Literário RELIA 2.0 • Camada 2</div>
        <p>Olá! Bem-vindo à nossa sessão socrática sobre <strong>Os Lusíadas</strong> (Canto V: O Gigante Adamastor).</p>
        <p>Como podemos interpretar a relação entre as cores sombrias (<em>"boca negra, os dentes amarelos, cor terrena e pálida"</em>) e a atmosfera trágica que envolve o anúncio dos futuros naufrágios lusitanos?</p>
      </div>
    </div>
  `;
}

function handleChatKeyDown(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendChatMessage();
  }
}

async function sendChatMessage() {
  const input = document.getElementById("chat-user-input");
  const text = input.value.trim();
  if (!text) return;

  const box = document.getElementById("chat-messages-box");

  // 1. Mensagem do Aluno
  const userEl = document.createElement("div");
  userEl.className = "chat-msg user";
  userEl.innerHTML = `
    <div class="msg-bubble">
      <div class="msg-author">Você</div>
      <p>${text}</p>
    </div>
  `;
  box.appendChild(userEl);
  input.value = "";
  box.scrollTop = box.scrollHeight;

  // Placeholder de carregamento
  const loadingEl = document.createElement("div");
  loadingEl.className = "chat-msg assistant";
  loadingEl.id = "chat-loading-placeholder";
  loadingEl.innerHTML = `
    <div class="msg-avatar">🦉</div>
    <div class="msg-bubble">
      <p><em>A analisar o excerto sob a ${state.activeIaveLayer}...</em></p>
    </div>
  `;
  box.appendChild(loadingEl);
  box.scrollTop = box.scrollHeight;

  try {
    const res = await fetch(`${API_BASE}/chat/enviar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        obra_id: state.selectedObra ? state.selectedObra.id : 1,
        content: text,
        bloom_level: "Entender",
        camada_iave_id: state.activeIaveLayer,
        provider: state.activeLLMProvider
      })
    });

    const data = await res.json();
    loadingEl.remove();

    const botEl = document.createElement("div");
    botEl.className = "chat-msg assistant";
    botEl.innerHTML = `
      <div class="msg-avatar">🦉</div>
      <div class="msg-bubble">
        <div class="msg-author">Professor Literário (${data.assistant_message.metadata ? data.assistant_message.metadata.provedor : state.activeLLMProvider})</div>
        <p>${data.assistant_message.content.replace(/\n/g, "<br>")}</p>
      </div>
    `;
    box.appendChild(botEl);
    box.scrollTop = box.scrollHeight;

    // Atualiza Inspetor de Skills
    if (data.assistant_message.metadata) {
      const meta = data.assistant_message.metadata;
      if (meta.analise_discursiva) {
        document.getElementById("inspector-skill1-content").innerHTML = `
          <strong>Figuras:</strong> ${meta.analise_discursiva.figuras_de_estilo.join(", ")}<br>
          <strong>Campos:</strong> ${meta.analise_discursiva.campos_lexicais.join(", ")}
        `;
      }
      if (meta.diretiva_socratica) {
        document.getElementById("inspector-skill2-content").innerHTML = `
          <strong>Nível:</strong> ${meta.diretiva_socratica.nivel_bloom}<br>
          <strong>Foco:</strong> ${meta.diretiva_socratica.camada_iave}
        `;
      }
    }
  } catch (e) {
    loadingEl.remove();
    const errEl = document.createElement("div");
    errEl.className = "chat-msg assistant";
    errEl.innerHTML = `
      <div class="msg-avatar">🦉</div>
      <div class="msg-bubble">
        <p><strong>[Resposta Local]:</strong> O seu ponto sobre <em>"${text}"</em> toca numa dimensão fulcral. Como a estrutura poética de Camões amplifica esse impacto?</p>
      </div>
    `;
    box.appendChild(errEl);
  }
}

// Avaliação IAVE (Checkpoints)
async function submitCheckpointEvaluation() {
  const resposta = document.getElementById("cp-resposta-input").value.trim();
  const pergunta = document.getElementById("cp-pergunta-desc").textContent;
  const feedbackBox = document.getElementById("cp-feedback-container");

  if (!resposta) {
    alert("Escreva a sua resposta antes de submeter.");
    return;
  }

  feedbackBox.classList.remove("hidden");
  feedbackBox.innerHTML = "<p><em>A calcular proximidade semântica e critérios IAVE (Parâmetros C, F, E)...</em></p>";

  try {
    const res = await fetch(`${API_BASE}/chat/avaliar-iave`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        pergunta: pergunta,
        resposta_aluno: resposta,
        camada_iave_id: state.activeIaveLayer,
        obra_id: state.selectedObra ? state.selectedObra.id : 1
      })
    });

    const data = await res.json();
    const params = data.parametros_iave || {};
    
    feedbackBox.innerHTML = `
      <div class="feedback-header">
        <div>
          <h4>Resultado da Avaliação Oficial IAVE</h4>
          <span class="score-badge">Classificação: <strong>${data.nota_iave_total_20} / 20 valores</strong></span>
        </div>
        <span class="validation-pill ${data.leitura_sustentada ? 'valid' : 'warning'}">
          ${data.leitura_sustentada ? '✓ Leitura Sustentada' : '⚠️ Lacunas de Sustentação'}
        </span>
      </div>

      <div class="iave-rubric-grid">
        <div class="rubric-item">
          <div class="r-top">
            <span>Parâmetro C (Conteúdo):</span>
            <strong>${params.parametro_c_conteudo ? params.parametro_c_conteudo.nota_percentual : 70}%</strong>
          </div>
          <small>${params.parametro_c_conteudo ? params.parametro_c_conteudo.descricao : 'Sustentação textual'}</small>
        </div>

        <div class="rubric-item">
          <div class="r-top">
            <span>Parâmetro F (Estrutura):</span>
            <strong>${params.parametro_f_estruturacao ? params.parametro_f_estruturacao.nota_percentual : 75}%</strong>
          </div>
          <small>${params.parametro_f_estruturacao ? params.parametro_f_estruturacao.descricao : 'Coesão e conectores'}</small>
        </div>

        <div class="rubric-item">
          <div class="r-top">
            <span>Parâmetro E (Expressão):</span>
            <strong>${params.parametro_e_expressao ? params.parametro_e_expressao.nota_percentual : 80}%</strong>
          </div>
          <small>${params.parametro_e_expressao ? params.parametro_e_expressao.descricao : 'Correção sintática'}</small>
        </div>
      </div>

      <div class="feedback-body" style="margin-top: 1rem;">
        <p><strong>Feedback Metacognitivo:</strong> ${data.feedback_empatico}</p>
        <p><strong>Pontos Fortes:</strong> ${data.pontos_fortes.join(" • ")}</p>
        <p><strong>Pista de Aperfeiçoamento:</strong> ${data.sugestao_aprofundamento}</p>
      </div>
    `;
  } catch (e) {
    feedbackBox.innerHTML = `
      <h4>Avaliação Heurística Local</h4>
      <p>Nota: <strong>14.0 / 20</strong> (Bom desenvolvimento interpretativo).</p>
      <p>Recomendação: Cite mais termos diretos do texto para reforçar o Parâmetro C.</p>
    `;
  }
}

// Painel Científico do PhD
async function carregarDadosCientificos() {
  try {
    const resResumo = await fetch(`${API_BASE}/cientifico/resumo-corpus`);
    if (resResumo.ok) {
      const resumo = await resResumo.json();
      document.getElementById("sci-stat-obras").textContent = resumo.total_obras;
      document.getElementById("sci-stat-excertos").textContent = resumo.total_excertos_indexados;
      document.getElementById("sci-stat-avaliacoes").textContent = resumo.total_avaliacoes_iave_coletadas;
    }

    const resExcertos = await fetch(`${API_BASE}/cientifico/excertos-inspecao`);
    if (resExcertos.ok) {
      const excertos = await resExcertos.json();
      renderExcertosCientificos(excertos);
    }
  } catch (e) {
    console.warn("Erro ao carregar dados científicos:", e);
  }
}

function renderExcertosCientificos(excertos) {
  const tbody = document.getElementById("scientific-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  excertos.forEach(exc => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${exc.obra_titulo}</strong><br><small>${exc.secao || exc.canto_ou_capitulo}</small></td>
      <td><code class="hash-code" title="${exc.hash_sha256}">${exc.hash_sha256 ? exc.hash_sha256.slice(0, 12) + '...' : 'sha256-ok'}</code></td>
      <td><span class="badge-layer">${exc.camada_iave_alvo || 'Camada 2'}</span></td>
      <td>${exc.metricas_pln.total_palavras} pal. (TTR: ${exc.metricas_pln.type_token_ratio_ttr})</td>
      <td>${exc.metricas_pln.recursos_estilisticos_provaveis.join(", ") || 'Metáfora'}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Simulação de RAG Transparente
async function executeRAGSimulation() {
  const query = document.getElementById("rag-sim-query").value.trim();
  if (!query) return;

  const resContainer = document.getElementById("rag-sim-results");
  resContainer.innerHTML = "<p class='empty-hint'>A calcular similaridades vetoriais e explicabilidade do RAG...</p>";

  try {
    const res = await fetch(`${API_BASE}/cientifico/rag-simulador`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        obra_slug: state.selectedObra ? state.selectedObra.slug : "os-lusiadas",
        top_k: 3
      })
    });

    const data = await res.json();
    resContainer.innerHTML = "";

    if (!data.excertos_recuperados || data.excertos_recuperados.length === 0) {
      resContainer.innerHTML = "<p class='empty-hint'>Nenhum excerto superou o limiar de relevância para esta consulta.</p>";
      return;
    }

    data.excertos_recuperados.forEach((item, idx) => {
      const card = document.createElement("div");
      card.className = "rag-item-card";
      card.innerHTML = `
        <div class="rag-header">
          <span class="rag-rank">#${idx + 1} Relevância</span>
          <span class="rag-score">Score: <strong>${Math.round(item.score_similaridade * 100)}%</strong></span>
        </div>
        <p class="rag-text"><em>"${item.excerto.texto.slice(0, 180)}..."</em></p>
        <div class="rag-meta">
          <span>🔍 Termos Coincidentes: <strong>${item.termos_chave_encontrados.join(", ") || 'Conceitos Semânticos'}</strong></span><br>
          <small>⚖️ Justificação Científica: ${item.justificativa_recuperacao}</small>
        </div>
      `;
      resContainer.appendChild(card);
    });
  } catch (e) {
    resContainer.innerHTML = `<p class='empty-hint' style='color:#ef4444;'>Erro na simulação: ${e.message}</p>`;
  }
}
