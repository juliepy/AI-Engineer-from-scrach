/**
 * failure-pattern-demo.ts
 *
 * Simula o padrão de falha em 4 etapas no qual agentes capazes frequentemente caem:
 *   1. Contexto incompleto
 *   2. Mudanças localmente razoáveis
 *   3. Ausência de verificação global
 *   4. Conclusão prematura
 *
 * Execute:
 * npx tsx docs/lectures/lecture-01-why-capable-agents-still-fail/code/failure-pattern-demo.ts
 */

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

interface StepState {
  step: number;
  name: string;
  contextAvailable: string[];
  contextMissing: string[];
  actionTaken: string;
  localOutcome: string;
  globalImpact: string;
  completed: boolean;
}

// ---------------------------------------------------------------------------
// "Modelo" simulado — uma função simples de decisão que baseia sua saída
// apenas no contexto que recebeu.
// ---------------------------------------------------------------------------

function modelDecide(context: string[], task: string): string {
  const has = (s: string) => context.some((c) => c.includes(s));

  // A tarefa é "adicionar um endpoint de busca na API".
  // A resposta correta exige conhecimento sobre middleware de autenticação
  // e limitação de taxa (rate limiting).

  if (!has("auth")) {
    return "Criou a nova rota /search sem verificações de autenticação";
  }

  if (!has("rate-limit")) {
    return "Adicionou a rota de busca com autenticação, mas esqueceu o rate limiting";
  }

  if (!has("test-standards")) {
    return "Implementou a busca com autenticação e rate limiting, mas sem testes";
  }

  return "Implementou completamente o endpoint de busca com autenticação, rate limiting e testes";
}

// ---------------------------------------------------------------------------
// Simulação de falha
// ---------------------------------------------------------------------------

function simulateFailurePattern(): StepState[] {
  const steps: StepState[] = [];

  // ---- Etapa 1: Contexto incompleto ----
  const step1Context = ["estrutura do projeto", "definições de rotas"];
  const step1Missing = [
    "middleware de autenticação",
    "política de rate limiting",
    "padrões de testes",
  ];

  const step1Decision = modelDecide(
    step1Context,
    "adicionar endpoint de busca"
  );

  steps.push({
    step: 1,
    name: "Contexto Incompleto",
    contextAvailable: step1Context,
    contextMissing: step1Missing,
    actionTaken: step1Decision,
    localOutcome: "Parece correto -- a rota compila e retorna dados",
    globalImpact:
      "A ausência de autenticação permite acesso não autenticado à busca",
    completed: false,
  });

  // ---- Etapa 2: Mudanças localmente razoáveis ----
  // O agente adiciona autenticação após uma dica,
  // mas ainda sem outros contextos importantes.
  const step2Context = [...step1Context, "middleware de autenticação"];
  const step2Missing = ["política de rate limiting", "padrões de testes"];

  const step2Decision = modelDecide(
    step2Context,
    "adicionar endpoint de busca"
  );

  steps.push({
    step: 2,
    name: "Mudanças Localmente Razoáveis",
    contextAvailable: step2Context,
    contextMissing: step2Missing,
    actionTaken: step2Decision,
    localOutcome: "A rota possui autenticação -- parece completa localmente",
    globalImpact:
      "Sem rate limiting, o endpoint pode ser abusado",
    completed: false,
  });

  // ---- Etapa 3: Ausência de verificação global ----
  const step3Context = [...step2Context, "política de rate limiting"];
  const step3Missing = ["padrões de testes"];

  const step3Decision = modelDecide(
    step3Context,
    "adicionar endpoint de busca"
  );

  steps.push({
    step: 3,
    name: "Ausência de Verificação Global",
    contextAvailable: step3Context,
    contextMissing: step3Missing,
    actionTaken: step3Decision,
    localOutcome: "A funcionalidade parece totalmente implementada",
    globalImpact:
      "Sem testes -- risco de regressão e violação dos padrões do projeto",
    completed: false,
  });

  // ---- Etapa 4: Conclusão prematura ----
  steps.push({
    step: 4,
    name: "Conclusão Prematura",
    contextAvailable: step3Context,
    contextMissing: step3Missing,
    actionTaken: 'Agente responde: "Concluído. Endpoint de busca adicionado."',
    localOutcome: "O agente está satisfeito e marca a tarefa como concluída",
    globalImpact:
      "A tarefa está incompleta -- faltam testes e verificação E2E",
    completed: true,
  });

  return steps;
}

// ---------------------------------------------------------------------------
// Tabela comparativa
// ---------------------------------------------------------------------------

function printComparisonTable(steps: StepState[]): void {
  console.log("\n" + "=".repeat(90));
  console.log("  DEMONSTRAÇÃO DO PADRÃO DE FALHA -- 4 Etapas até uma entrega quebrada");
  console.log("=".repeat(90));

  for (const s of steps) {
    console.log(`\n  Etapa ${s.step}: ${s.name}`);
    console.log("  " + "-".repeat(60));

    console.log(
      `  Contexto disponível : ${s.contextAvailable.join(", ")}`
    );

    console.log(
      `  Contexto ausente    : ${
        s.contextMissing.join(", ") || "(nenhum)"
      }`
    );

    console.log(`  Ação executada      : ${s.actionTaken}`);
    console.log(`  Resultado local     : ${s.localOutcome}`);
    console.log(`  Impacto global      : ${s.globalImpact}`);

    console.log(
      `  Marcado como concluído? : ${
        s.completed ? "SIM (prematuramente)" : "Não"
      }`
    );
  }

  // Resumo comparativo
  console.log("\n" + "=".repeat(90));
  console.log(
    "  COMPARAÇÃO: O que o agente viu vs. o que realmente era necessário"
  );
  console.log("=".repeat(90));

  const totalRequired = [
    "estrutura do projeto",
    "definições de rotas",
    "middleware de autenticação",
    "política de rate limiting",
    "padrões de testes",
  ];

  const finalAvailable =
    steps[steps.length - 1].contextAvailable;

  const header =
    "| Critério                | Disponível | Ausente | Status   |";

  const sep =
    "|-------------------------|------------|----------|----------|";

  console.log("\n" + header);
  console.log(sep);

  for (const item of totalRequired) {
    const avail = finalAvailable.includes(item);

    const row = `| ${item.padEnd(24)}| ${(
      avail ? "Sim" : "Não"
    ).padEnd(11)}| ${(!avail ? "Sim" : "").padEnd(9)}| ${(
      avail ? "OK" : "LACUNA"
    ).padEnd(9)}|`;

    console.log(row);
  }

  const gapCount = totalRequired.filter(
    (i) => !finalAvailable.includes(i)
  ).length;

  console.log(
    "\n  Resultado: o agente concluiu com " +
      gapCount +
      " de " +
      totalRequired.length +
      " itens de contexto ausentes."
  );

  console.log(
    "  Este é o padrão central de falha: cada etapa parecia razoável isoladamente.\n"
  );
}

// ---------------------------------------------------------------------------
// Execução
// ---------------------------------------------------------------------------

printComparisonTable(simulateFailurePattern());