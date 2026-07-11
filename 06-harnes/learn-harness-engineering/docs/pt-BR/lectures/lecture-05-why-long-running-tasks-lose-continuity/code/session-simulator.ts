/**
 * session-simulator.ts
 *
 * Simula duas sessões trabalhando em uma tarefa de múltiplas etapas.
 *   Execução 1: Sem arquivo de handoff — a Sessão B começa do zero e duplica trabalho.
 *   Execução 2: Com arquivo de handoff — a Sessão B continua de onde a Sessão A parou.
 *
 * Executar:
 * npx tsx docs/lectures/lecture-05-why-long-running-tasks-lose-continuity/code/session-simulator.ts
 */

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

interface TaskStep {
  id: number;
  name: string;
  durationMs: number;
}

interface SessionResult {
  session: string;
  stepsCompleted: number;
  totalDurationMs: number;
  duplicatedSteps: number;
  output: string[];
}

// ---------------------------------------------------------------------------
// Definição da tarefa
// ---------------------------------------------------------------------------

const taskSteps: TaskStep[] = [
  { id: 1, name: "Ler a estrutura do projeto", durationMs: 50 },
  { id: 2, name: "Compreender o módulo de autenticação existente", durationMs: 80 },
  { id: 3, name: "Projetar novo endpoint de busca", durationMs: 60 },
  { id: 4, name: "Implementar endpoint de busca", durationMs: 100 },
  { id: 5, name: "Escrever testes de integração", durationMs: 70 },
  { id: 6, name: "Atualizar documentação", durationMs: 40 },
];

// ---------------------------------------------------------------------------
// Executor de sessão simulada
// ---------------------------------------------------------------------------

/** Simula uma sessão executando trabalho. */
function runSession(
  sessionName: string,
  startStep: number,
  endStep: number
): SessionResult {
  const output: string[] = [];
  let totalDuration = 0;

  for (let i = startStep; i <= endStep; i++) {
    const step = taskSteps.find((s) => s.id === i)!;
    totalDuration += step.durationMs;
    output.push(
      `  [${sessionName}] Etapa ${step.id}: ${step.name} (${step.durationMs}ms)`
    );
  }

  return {
    session: sessionName,
    stepsCompleted: endStep - startStep + 1,
    totalDurationMs: totalDuration,
    duplicatedSteps: 0,
    output,
  };
}

// ---------------------------------------------------------------------------
// Execução 1: Sem arquivo de handoff
// ---------------------------------------------------------------------------

function simulateNoHandoff(): {
  sessionA: SessionResult;
  sessionB: SessionResult;
} {
  // A Sessão A executa as etapas 1-3 antes de atingir o limite de contexto
  const sessionA = runSession("Sessão A", 1, 3);

  // A Sessão B não possui contexto e começa do zero
  const sessionB = runSession("Sessão B", 1, 6);
  sessionB.duplicatedSteps = 3; // Refaz as etapas 1-3 já concluídas pela Sessão A

  return { sessionA, sessionB };
}

// ---------------------------------------------------------------------------
// Execução 2: Com arquivo de handoff
// ---------------------------------------------------------------------------

function simulateWithHandoff(): {
  sessionA: SessionResult;
  sessionB: SessionResult;
} {
  // A Sessão A executa as etapas 1-3 e grava um arquivo de handoff
  const sessionA = runSession("Sessão A", 1, 3);

  // A Sessão B lê o handoff e continua a partir da etapa 4
  const sessionB = runSession("Sessão B", 4, 6);
  sessionB.duplicatedSteps = 0;

  return { sessionA, sessionB };
}

// ---------------------------------------------------------------------------
// Relatórios
// ---------------------------------------------------------------------------

function pad(s: string, len: number): string {
  return s.length >= len ? s : s + " ".repeat(len - s.length);
}

function printRun(
  title: string,
  result: { sessionA: SessionResult; sessionB: SessionResult }
): void {
  console.log("\n" + "=".repeat(80));
  console.log(`  ${title}`);
  console.log("=".repeat(80));

  console.log("\n  Saída da Sessão A:");
  for (const line of result.sessionA.output) {
    console.log(line);
  }

  console.log("\n  Saída da Sessão B:");
  for (const line of result.sessionB.output) {
    console.log(line);
  }

  console.log("\n  Observações da Sessão B:");
  if (result.sessionB.duplicatedSteps > 0) {
    console.log(
      `    - Refez ${result.sessionB.duplicatedSteps} etapas já concluídas pela Sessão A`
    );
    console.log(
      `    - Desperdiçou ${
        result.sessionB.totalDurationMs -
        taskSteps.slice(3).reduce((s, t) => s + t.durationMs, 0)
      }ms em trabalho duplicado`
    );
  } else {
    console.log("    - Leu o arquivo de handoff e continuou a partir da etapa 4");
    console.log("    - Nenhum trabalho duplicado foi realizado");
  }
}

function printComparison(): void {
  const noHandoff = simulateNoHandoff();
  const withHandoff = simulateWithHandoff();

  printRun("EXECUÇÃO 1: SEM ARQUIVO DE HANDOFF", noHandoff);
  printRun("EXECUÇÃO 2: COM ARQUIVO DE HANDOFF", withHandoff);

  // Tabela comparativa
  console.log("\n" + "=".repeat(80));
  console.log("  TABELA COMPARATIVA");
  console.log("=".repeat(80) + "\n");

  const header = `| ${pad("Métrica", 35)}| ${pad(
    "Sem Handoff",
    15
  )}| ${pad("Com Handoff", 15)}|`;
  const sep = `|${"-".repeat(37)}|${"-".repeat(17)}|${"-".repeat(17)}|`;

  console.log(header);
  console.log(sep);

  const noTotal =
    noHandoff.sessionA.totalDurationMs +
    noHandoff.sessionB.totalDurationMs;

  const withTotal =
    withHandoff.sessionA.totalDurationMs +
    withHandoff.sessionB.totalDurationMs;

  console.log(
    `| ${pad("Etapas concluídas pela Sessão A", 35)}| ${pad(
      String(noHandoff.sessionA.stepsCompleted),
      15
    )}| ${pad(String(withHandoff.sessionA.stepsCompleted), 15)}|`
  );

  console.log(
    `| ${pad("Etapas concluídas pela Sessão B", 35)}| ${pad(
      String(noHandoff.sessionB.stepsCompleted),
      15
    )}| ${pad(String(withHandoff.sessionB.stepsCompleted), 15)}|`
  );

  console.log(
    `| ${pad("Etapas duplicadas", 35)}| ${pad(
      String(noHandoff.sessionB.duplicatedSteps),
      15
    )}| ${pad(String(withHandoff.sessionB.duplicatedSteps), 15)}|`
  );

  console.log(
    `| ${pad("Trabalho total (ms)", 35)}| ${pad(
      String(noTotal),
      15
    )}| ${pad(String(withTotal), 15)}|`
  );

  console.log(
    `| ${pad("Tempo economizado com handoff", 35)}| ${pad(
      "-",
      15
    )}| ${pad(String(noTotal - withTotal) + "ms", 15)}|`
  );

  console.log(
    "\n  Um arquivo de handoff elimina trabalho duplicado e garante continuidade entre sessões.\n"
  );
}

printComparison();