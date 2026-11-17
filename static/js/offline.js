/* Fila local de entregas (IndexedDB) e sincronização com a API. */
(function () {
  "use strict";

  const DB_NAME = "sementes";
  const STORE = "fila";
  const SYNC_URL = "/api/entregas/sincronizar/";

  function abrir() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, 1);
      req.onupgradeneeded = () => {
        if (!req.result.objectStoreNames.contains(STORE)) {
          req.result.createObjectStore(STORE, { keyPath: "origem_uuid" });
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async function comStore(modo, acao) {
    const db = await abrir();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, modo);
      const store = tx.objectStore(STORE);
      const req = acao(store);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
      tx.oncomplete = () => db.close();
    });
  }

  const fila = {
    adicionar: (item) => comStore("readwrite", (s) => s.put(item)),
    todos: () => comStore("readonly", (s) => s.getAll()),
    remover: (uuid) => comStore("readwrite", (s) => s.delete(uuid)),
    atualizar: (item) => comStore("readwrite", (s) => s.put(item)),
  };

  function csrfToken() {
    const par = document.cookie.split("; ").find((c) => c.startsWith("csrftoken="));
    return par ? decodeURIComponent(par.split("=")[1]) : "";
  }

  async function sincronizar() {
    const pendentes = await fila.todos();
    let enviados = 0;
    for (const item of pendentes) {
      if (item.status === "rejeitado") continue;
      try {
        const resposta = await fetch(SYNC_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken(),
          },
          body: JSON.stringify({
            origem_uuid: item.origem_uuid,
            familia_codigo: item.familia_codigo,
            item: item.item,
            quantidade: item.quantidade,
            ciclo: item.ciclo,
          }),
        });
        if (resposta.ok) {
          await fila.remover(item.origem_uuid);
          enviados += 1;
        } else if (resposta.status === 409) {
          const corpo = await resposta.json().catch(() => ({}));
          await fila.atualizar({ ...item, status: "rejeitado", motivo: corpo.detail || "Conflito" });
        } else if (resposta.status === 400) {
          const corpo = await resposta.json().catch(() => ({}));
          await fila.atualizar({
            ...item,
            status: "rejeitado",
            motivo: corpo.detail || "Dados inválidos",
          });
        } else if (resposta.status === 401 || resposta.status === 403) {
          return enviados;
        }
      } catch (erro) {
        return enviados;
      }
    }
    return enviados;
  }

  window.FilaEntregas = { fila, sincronizar };

  function configurarFormulario() {
    const form = document.getElementById("form-entrega");
    if (!form) return;

    const aviso = document.getElementById("estado-conexao");
    const atualizarAviso = () => {
      if (aviso) aviso.hidden = navigator.onLine;
    };
    atualizarAviso();
    window.addEventListener("online", atualizarAviso);
    window.addEventListener("offline", atualizarAviso);

    const mapaEl = document.getElementById("familias-codigos");
    const mapa = mapaEl ? JSON.parse(mapaEl.textContent) : {};

    form.addEventListener("submit", async (evento) => {
      if (navigator.onLine) return;

      evento.preventDefault();
      const dados = new FormData(form);
      const familiaId = String(dados.get("familia") || "");
      const codigo = mapa[familiaId];
      if (!codigo) {
        window.alert("Selecione uma família válida antes de salvar.");
        return;
      }

      const registro = {
        origem_uuid: crypto.randomUUID(),
        familia_codigo: codigo,
        item: Number(dados.get("item")),
        quantidade: Number(dados.get("quantidade")),
        ciclo: String(dados.get("ciclo") || ""),
        criado_em: new Date().toISOString(),
        status: "pendente",
      };

      await fila.adicionar(registro);

      const container = document.createElement("div");
      container.className = "alerta-sucesso";
      container.setAttribute("role", "status");

      const icone = document.createElement("span");
      icone.setAttribute("aria-hidden", "true");
      icone.textContent = "✓";

      const texto = document.createElement("div");
      const forte = document.createElement("strong");
      forte.textContent = "Entrega salva no aparelho. ";
      texto.appendChild(forte);
      texto.appendChild(document.createTextNode("Aguardando sincronização. "));
      const link = document.createElement("a");
      link.href = "/entregas/pendentes/";
      link.textContent = "Ver pendentes";
      texto.appendChild(link);

      container.appendChild(icone);
      container.appendChild(texto);
      form.parentNode.insertBefore(container, form);
      form.reset();
      atualizarAviso();
    });
  }

  window.addEventListener("online", () => {
    sincronizar().then((enviados) => {
      if (enviados > 0 && document.body.dataset.recarregarAposSync === "true") {
        window.location.reload();
      }
    });
  });

  document.addEventListener("DOMContentLoaded", configurarFormulario);
})();
