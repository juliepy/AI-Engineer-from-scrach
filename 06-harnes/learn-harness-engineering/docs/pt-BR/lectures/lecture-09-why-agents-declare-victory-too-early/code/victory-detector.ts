/**
 * victory-detector.ts
 *
 * Simula um agente que afirma ter concluído uma tarefa e, em seguida,
 * compara o estado declarado com a verificação real. Exibe: declarado vs real,
 * destacando diferenças entre o que o agente disse e o que realmente é verdade.
 *
 * Executar:
 *   npx tsx docs/lectures/lecture-09-why-agents-declare-victory-too-early/code/victory-detector.ts
 */

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

interface Task {
  name: string;
  claimedComplete: boolean;
  checks: VerificationCheck[];
}

interface VerificationCheck {
  description: string;
  claimed: boolean; // O que o agente afirma
  actual: boolean; // O que realmente é verdade
  severity: "critical" | "warning";
}

// ---------------------------------------------------------------------------
// Tarefas simuladas com estados declarados vs reais
// ---------------------------------------------------------------------------

const tasks: Task[] = [
  {
    name: "Add search endpoint",
    claimedComplete: true,
    checks: [
      {
        description: "Route handler exists",
        claimed: true,
        actual: true,
        severity: "critical",
      },
      {
        description: "Authentication middleware applied",
        claimed: true,
        actual: false, // O agente esqueceu a autenticação
        severity: "critical",
      },
      {
        description: "Input validation added",
        claimed: true,
        actual: true,
        severity: "critical",
      },
      {
        description: "Unit tests written",
        claimed: true,
        actual: false, // O agente pulou os testes
        severity: "critical",
      },
      {
        description: "Integration tests pass",
        claimed: true,
        actual: false, // Não há testes para executar
        severity: "critical",
      },
      {
        description: "Documentation updated",
        claimed: true,
        actual: false, // O agente pulou a documentação
        severity: "warning",
      },
    ],
  },
  {
    name: "Fix pagination bug",
    claimedComplete: true,
    checks: [
      {
        description: "Bug reproduction case confirmed",
        claimed: true,
        actual: true,
        severity: "critical",
      },
      {
        description: "Root cause identified",
        claimed: true,
        actual: true,
        severity: "critical",
      },
      {
        description: "Fix applied",
        claimed: true,
        actual: true,
        severity: "critical",
      },
      {
        description: "Edge cases tested",
        claimed: true,
        actual: false, // Apenas o caminho feliz foi testado
        severity: "warning",
      },
      {
        description: "Regression tests added",
        claimed: true,
        actual: false,
        severity: "critical",
      },
    ],
  },
  {
    name: "Refactor auth module",
    claimedComplete: true,
    checks: [
      {
        description: "Old code removed",
        claimed: true,
        actual: false, // Código antigo ainda existe
        severity: "warning",
      },
      {
        description: "All existing tests still pass",
        claimed: true,
        actual: false, // Dois testes quebraram
        severity: "critical",
      },
      {
        description: "New auth flow works",
        claimed: true,
        actual: true,
        severity: "critical",
      },
      {
        description: "Migration guide written",
        claimed: true,
        actual: false,
        severity: "warning",
      },
    ],
  },
];

// ---------------------------------------------------------------------------
// Verificação
// ---------------------------------------------------------------------------

interface TaskVerification {
  taskName: string;
  claimedComplete: boolean;
  actuallyComplete: boolean;
  totalChecks: number;
  claimedPassing: number;
  actualPassing: number;
  gaps: { description: string; severity: string }[];
}

function verifyTask(task: Task): TaskVerification {
  const claimedPassing = task.checks.filter((c) => c.claimed).length;
  const actualPassing = task.checks.filter((c) => c.actual).length;
  const gaps = task.checks.filter((c) => c.claimed && !c.actual);

  return {
    taskName: task.name,
    claimedComplete: task.claimedComplete,
    actuallyComplete: gaps.length === 0,
    totalChecks: task.checks.length,
    claimedPassing,
    actualPassing,
    gaps: gaps.map((g) => ({
      description: g.description,
      severity: g.severity,
    })),
  };
}

// ---------------------------------------------------------------------------
// Relatórios
// ---------------------------------------------------------------------------

function pad(s: string, len: number): string {
  return s.length >= len ? s : s + " ".repeat(len - s.length);
}

function run(): void {
  console.log("\n" + "=".repeat(90));
  console.log("  DETECTOR DE VITÓRIA -- Verificação Declarada vs Real");
  console.log("=".repeat(90));

  const verifications = tasks.map(verifyTask);

  for (const v of verifications) {
    console.log("\n  Tarefa: " + v.taskName);
    console.log("  " + "-".repeat(70));

    console.log(
      `  Agente declarou: ${
        v.claimedComplete ? "CONCLUÍDA" : "NÃO CONCLUÍDA"
      }`
    );

    console.log(
      `  Estado real:      ${
        v.actuallyComplete ? "CONCLUÍDA" : "INCOMPLETA"
      }`
    );

    if (!v.actuallyComplete) {
      console.log(
        `  DIVERGÊNCIA: O agente declarou vitória, mas ${v.gaps.length} verificação(ões) falharam!`
      );
    }

    // Detalhes das verificações da tarefa
    const task = tasks.find((t) => t.name === v.taskName)!;

    console.log("\n  Detalhes das verificações:");

    const header = `  | ${pad("Verificação", 40)}| ${pad(
      "Declarado",
      9
    )}| ${pad("Real", 9)}| ${pad("Gap?", 6)}|`;

    const sep = `  |${"-".repeat(42)}|${"-".repeat(11)}|${"-".repeat(
      11
    )}|${"-".repeat(8)}|`;

    console.log(header);
    console.log(sep);

    for (const check of task.checks) {
      const claimedLabel = check.claimed ? "PASS" : "FAIL";
      const actualLabel = check.actual ? "PASS" : "FAIL";
      const gapLabel = check.claimed && !check.actual ? "GAP" : "";
      const marker = gapLabel ? ">>" : "  ";

      console.log(
        `${marker}| ${pad(check.description, 40)}| ${pad(
          claimedLabel,
          9
        )}| ${pad(actualLabel, 9)}| ${pad(gapLabel, 6)}|`
      );
    }
  }

  // Resumo geral
  console.log("\n" + "=".repeat(90));
  console.log("  RESUMO GERAL");
  console.log("=".repeat(90) + "\n");

  const sHeader = `| ${pad("Tarefa", 28)}| ${pad(
    "Declarado",
    10
  )}| ${pad("Real", 10)}| ${pad("Gaps", 6)}| ${pad(
    "Precisão",
    10
  )}|`;

  const sSep = `|${"-".repeat(30)}|${"-".repeat(12)}|${"-".repeat(
    12
  )}|${"-".repeat(8)}|${"-".repeat(12)}|`;

  console.log(sHeader);
  console.log(sSep);

  for (const v of verifications) {
    const accuracy = Math.round(
      (v.actualPassing / v.totalChecks) * 100
    );

    const cLabel = v.claimedComplete ? "Concluída" : "Pendente";
    const aLabel = v.actuallyComplete ? "Concluída" : "Incompleta";

    console.log(
      `| ${pad(v.taskName, 28)}| ${pad(cLabel, 10)}| ${pad(
        aLabel,
        10
      )}| ${pad(String(v.gaps.length), 6)}| ${pad(
        accuracy + "%",
        10
      )}|`
    );
  }

  const totalGaps = verifications.reduce(
    (s, v) => s + v.gaps.length,
    0
  );

  const falseVictories = verifications.filter(
    (v) => v.claimedComplete && !v.actuallyComplete
  ).length;

  console.log(
    "\n  Falsas vitórias: " +
      falseVictories +
      " de " +
      verifications.length +
      " tarefas"
  );

  console.log("  Total de gaps não detectados: " + totalGaps);

  console.log(
    "\n  O agente declarou 'concluído' para todas as tarefas, mas a verificação revelou " +
      totalGaps +
      " critérios não atendidos."
  );

  console.log(
    "  Sem verificação explícita, declarações prematuras de vitória passam despercebidas.\n"
  );
}

run();