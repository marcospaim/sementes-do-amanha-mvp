/* Move o foco para o alerta de erro, para que leitores de tela o anunciem. */
document.addEventListener("DOMContentLoaded", function () {
  var erro = document.getElementById("erro-formulario");
  if (erro) {
    erro.setAttribute("tabindex", "-1");
    erro.focus();
  }
});
