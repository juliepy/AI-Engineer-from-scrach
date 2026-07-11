/**
 * harness-vs-no-harness.ts
 *
 * Comparação lado a lado do mesmo executor de tarefas rodando com e sem
 * um harness. A versão com harness adiciona regras explícitas, etapas de
 * verificação e condições de parada.
 *
 * Execute: npx tsx docs/lectures/lecture-02-what-a-harness-actually-is/code/harness-vs-no-harness.ts
 */

// ---------------------------------------------------------------------------
// Tipos e helpers
// ---------------------------------------------------------------------------

interface TaskResult {
  name: string;
  passed: boolean;
  durationMs: number;
  issues: string[];
}

function pad(s: string, len: number): string {
  return s.length >= len ? s : s + " ".repeat(len - s.length);
}

// ---------------------------------------------------------------------------
// Executor de tarefas simulado
// ---------------------------------------------------------------------------

/** Uma tarefa simples que pode passar ou falhar dependendo das regras. */
type Task = {
  name: string;
  requiresAuth: boolean;
  hasTests: boolean;
  withinScope: boolean;
};

const tasks: Task[] = [
  { name: "Adicionar endpoint de busca", requiresAuth: true, hasTests: false, withinScope: true },
  { name: "Adicionar endpoint de exclusão", requiresAuth: true, hasTests: true, withinScope: true },
  { name: "Refatorar middleware de autenticação", requiresAuth: true, hasTests: true, withinScope: false },
  { name: "Adicionar health check", requiresAuth: false, hasTests: true, withinScope: true },
  { name: "Adicionar limitador de taxa", requiresAuth: true, hasTests: false, withinScope: true },
];

// ---------------------------------------------------------------------------
// Execução SEM harness -- apenas executa todas as tarefas, sem verificações
// ---------------------------------------------------------------------------

function runWithoutHarness(taskList: Task[]): TaskResult[] {
  const results: TaskResult[] = [];

  for (const t of taskList) {
    const start = performance.now();
    const issues: string[] = [];

    // O "agente" faz o trabalho e considera concluído.
    let passed = true;

    // Problemas que passam despercebidos sem um harness
    if (t.requiresAuth && !t.hasTests) {
      issues.push("Sem testes para endpoint protegido por autenticação");
      // O agente não percebe -- marca como sucesso mesmo assim
    }
    if (!t.withinScope) {
      issues.push("Tarefa fora do escopo atual");
      // O agente não percebe
    }

    const duration = performance.now() - start;
    results.push({ name: t.name, passed, durationMs: duration, issues });
  }

  return results;
}

// ---------------------------------------------------------------------------
// Execução COM harness -- regras, verificação e condições de parada
// ---------------------------------------------------------------------------

function runWithHarness(taskList: Task[]): TaskResult[] {
  const rules = {
    requireTestsForAuth: true,
    enforceScope: true,
  };

  const results: TaskResult[] = [];

  for (const t of taskList) {
    const start = performance.now();
    const issues: string[] = [];
    let passed = true;

    // Regra: endpoints protegidos por autenticação devem ter testes
    if (rules.requireTestsForAuth && t.requiresAuth && !t.hasTests) {
      issues.push("BLOQUEADO: Endpoint protegido por autenticação sem testes");
      passed = false;
    }

    // Regra: permanecer dentro do escopo
    if (rules.enforceScope && !t.withinScope) {
      issues.push("BLOQUEADO: Tarefa fora do escopo ativo -- ignorada");
      passed = false;
    }

    // Verificação: revalidar após a execução
    if (passed && !t.hasTests) {
      issues.push("AVISO: Não existem testes para esta alteração");
    }

    const duration = performance.now() - start;
    results.push({ name: t.name, passed, durationMs: duration, issues });
  }

  return results;
}

// ---------------------------------------------------------------------------
// Relatório
// ---------------------------------------------------------------------------

function printComparison(
  noHarness: TaskResult[],
  withHarness: TaskResult[]
): void {
  console.log("\n" + "=".repeat(80));
  console.log("  COMPARAÇÃO: HARNESS vs SEM HARNESS");
  console.log("=".repeat(80));

  const header = `| ${pad("Tarefa", 28)}| ${pad("Sem Harness", 12)}| ${pad("Problemas(SH)", 35)}| ${pad("Com Harness", 12)}| ${pad("Problemas(CH)", 35)}|`;
  const sep = `|${"-".repeat(30)}|${"-".repeat(14)}|${"-".repeat(37)}|${"-".repeat(14)}|${"-".repeat(37)}|`;

  console.log("\n" + header);
  console.log(sep);

  for (let i = 0; i < noHarness.length; i++) {
    const nh = noHarness[i];
    const wh = withHarness[i];
    const nhPass = nh.passed ? "PASSOU" : "FALHOU";
    const whPass = wh.passed ? "PASSOU" : "FALHOU";
    const nhIssue = nh.issues[0] ?? "(nenhum)";
    const whIssue = wh.issues[0] ?? "(nenhum)";

    console.log(
      `| ${pad(nh.name, 28)}| ${pad(nhPass, 12)}| ${pad(nhIssue, 35)}| ${pad(whPass, 12)}| ${pad(whIssue, 35)}|`
    );
  }

  // Métricas
  const nhPassed = noHarness.filter((r) => r.passed).length;
  const whPassed = withHarness.filter((r) => r.passed).length;
  const nhIssues = noHarness.reduce((sum, r) => sum + r.issues.length, 0);
  const whIssues = withHarness.reduce((sum, r) => sum + r.issues.length, 0);

  console.log("\n" + "=".repeat(80));
  console.log("  MÉTRICAS RESUMIDAS");
  console.log("=".repeat(80));

  const metricsHeader = `| ${pad("Métrica", 30)}| ${pad("Sem Harness", 15)}| ${pad("Com Harness", 15)}|`;
  const metricsSep = `|${"-".repeat(32)}|${"-".repeat(17)}|${"-".repeat(17)}|`;
  console.log("\n" + metricsHeader);
  console.log(metricsSep);
  console.log(`| ${pad("Tarefas aprovadas", 30)}| ${pad(String(nhPassed) + "/" + noHarness.length, 15)}| ${pad(String(whPassed) + "/" + withHarness.length, 15)}|`);
  console.log(`| ${pad("Problemas detectados", 30)}| ${pad(String(nhIssues), 15)}| ${pad(String(whIssues), 15)}|`);
  console.log(`| ${pad("Falsos positivos (passou mas com falhas)", 30)}| ${pad(String(nhPassed - truePassCount(noHarness)), 15)}| ${pad(String(whPassed - truePassCount(withHarness)), 15)}|`);

  console.log("\n  O harness detecta problemas que a execução sem harness ignora silenciosamente.");
  console.log("  Sem um harness, toda tarefa 'passa' mesmo quando não deveria.\n");
}

/** Conta tarefas que realmente passaram (têm testes e estão dentro do escopo). */
function truePassCount(results: TaskResult[]): number {
  return results.filter((r) => r.passed && r.issues.length === 0).length;
}

// ---------------------------------------------------------------------------
// Execução
// ---------------------------------------------------------------------------

printComparison(runWithoutHarness(tasks), runWithHarness(tasks));