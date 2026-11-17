/* Exibe a fila local de entregas pendentes no aparelho. */
(function () {
  "use strict";

  const lista = document.getElementById("lista-pendentes");
  const resumo = document.getElementById("resumo-pendentes");
  const botao = document.getElementById("sincronizar-agora");

  function rotulo(status) {
    if (status === "rejeitado") {
      return "<span class='pill pill-ambar'>! Rejeitado</span>";
    }
    return "<span class='pill pill-ambar'>◷ Pendente</span>";
  }

  async function renderizar() {
    if (!window.FilaEntregas) return;
    const itens = await window.FilaEntregas.fila.todos();
    if (!lista) return;

    if (itens.length === 0) {
      lista.innerHTML = "<tr><td colspan='4'>Nenhum registro pendente no aparelho.</td></tr>";
      if (resumo) resumo.textContent = "Nenhum registro pendente.";
      return;
    }

    lista.innerHTML = itens
      .map(
        (i) =>
          "<tr>" +
          `<td>${i.familia_codigo}</td>` +
          `<td>${i.quantidade}</td>` +
          `<td>${i.ciclo}</td>` +
          `<td>${rotulo(i.status)}${i.motivo ? " — " + i.motivo : ""}</td>` +
          "</tr>"
      )
      .join("");
    if (resumo) resumo.textContent = `${itens.length} registro(s) no aparelho.`;
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
