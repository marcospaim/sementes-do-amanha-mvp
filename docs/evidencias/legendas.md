# Evidências de operação e acessibilidade

Capturas reais do sistema em execução (ambiente local, dados fictícios do
`seed_demo`), geradas a partir da aplicação Django, sem mockups.

## Captura 1 — Menu inicial (operação geral)

Tela inicial após autenticação do perfil **Voluntário** (Cláudia Santos). Exibe
o menu com a ação prioritária "Registrar entrega" em destaque e os atalhos para
cadastro/consulta de famílias e pendentes de sincronização. O rodapé informa que
painel e relatório são restritos à coordenação. Evidencia a hierarquia visual,
os alvos de toque e a navegação por perfil.

## Captura 2 — Confirmação do registro de entrega

Continuação do fluxo central: após registrar a entrega da **FAM-0043 (Ana
Souza)**, o sistema confirma a operação e mostra família, item, quantidade,
ciclo **2026-11** e autoria. A mensagem "Entrega registrada e sincronizada"
indica que a baixa foi aplicada ao estoque. Evidencia a integridade do registro
e a rastreabilidade (quem registrou e em qual ciclo).

## Captura 3 — Acessibilidade em funcionamento

Tela de registro de entrega com **ampliação de 175%** e **foco de teclado no
alerta de erro**. A tentativa de registrar novamente a **FAM-0042 (Maria
Silva)** no ciclo 2026-11 foi bloqueada; o alerta usa `role="alert"`, ícone,
texto e cor (não depende apenas de cor), recebe foco automaticamente e apresenta
contorno azul visível. Os rótulos permanecem associados aos campos e o conteúdo
não se perde com a ampliação.

## Conexão com o ODS 2

O ODS 2 (meta 2.1) busca garantir acesso de todas as pessoas a alimentação
segura e nutritiva. No contexto do parceiro, o acesso depende de a distribuição
de cestas ser registrada com confiabilidade. A barreira concreta é operar o
sistema em pé, com uma mão, sob luz solar, em aparelho intermediário e com baixa
familiaridade digital; a isso somam-se hipóteses de baixa visão.

O recurso de acessibilidade reduz essa barreira: a ampliação permite ler valores
e mensagens; o foco no alerta garante que o erro seja percebido e anunciado;
ícone + texto + cor evitam interpretação errada por quem não distingue cores; e
os rótulos persistentes orientam o preenchimento. Com isso, o voluntário conclui
o registro sem ajuda, o que evita duplicidade e famílias desatendidas e torna a
distribuição mais equitativa.

**Limite:** o software não amplia a oferta de alimentos nem controla doações,
renda ou políticas públicas; sua contribuição é restrita à confiabilidade da
operação local.
