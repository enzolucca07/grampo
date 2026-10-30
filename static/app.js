// Grampo: a tela. Monta os cartões, recebe os arquivos, mostra as páginas e acompanha o andamento.
"use strict";

const G = window.GRAMPO;
const $ = (seletor, raiz = document) => raiz.querySelector(seletor);
const POR_ID = Object.fromEntries(G.ferramentas.map((f) => [f.id, f]));

const ICONES = {
  juntar: '<path d="M8 3h7l4 4v8"/><path d="M15 3v4h4"/><path d="M5 8h7l3 3v10H5z"/><path d="M8 15h4M10 13v4"/>',
  dividir: '<path d="M6 3h8l4 4v4"/><path d="M14 3v4h4"/><path d="M6 3v8"/><path d="M3 14h18" stroke-dasharray="2 2.5"/><path d="M6 17v4h12v-4"/>',
  extrair: '<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4"/><path d="M12 10v7M9 14l3 3 3-3"/>',
  excluir: '<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4"/><path d="M9.5 11.5l5 5M14.5 11.5l-5 5"/>',
  reordenar: '<rect x="4" y="3" width="7" height="8" rx="1.5"/><rect x="13" y="13" width="7" height="8" rx="1.5"/><path d="M15 4h2a2 2 0 0 1 2 2v3M17 7l2 2 2-2"/><path d="M9 20H7a2 2 0 0 1-2-2v-3M7 17l-2-2-2 2"/>',
  girar: '<path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 4v7h-7"/>',
  comprimir: '<path d="M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7"/>',
  marca: '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/><path d="M9.5 15a2.5 2.5 0 0 0 2.5 2.5"/>',
  numerar: '<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4"/><path d="M10 13h4M10 16.5h4M11 11l-.6 7.5M13.6 11 13 18.5"/>',
  word_pdf: '<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4"/><path d="M8.5 11l1.2 6 1.8-4.5 1.8 4.5 1.2-6"/>',
  excel_pdf: '<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4"/><path d="M9 11l5 6M14 11l-5 6"/>',
  powerpoint_pdf: '<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4"/><path d="M10 18v-7h2.5a2 2 0 0 1 0 4H10"/>',
  imagem_pdf: '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M21 16l-5-5-9 9"/>',
  texto_pdf: '<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4"/><path d="M9 11h6M9 14h6M9 17h4"/>',
  pdf_jpg: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 15l5-5 4 4 3-3 6 6"/><circle cx="16" cy="8.5" r="1.5"/>',
  pdf_word: '<path d="M4 7h7M4 11h5M4 15h4"/><path d="M13 5h8v14h-8z"/><path d="M14.5 9l1 5 1.5-3.5 1.5 3.5 1-5"/>',
  pdf_excel: '<path d="M4 7h7M4 11h5M4 15h4"/><path d="M13 5h8v14h-8z"/><path d="M15 9l4 6M19 9l-4 6"/>',
  pdf_powerpoint: '<path d="M4 7h7M4 11h5M4 15h4"/><path d="M13 5h8v14h-8z"/><path d="M15.5 15V9h2a1.8 1.8 0 0 1 0 3.6h-2"/>',
  pdf_texto: '<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4"/><path d="M9 11h6M12 11v7"/>',
  extrair_imagens: '<rect x="3" y="7" width="14" height="13" rx="2"/><path d="M3 16l4-4 3 3 2-2 5 5"/><path d="M14 3h7v7M21 3l-6 6"/>',
  proteger: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/><path d="M12 15v2"/>',
  desproteger: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 7.5-2"/><path d="M12 15v2"/>',
};
const SVG = (miolo) => `<svg viewBox="0 0 24 24" aria-hidden="true">${miolo}</svg>`;
const SIMBOLOS = {
  cima: '<path d="M18 15l-6-6-6 6"/>', baixo: '<path d="M6 9l6 6 6-6"/>', fechar: '<path d="M6 6l12 12M18 6L6 18"/>',
  alca: '<circle cx="9" cy="6" r="1"/><circle cx="15" cy="6" r="1"/><circle cx="9" cy="12" r="1"/><circle cx="15" cy="12" r="1"/><circle cx="9" cy="18" r="1"/><circle cx="15" cy="18" r="1"/>',
  horario: '<path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 4v7h-7"/>',
  antihorario: '<path d="M4 11a8 8 0 1 1 2.3 5.7"/><path d="M4 4v7h7"/>',
  check: '<path d="M5 12l5 5 9-10"/>', ok: '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
  erro: '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16.5v.01"/>',
  abrir: '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
  pasta: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  esquerda: '<path d="M15 18l-6-6 6-6"/>', direita: '<path d="M9 18l6-6-6-6"/>',
};
const icone = (nome) => SVG(SIMBOLOS[nome]);

const estado = {
  ferramenta: null, arquivos: [], marcadas: new Set(), giros: {}, ordem: [], ocupado: false, terminou: false,
};
let ambiente = { pasta: "", padrao: "", programas: {} };

// ------------------------------------------------------------------ utilidades

function escapar(texto) {
  return String(texto).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function semAcento(texto) {
  return texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}
function tamanho(bytes) {
  const unidades = ["bytes", "KB", "MB", "GB"];
  let i = 0;
  while (bytes >= 1024 && i < unidades.length - 1) { bytes /= 1024; i++; }
  return (i === 0 ? bytes : bytes.toFixed(1).replace(".", ",")) + " " + unidades[i];
}
function plural(n, um, varios) { return `${n} ${n === 1 ? um : varios}`; }
function nomeDaPasta(caminho) { return caminho.split(/[\\/]/).filter(Boolean).pop() || caminho; }

async function api(url, dados) {
  const resposta = await fetch(url, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Grampo": G.chave },
    body: JSON.stringify(dados || {}),
  });
  const json = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(json.erro || "Não consegui falar com o Grampo. Feche e abra de novo.");
  return json;
}

// ------------------------------------------------------------------ início

function corDoGrupo(elemento, grupo) {
  elemento.style.setProperty("--cor-grupo", `var(--g-${grupo})`);
  elemento.style.setProperty("--fundo-grupo", `var(--g-${grupo}-f)`);
}

function montarInicio() {
  const raiz = $("#grupos");
  raiz.innerHTML = "";
  for (const [grupo, titulo] of G.grupos) {
    const secao = document.createElement("section");
    secao.className = "grupo";
    secao.dataset.grupo = grupo;
    secao.innerHTML = `<h2>${escapar(titulo)}</h2><div class="cartoes"></div>`;
    for (const f of G.ferramentas.filter((f) => f.grupo === grupo)) {
      const cartao = document.createElement("button");
      cartao.type = "button";
      cartao.className = "cartao";
      cartao.dataset.id = f.id;
      cartao.dataset.busca = semAcento(`${f.titulo} ${f.descricao} ${f.aceita.join(" ")}`);
      corDoGrupo(cartao, grupo);
      cartao.innerHTML = `<span class="cartao-icone">${SVG(ICONES[f.id])}</span>
        <h3>${escapar(f.titulo)}</h3><p>${escapar(f.descricao)}</p>`;
      cartao.addEventListener("click", () => { location.hash = "#/" + f.id; });
      $(".cartoes", secao).appendChild(cartao);
    }
    raiz.appendChild(secao);
  }
  marcarProgramasQueFaltam();
}

function marcarProgramasQueFaltam() {
  for (const f of G.ferramentas.filter((f) => f.precisa)) {
    const cartao = document.querySelector(`.cartao[data-id="${f.id}"]`);
    if (!cartao) continue;
    $(".selo", cartao)?.remove();
    if (ambiente.programas && ambiente.programas[f.precisa] === null) {
      cartao.insertAdjacentHTML("beforeend", '<span class="selo">Precisa do Office</span>');
    }
  }
}

function filtrar() {
  const termos = semAcento($("#busca").value).split(/\s+/).filter(Boolean);
  let algum = false;
  for (const secao of document.querySelectorAll(".grupo")) {
    let visiveis = 0;
    for (const cartao of secao.querySelectorAll(".cartao")) {
      const mostra = termos.every((t) => cartao.dataset.busca.includes(t));
      cartao.hidden = !mostra;
      visiveis += mostra;
    }
    secao.hidden = visiveis === 0;
    algum ||= visiveis > 0;
  }
  $("#sem-resultado").hidden = algum;
}

// ------------------------------------------------------------------ navegação

function rota() {
  const id = location.hash.replace(/^#\/?/, "");
  if (estado.ocupado) return;
  if (POR_ID[id]) abrirFerramenta(POR_ID[id]);
  else {
    estado.ferramenta = null;
    $("#ferramenta").hidden = true;
    $("#inicio").hidden = false;
    document.title = "Grampo";
  }
  window.scrollTo(0, 0);
}

function abrirFerramenta(f) {
  Object.assign(estado, { ferramenta: f, arquivos: [], marcadas: new Set(), giros: {}, ordem: [], terminou: false });
  $("#inicio").hidden = true;
  $("#ferramenta").hidden = false;
  document.title = `${f.titulo} · Grampo`;
  corDoGrupo($("#f-icone"), f.grupo);
  $("#f-icone").innerHTML = SVG(ICONES[f.id]);
  $("#f-titulo").textContent = f.titulo;
  $("#f-descricao").textContent = f.descricao;
  const entrada = $("#escolher");
  entrada.accept = f.aceita.join(",");
  entrada.multiple = !!f.varios;
  $("#soltar-titulo").textContent = f.varios ? "Arraste os arquivos para cá" : "Arraste o arquivo para cá";
  $("#soltar-aceita").textContent = "Aceita: " + f.aceita.map((e) => e.slice(1).toUpperCase()).join(", ");
  avisoDoPrograma();
  montarOpcoes(f);
  $("#andamento").hidden = true;
  $("#resultado").hidden = true;
  desenhar();
}

function avisoDoPrograma() {
  const f = estado.ferramenta, aviso = $("#f-aviso-programa");
  aviso.hidden = true;
  if (!f || !f.precisa || !ambiente.programas) return;
  const programa = ambiente.programas[f.precisa];
  if (programa === null) {
    aviso.innerHTML = `<strong>Falta um programa neste computador</strong>Para converter estes arquivos o Grampo usa o
      Microsoft Office ou o LibreOffice (gratuito), e nenhum dos dois foi encontrado. Peça para a TI instalar um deles.`;
    aviso.hidden = false;
  }
}

// ------------------------------------------------------------------ opções

function montarOpcoes(f) {
  const form = $("#opcoes");
  form.innerHTML = "";
  for (const o of f.opcoes || []) {
    let html = "";
    const id = `op-${o.nome}`;
    const ajuda = o.ajuda ? `<small>${escapar(o.ajuda)}</small>` : "";
    if (o.tipo === "escolha") {
      html = `<fieldset class="campo"><legend>${escapar(o.rotulo)}</legend><div class="escolhas">` +
        o.valores.map(([valor, rotulo]) => `<label class="escolha"><input type="radio" name="${o.nome}" value="${escapar(valor)}"
          ${String(valor) === String(o.padrao) ? "checked" : ""}> ${escapar(rotulo)}</label>`).join("") +
        `</div>${ajuda}</fieldset>`;
    } else if (o.tipo === "marcar") {
      html = `<label class="marcar"><input type="checkbox" name="${o.nome}" ${o.padrao ? "checked" : ""}> ${escapar(o.rotulo)}</label>`;
    } else if (o.tipo === "faixa") {
      html = `<label class="campo"><span>${escapar(o.rotulo)}</span><span class="faixa">
        <input type="range" name="${o.nome}" min="${o.minimo}" max="${o.maximo}" step="${o.passo}" value="${o.padrao}"
          ${o.porcento ? 'data-porcento="1"' : ""}><output></output></span>${ajuda}</label>`;
    } else {
      const tipo = o.tipo === "senha" ? "password" : o.tipo === "numero" ? "number" : "text";
      html = `<label class="campo" for="${id}"><span>${escapar(o.rotulo)}</span>
        <input id="${id}" type="${tipo}" name="${o.nome}" value="${escapar(o.padrao ?? "")}"
          ${o.exemplo ? `placeholder="Ex.: ${escapar(o.exemplo)}"` : ""} ${o.minimo != null ? `min="${o.minimo}"` : ""}>${ajuda}</label>`;
    }
    const caixa = document.createElement("div");
    caixa.dataset.opcao = o.nome;
    caixa.innerHTML = html;
    form.appendChild(caixa);
  }
  atualizarOpcoes();
}

function atualizarOpcoes() {
  const f = estado.ferramenta, valores = lerOpcoes();
  for (const o of f.opcoes || []) {
    const caixa = document.querySelector(`[data-opcao="${o.nome}"]`);
    if (o.se) caixa.hidden = !Object.entries(o.se).every(([nome, valor]) => String(valores[nome]) === String(valor));
  }
  for (const faixa of document.querySelectorAll("#opcoes input[type=range]")) {
    const v = Number(faixa.value);
    faixa.nextElementSibling.textContent = faixa.dataset.porcento ? `${Math.round(v * 100)}%` : v;
  }
}

function lerOpcoes() {
  const f = estado.ferramenta, valores = {};
  for (const o of f.opcoes || []) {
    if (o.tipo === "escolha") valores[o.nome] = $(`#opcoes input[name="${o.nome}"]:checked`)?.value;
    else if (o.tipo === "marcar") valores[o.nome] = $(`#opcoes input[name="${o.nome}"]`).checked;
    else if (o.tipo === "numero" || o.tipo === "faixa") valores[o.nome] = Number($(`#opcoes input[name="${o.nome}"]`).value);
    else valores[o.nome] = $(`#opcoes input[name="${o.nome}"]`).value;
  }
  if (f.paginas === "girar") valores.giros = estado.giros;
  if (f.paginas === "ordenar") valores.ordem = estado.ordem;
  return valores;
}

// ------------------------------------------------------------------ arquivos

function aceito(nome) {
  const ext = "." + nome.split(".").pop().toLowerCase();
  return estado.ferramenta.aceita.includes(ext);
}

function enviar(lista) {
  const f = estado.ferramenta;
  if (!f || estado.ocupado) return;
  let arquivos = [...lista];
  const recusados = arquivos.filter((a) => !aceito(a.name));
  arquivos = arquivos.filter((a) => aceito(a.name));
  if (recusados.length) {
    mostrarErro(`${recusados.map((a) => `“${a.name}”`).join(", ")} não ${recusados.length > 1 ? "servem" : "serve"} aqui. ` +
      `Esta ferramenta aceita: ${f.aceita.map((e) => e.slice(1).toUpperCase()).join(", ")}.`);
  }
  if (!arquivos.length) return;
  if (!f.varios) arquivos = arquivos.slice(0, 1);
  const dados = new FormData();
  arquivos.forEach((a) => dados.append("arquivos", a, a.name));
  const pedido = new XMLHttpRequest();
  pedido.open("POST", "/api/enviar");
  pedido.setRequestHeader("X-Grampo", G.chave);
  ocupar(true);
  progresso(0, arquivos.length > 1 ? `Carregando ${arquivos.length} arquivos` : `Carregando ${arquivos[0].name}`);
  pedido.upload.onprogress = (e) => { if (e.lengthComputable) progresso(e.loaded / e.total * 0.95); };
  pedido.onload = () => {
    ocupar(false);
    $("#andamento").hidden = true;
    if (pedido.status !== 200) { mostrarErro("Não consegui carregar os arquivos. Tente de novo."); return; }
    if (!recusados.length) $("#resultado").hidden = true;
    const recebidos = JSON.parse(pedido.responseText);
    estado.arquivos = f.varios ? estado.arquivos.concat(recebidos) : recebidos;
    estado.terminou = false;
    if (f.paginas) prepararPaginas();
    desenhar();
  };
  pedido.onerror = () => { ocupar(false); mostrarErro("Não consegui carregar os arquivos. Tente de novo."); };
  pedido.send(dados);
}

function prepararPaginas() {
  const a = estado.arquivos[0];
  estado.marcadas = new Set();
  estado.giros = {};
  estado.ordem = a && a.paginas ? [...Array(a.paginas).keys()] : [];
  const campo = $('#opcoes input[name="paginas"]');
  if (campo) campo.value = "";
}

function problemaDe(a) {
  const f = estado.ferramenta;
  if (a.problema) return a.problema;
  if (a.senha && f.id === "proteger") return "Este PDF já tem senha.";
  if (a.senha && f.id !== "desproteger") return "Tem senha: use antes a ferramenta “Tirar senha”.";
  return "";
}

function detalheDe(a) {
  const partes = [tamanho(a.tamanho)];
  if (a.paginas) partes.push(plural(a.paginas, "página", "páginas"));
  if (a.senha) partes.push("com senha");
  return partes.join(" · ");
}

function desenhar() {
  const f = estado.ferramenta;
  const tem = estado.arquivos.length > 0;
  const soltar = $("#soltar");
  soltar.hidden = tem && !f.varios;
  soltar.classList.toggle("compacto", tem);
  if (tem && f.varios) $("#soltar-titulo").textContent = "Adicionar mais arquivos";
  desenharLista();
  desenharPaginas();
  atualizarBotao();
}

function desenharLista() {
  const f = estado.ferramenta, lista = $("#lista");
  lista.hidden = !estado.arquivos.length;
  lista.innerHTML = "";
  const ordenavel = f.varios && estado.arquivos.length > 1;
  estado.arquivos.forEach((a, i) => {
    const item = document.createElement("div");
    item.className = "item" + (ordenavel ? " arrastavel" : "");
    item.draggable = ordenavel;
    const problema = problemaDe(a);
    const capa = a.paginas ? `style="background-image:url('/api/miniatura/${a.id}/0?largura=80')"` : "";
    item.innerHTML = `
      ${ordenavel ? `<span class="item-alca" title="Arraste para mudar a ordem">${icone("alca")}</span>` : ""}
      <span class="item-capa" ${capa}>${a.paginas ? "" : escapar(a.nome.split(".").pop().toUpperCase())}</span>
      <div class="item-info"><div class="item-nome" title="${escapar(a.nome)}">${escapar(a.nome)}</div>
        <div class="item-detalhe ${problema ? "problema" : ""}">${escapar(problema || detalheDe(a))}</div></div>
      <div class="item-acoes">
        ${ordenavel ? `<button class="mini-botao" type="button" data-acao="subir" title="Subir" ${i === 0 ? "disabled" : ""}>${icone("cima")}</button>
        <button class="mini-botao" type="button" data-acao="descer" title="Descer" ${i === estado.arquivos.length - 1 ? "disabled" : ""}>${icone("baixo")}</button>` : ""}
        <button class="mini-botao" type="button" data-acao="tirar" title="${f.varios ? "Tirar da lista" : "Trocar o arquivo"}">${icone("fechar")}</button>
      </div>`;
    item.addEventListener("click", (e) => {
      const acao = e.target.closest("[data-acao]")?.dataset.acao;
      if (!acao || estado.ocupado) return;
      if (acao === "tirar") estado.arquivos.splice(i, 1);
      if (acao === "subir") mover(estado.arquivos, i, i - 1);
      if (acao === "descer") mover(estado.arquivos, i, i + 1);
      if (acao === "tirar" && f.paginas) prepararPaginas();
      estado.terminou = false;
      $("#resultado").hidden = true;
      desenhar();
    });
    if (ordenavel) arrastarParaOrdenar(item, i, estado.arquivos, desenhar);
    lista.appendChild(item);
  });
}

function mover(lista, de, para) {
  if (para < 0 || para >= lista.length || de === para) return;
  const [elemento] = lista.splice(de, 1);
  lista.splice(para, 0, elemento);
}

let arrastandoDe = null;
function arrastarParaOrdenar(elemento, indice, lista, depois) {
  elemento.addEventListener("dragstart", (e) => {
    arrastandoDe = indice;
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/x-grampo", String(indice));
    elemento.classList.add("arrastado");
  });
  elemento.addEventListener("dragend", () => {
    arrastandoDe = null;
    elemento.classList.remove("arrastado");
    document.querySelectorAll(".solto-aqui").forEach((el) => el.classList.remove("solto-aqui"));
  });
  elemento.addEventListener("dragover", (e) => {
    if (arrastandoDe === null) return;
    e.preventDefault();
    e.stopPropagation();
    elemento.classList.add("solto-aqui");
  });
  elemento.addEventListener("dragleave", () => elemento.classList.remove("solto-aqui"));
  elemento.addEventListener("drop", (e) => {
    if (arrastandoDe === null) return;
    e.preventDefault();
    e.stopPropagation();
    mover(lista, arrastandoDe, indice);
    arrastandoDe = null;
    estado.terminou = false;
    $("#resultado").hidden = true;
    depois();
  });
}

// ------------------------------------------------------------------ páginas (marcar, girar, ordenar)

function textoDasMarcadas() {
  const nums = [...estado.marcadas].sort((a, b) => a - b).map((n) => n + 1);
  const partes = [];
  for (let i = 0; i < nums.length; i++) {
    let j = i;
    while (j + 1 < nums.length && nums[j + 1] === nums[j] + 1) j++;
    partes.push(j > i ? `${nums[i]}-${nums[j]}` : `${nums[i]}`);
    i = j;
  }
  return partes.join(", ");
}

function lerMarcadasDoTexto(texto, total) {
  const marcadas = new Set();
  for (const parte of texto.split(/[,;]/)) {
    const m = parte.trim().match(/^(\d*)\s*(?:-|a|até)?\s*(\d*)$/);
    if (!m || (!m[1] && !m[2])) continue;
    const temFaixa = /-|a|até/.test(parte);
    let de = Number(m[1] || 1), ate = temFaixa ? Number(m[2] || total) : de;
    if (de > ate) [de, ate] = [ate, de];
    for (let n = de; n <= Math.min(ate, total); n++) if (n >= 1) marcadas.add(n - 1);
  }
  return marcadas;
}

function desenharPaginas() {
  const f = estado.ferramenta, area = $("#paginas"), a = estado.arquivos[0];
  area.hidden = !(f.paginas && a && a.paginas && !problemaDe(a));
  if (area.hidden) return;
  area.className = `paginas-area modo-${f.paginas === "marcar" ? (f.id === "excluir" ? "excluir" : "marcar") : f.paginas}`;
  const barra = $("#paginas-barra"), grade = $("#grade");
  const total = a.paginas;
  if (f.paginas === "marcar") {
    const verbo = f.id === "excluir" ? "tirar" : "copiar";
    barra.innerHTML = `<span class="contagem">${estado.marcadas.size ? `${plural(estado.marcadas.size, "página marcada", "páginas marcadas")} para ${verbo}` : `Clique nas páginas para ${verbo}`}</span>
      <button class="botao" type="button" data-acao="todas">Marcar todas</button>
      <button class="botao" type="button" data-acao="nenhuma">Desmarcar</button>`;
  } else if (f.paginas === "girar") {
    const giradas = Object.values(estado.giros).filter((g) => g % 360).length;
    barra.innerHTML = `<span class="contagem">${giradas ? plural(giradas, "página girada", "páginas giradas") : "Use as setas embaixo de cada página"}</span>
      <button class="botao" type="button" data-acao="todas-anti">${icone("antihorario")} Todas</button>
      <button class="botao" type="button" data-acao="todas-horario">${icone("horario")} Todas</button>
      <button class="botao fantasma" type="button" data-acao="desfazer" ${giradas ? "" : "disabled"}>Desfazer</button>`;
  } else {
    const mudou = estado.ordem.some((p, i) => p !== i);
    barra.innerHTML = `<span class="contagem">Arraste as páginas (ou use as setas) para mudar a ordem</span>
      <button class="botao" type="button" data-acao="inverter">Inverter</button>
      <button class="botao fantasma" type="button" data-acao="original" ${mudou ? "" : "disabled"}>Ordem original</button>`;
  }
  barra.onclick = (e) => {
    const acao = e.target.closest("[data-acao]")?.dataset.acao;
    if (!acao || estado.ocupado) return;
    if (acao === "todas") estado.marcadas = new Set(Array(total).keys());
    if (acao === "nenhuma") estado.marcadas = new Set();
    if (acao === "todas-horario" || acao === "todas-anti") {
      for (let p = 0; p < total; p++) estado.giros[p] = ((estado.giros[p] || 0) + (acao === "todas-horario" ? 90 : 270)) % 360;
    }
    if (acao === "desfazer") estado.giros = {};
    if (acao === "inverter") estado.ordem.reverse();
    if (acao === "original") estado.ordem = [...Array(total).keys()];
    sincronizarCampoPaginas();
    desenharPaginas();
    atualizarBotao();
  };

  grade.innerHTML = "";
  const sequencia = f.paginas === "ordenar" ? estado.ordem : [...Array(total).keys()];
  sequencia.forEach((p, posicao) => {
    const cartao = document.createElement("div");
    cartao.className = "pagina";
    const giro = estado.giros[p] || 0;
    if (f.paginas === "marcar" && estado.marcadas.has(p)) cartao.classList.add("marcada");
    if (giro % 360) cartao.classList.add("girada");
    const escala = giro % 180 ? " scale(.78)" : "";
    let rodape = `<span class="pagina-numero">${p + 1}</span>`;
    if (f.paginas === "girar") {
      rodape = `<div class="pagina-giros">
        <button class="mini-botao" type="button" data-giro="270" title="Girar para a esquerda">${icone("antihorario")}</button>
        <span class="pagina-numero" style="align-self:center">${p + 1}</span>
        <button class="mini-botao" type="button" data-giro="90" title="Girar para a direita">${icone("horario")}</button></div>`;
    } else if (f.paginas === "ordenar") {
      rodape = `<div class="pagina-giros">
        <button class="mini-botao" type="button" data-mover="-1" title="Mais para trás" ${posicao === 0 ? "disabled" : ""}>${icone("esquerda")}</button>
        <span class="pagina-numero" style="align-self:center">pág. ${p + 1}</span>
        <button class="mini-botao" type="button" data-mover="1" title="Mais para frente" ${posicao === total - 1 ? "disabled" : ""}>${icone("direita")}</button></div>`;
    }
    cartao.innerHTML = `${f.paginas === "marcar" ? `<span class="marca-check">${icone("check")}</span>` : ""}
      <div class="pagina-imagem"><img loading="lazy" alt="Página ${p + 1}" src="/api/miniatura/${a.id}/${p}?largura=200"
        style="transform: rotate(${giro}deg)${escala}"></div>${rodape}`;
    cartao.addEventListener("click", (e) => {
      if (estado.ocupado) return;
      const botao = e.target.closest("button");
      if (f.paginas === "marcar") {
        estado.marcadas.has(p) ? estado.marcadas.delete(p) : estado.marcadas.add(p);
        sincronizarCampoPaginas();
      } else if (botao?.dataset.giro) {
        estado.giros[p] = ((estado.giros[p] || 0) + Number(botao.dataset.giro)) % 360;
      } else if (botao?.dataset.mover) {
        mover(estado.ordem, posicao, posicao + Number(botao.dataset.mover));
      } else return;
      estado.terminou = false;
      $("#resultado").hidden = true;
      desenharPaginas();
      atualizarBotao();
    });
    if (f.paginas === "ordenar") {
      cartao.draggable = true;
      arrastarParaOrdenar(cartao, posicao, estado.ordem, () => { desenharPaginas(); atualizarBotao(); });
    }
    grade.appendChild(cartao);
  });
}

function sincronizarCampoPaginas() {
  const campo = $('#opcoes input[name="paginas"]');
  if (campo) campo.value = textoDasMarcadas();
}

// ------------------------------------------------------------------ botão, andamento e resultado

function rotuloDoBotao(f) {
  if (f.id === "extrair_imagens") return f.titulo;
  if (f.grupo === "para_pdf" || f.grupo === "do_pdf") return "Converter";
  return f.titulo;
}

function atualizarBotao() {
  const f = estado.ferramenta, botao = $("#fazer"), dica = $("#dica");
  const validos = estado.arquivos.filter((a) => !problemaDe(a));
  botao.textContent = rotuloDoBotao(f);
  let motivo = "";
  if (!estado.arquivos.length) motivo = f.varios ? "Escolha os arquivos para começar." : "Escolha o arquivo para começar.";
  else if (validos.length < estado.arquivos.length) motivo = "Tire da lista o arquivo com problema.";
  else if (validos.length < (f.minimo || 1)) motivo = `Escolha pelo menos ${f.minimo} arquivos.`;
  else if (f.precisa && ambiente.programas[f.precisa] === null) motivo = "Falta o Office ou o LibreOffice neste computador.";
  else if (f.paginas === "marcar" && !$('#opcoes input[name="paginas"]').value.trim()) motivo = "Marque as páginas.";
  else if (f.paginas === "girar" && !Object.values(estado.giros).some((g) => g % 360)) motivo = "Gire pelo menos uma página.";
  else if (f.paginas === "ordenar" && !estado.ordem.some((p, i) => p !== i)) motivo = "Mude a ordem de alguma página.";
  else if (f.precisa) motivo = `Vai usar o ${ambiente.programas[f.precisa]} deste computador.`;
  const bloqueia = motivo && !motivo.startsWith("Vai usar");
  botao.disabled = estado.ocupado || !!bloqueia;
  dica.textContent = estado.ocupado ? "" : motivo || `O resultado vai para a pasta ${nomeDaPasta(ambiente.pasta)}. O original não muda.`;
}

function ocupar(sim) {
  estado.ocupado = sim;
  document.body.classList.toggle("ocupado", sim);
  atualizarBotao();
}

function progresso(fracao, texto) {
  $("#andamento").hidden = false;
  const p = Math.round(Math.max(0, Math.min(1, fracao)) * 100);
  $("#barra").style.width = p + "%";
  $("#andamento-porcento").textContent = p + "%";
  if (texto) $("#andamento-texto").textContent = texto;
}

function mostrarErro(mensagem) {
  const r = $("#resultado");
  r.className = "resultado falhou";
  r.innerHTML = `<h3>${icone("erro")} Não deu certo</h3><p>${escapar(mensagem)}</p>`;
  r.hidden = false;
  r.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

async function fazer() {
  const f = estado.ferramenta;
  if (estado.ocupado) return;
  $("#resultado").hidden = true;
  ocupar(true);
  progresso(0, "Começando");
  try {
    const { tarefa } = await api("/api/executar", {
      ferramenta: f.id, arquivos: estado.arquivos.map((a) => a.id), opcoes: lerOpcoes(),
    });
    let situacao;
    do {
      await new Promise((ok) => setTimeout(ok, 300));
      const resposta = await fetch(`/api/tarefa/${tarefa}`);
      situacao = await resposta.json();
      progresso(situacao.progresso / 100, situacao.texto);
    } while (situacao.estado === "rodando");
    ocupar(false);
    $("#andamento").hidden = true;
    if (situacao.estado === "erro") mostrarErro(situacao.erro);
    else mostrarResultado(situacao.resultado);
  } catch (erro) {
    ocupar(false);
    $("#andamento").hidden = true;
    mostrarErro(erro.message);
  }
}

function mostrarResultado(resultado) {
  estado.terminou = true;
  const r = $("#resultado"), arquivos = resultado.arquivos;
  r.className = "resultado ok";
  const pastas = [...new Set(arquivos.map((c) => c.replace(/[\\/][^\\/]+$/, "")))];
  const umaSubpasta = arquivos.length > 1 && pastas.length === 1 && pastas[0] !== ambiente.pasta;
  let html = `<h3>${icone("ok")} ${arquivos.length ? "Pronto!" : "Feito"}</h3><p>${escapar(resultado.mensagem)}</p>`;
  if (arquivos.length) {
    if (umaSubpasta) html += `<p class="dica" style="text-align:left">Na pasta <strong>${escapar(nomeDaPasta(pastas[0]))}</strong>, dentro de ${escapar(nomeDaPasta(ambiente.pasta))}.</p>`;
    html += `<div class="saidas">` + arquivos.slice(0, 50).map((c) => `<div class="saida"><span title="${escapar(c)}">${escapar(nomeDaPasta(c))}</span>
      <button class="mini-botao" type="button" data-abrir="${escapar(c)}" title="Abrir">${icone("abrir")}</button>
      <button class="mini-botao" type="button" data-mostrar="${escapar(c)}" title="Mostrar na pasta">${icone("pasta")}</button></div>`).join("") +
      (arquivos.length > 50 ? `<p class="dica">… e mais ${arquivos.length - 50}.</p>` : "") + `</div>`;
    html += `<div class="resultado-acoes">` + (umaSubpasta
      ? `<button class="botao principal" type="button" data-abrir="${escapar(pastas[0])}">${icone("pasta")} Abrir a pasta</button>`
      : arquivos.length === 1
        ? `<button class="botao principal" type="button" data-abrir="${escapar(arquivos[0])}">${icone("abrir")} Abrir</button>
           <button class="botao" type="button" data-mostrar="${escapar(arquivos[0])}">${icone("pasta")} Mostrar na pasta</button>`
        : `<button class="botao principal" type="button" data-mostrar="${escapar(arquivos[0])}">${icone("pasta")} Mostrar na pasta</button>`) + `</div>`;
  }
  html += `<div class="resultado-acoes"><button class="botao fantasma" type="button" data-de-novo>Fazer com outro arquivo</button></div>`;
  r.innerHTML = html;
  r.hidden = false;
}

$("#resultado").addEventListener("click", async (e) => {
  const alvo = e.target.closest("button");
  if (!alvo) return;
  if (alvo.hasAttribute("data-de-novo")) { abrirFerramenta(estado.ferramenta); return; }
  const caminho = alvo.dataset.abrir || alvo.dataset.mostrar;
  if (!caminho) return;
  try { await api("/api/abrir", { caminho, mostrar: !!alvo.dataset.mostrar }); }
  catch (erro) { alert(erro.message); }
});

// ------------------------------------------------------------------ pasta de saída e tema

async function carregarAmbiente() {
  try {
    ambiente = await (await fetch("/api/ambiente")).json();
  } catch (e) { /* segue com o padrão */ }
  $("#nome-pasta").textContent = nomeDaPasta(ambiente.pasta || "Downloads");
  $("#botao-pasta").title = `Os arquivos prontos são salvos em ${ambiente.pasta}`;
  marcarProgramasQueFaltam();
  if (estado.ferramenta) { avisoDoPrograma(); atualizarBotao(); }
}

function temJanela() { return !!(window.pywebview && window.pywebview.api && window.pywebview.api.escolher_pasta); }

$("#botao-pasta").addEventListener("click", () => {
  $("#caminho-pasta").textContent = ambiente.pasta;
  $("#pasta-navegador").hidden = temJanela();
  $("#pasta-padrao").hidden = ambiente.pasta === ambiente.padrao;
  $("#dialogo-pasta").showModal();
});
async function trocarPasta(pasta) {
  try {
    await api("/api/pasta", { pasta });
    await carregarAmbiente();
    $("#caminho-pasta").textContent = ambiente.pasta;
    $("#pasta-padrao").hidden = ambiente.pasta === ambiente.padrao;
  } catch (erro) { alert(erro.message); }
}
$("#pasta-trocar").addEventListener("click", async () => {
  if (temJanela()) {
    const escolhida = await window.pywebview.api.escolher_pasta();
    if (escolhida) trocarPasta(escolhida);
  } else {
    const digitada = $("#pasta-digitada").value.trim();
    if (digitada) trocarPasta(digitada);
    else $("#pasta-digitada").focus();
  }
});
$("#pasta-padrao").addEventListener("click", () => trocarPasta(null));
$("#pasta-abrir").addEventListener("click", () => api("/api/abrir", { caminho: ambiente.pasta }).catch((e) => alert(e.message)));

$("#botao-tema").addEventListener("click", () => {
  const escuroAgora = document.documentElement.dataset.theme
    ? document.documentElement.dataset.theme === "dark"
    : matchMedia("(prefers-color-scheme: dark)").matches;
  const novo = escuroAgora ? "light" : "dark";
  document.documentElement.dataset.theme = novo;
  try { localStorage.setItem("grampo-tema", novo); } catch (e) { /* sem memória: vale só agora */ }
});

// ------------------------------------------------------------------ eventos gerais

$("#busca").addEventListener("input", filtrar);
$("#busca").addEventListener("keydown", (e) => {
  if (e.key === "Enter") { const primeiro = $(".cartao:not([hidden])"); if (primeiro) primeiro.click(); }
});
$("#voltar").addEventListener("click", () => { if (!estado.ocupado) location.hash = ""; });
$(".marca").addEventListener("click", (e) => { e.preventDefault(); if (!estado.ocupado) location.hash = ""; });
$("#escolher").addEventListener("change", (e) => { enviar(e.target.files); e.target.value = ""; });
$("#fazer").addEventListener("click", fazer);
$("#opcoes").addEventListener("input", (e) => {
  if (e.target.name === "paginas" && estado.arquivos[0]?.paginas) {
    estado.marcadas = lerMarcadasDoTexto(e.target.value, estado.arquivos[0].paginas);
    desenharPaginas();
  }
  estado.terminou = false;
  atualizarOpcoes();
  atualizarBotao();
});
$("#opcoes").addEventListener("submit", (e) => { e.preventDefault(); if (!$("#fazer").disabled) fazer(); });

// Soltar arquivos em qualquer lugar da tela da ferramenta (e nunca deixar a janela "abrir" o arquivo solto)
let contadorArraste = 0;
const temArquivos = (e) => [...(e.dataTransfer?.types || [])].includes("Files");
window.addEventListener("dragenter", (e) => {
  if (!temArquivos(e)) return;
  e.preventDefault();
  if (estado.ferramenta && ++contadorArraste === 1) document.body.classList.add("arrastando");
});
window.addEventListener("dragleave", (e) => {
  if (!temArquivos(e)) return;
  if (--contadorArraste <= 0) { contadorArraste = 0; document.body.classList.remove("arrastando"); }
});
window.addEventListener("dragover", (e) => { if (temArquivos(e)) e.preventDefault(); });
window.addEventListener("drop", (e) => {
  if (!temArquivos(e)) return;
  e.preventDefault();
  contadorArraste = 0;
  document.body.classList.remove("arrastando");
  if (estado.ferramenta) enviar(e.dataTransfer.files);
});

window.addEventListener("hashchange", rota);
montarInicio();
rota();
carregarAmbiente();
