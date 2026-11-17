/* Exibe a fila local de entregas pendentes no aparelho. */
(function () {
  "use strict";

  const lista = document.getElementById("lista-pendentes");
  const resumo = document.getElementById("resumo-pendentes");
  const botao = document.getElementById("sincronizar-agora");

  function criarCelula(texto) {
    const td = document.createElement("td");
    td.textContent = texto;
    return td;
  }

  function criarRotulo(status) {
    const span = document.createElement("span");
    span.className = "pill pill-ambar";
    span.textContent = status === "rejeitado" ? "! Rejeitado" : "◷ Pendente";
    return span;
  }

  function linhaVazia(texto) {
    const tr = document.createElement("tr");
    const td = criarCelula(texto);
    td.colSpan = 4;
    tr.appendChild(td);
    return tr;
  }

  function preencherTabela(itens) {
    lista.textContent = "";
    if (itens.length === 0) {
      lista.appendChild(linhaVazia("Nenhum registro pendente no aparelho."));
      return;
    }
    itens.forEach(function (item) {
      const tr = document.createElement("tr");
      tr.appendChild(criarCelula(item.familia_codigo));
      tr.appendChild(criarCelula(String(item.quantidade)));
      tr.appendChild(criarCelula(item.ciclo));
      const tdEstado = document.createElement("td");
      tdEstado.appendChild(criarRotulo(item.status));
      if (item.motivo) {
        tdEstado.appendChild(document.createTextNode(" — " + item.motivo));
      }
      tr.appendChild(tdEstado);
      lista.appendChild(tr);
    });
  }

  async function renderizar() {
    if (!window.FilaEntregas || !lista) return;
    const itens = await window.FilaEntregas.fila.todos();
    preencherTabela(itens);
    if (resumo) {
      resumo.textContent =
        itens.length === 0
          ? "Nenhum registro pendente."
          : `${itens.length} registro(s) no aparelho.`;
    }
  }

  if (botao) {
    botao.addEventListener("click", async () => {
      botao.disabled = true;
      botao.textContent = "Sincronizando...";
      const enviados = await window.FilaEntregas.sincronizar();
      botao.disabled = false;
      botao.textContent = "Sincronizar agora";
      const aviso = document.getElementById("resultado-sync");
      if (aviso) {
        aviso.textContent =
          enviados > 0
            ? `${enviados} registro(s) sincronizado(s).`
            : "Nenhum registro pôde ser sincronizado agora.";
      }
      renderizar();
    });
  }

  document.addEventListener("DOMContentLoaded", renderizar);
})();
