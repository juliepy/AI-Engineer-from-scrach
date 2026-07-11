/**
 * benchmark-runner.ts
 *
 * Lê uma definição de tarefa de benchmark (array JSON de tarefas com critérios de aprovação),
 * "executa" cada tarefa, registra o tempo e a aprovação/falha, e gera um relatório
 * comparativo mostrando quais tarefas passaram e quais falharam.
 *
 * Executar: npx tsx benchmark-runner-pt-br.ts
 */

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

interface BenchmarkTask {
  id: string;
  name: string;
  category: string;
  passCriteria: string[];
  expectedDurationMs: number;
  // Resultados reais simulados
  actualDurationMs: number;
  actualPass: boolean;
  failureReason?: string;
}

interface BenchmarkResult {
  id: string;
  name: string;
  category: string;
  criteriaTotal: number;
  criteriaPassed: number;
  pass: boolean;
  expectedMs: number;
  actualMs: number;
  durationDelta: number;
  failureReason?: string;
}

// ---------------------------------------------------------------------------
// Definições de tarefas de benchmark
// ---------------------------------------------------------------------------

const benchmarkTasks: BenchmarkTask[] = [
  {
    id: "bench-001",
    name: "Importar documento markdown",
    category: "Pipeline de Documentos",
    passCriteria: ["Arquivo aceito", "Chunks criados", "Metadados armazenados"],
    expectedDurationMs: 100,
    actualDurationMs: 95,
    actualPass: true,
  },
  {
    id: "bench-002",
    name: "Importar documento PDF",
    category: "Pipeline de Documentos",
    passCriteria: ["Arquivo aceito", "Texto extraído", "Chunks criados", "Metadados armazenados"],
    expectedDurationMs: 200,
    actualDurationMs: 310,
    actualPass: false,
    failureReason: "A extração de texto do PDF falhou na página 3 -- problema de codificação",
  },
  {
    id: "bench-003",
    name: "Fazer pergunta embasada",
    category: "Pipeline de Q&A",
    passCriteria: ["Consulta recebida", "Chunks relevantes recuperados", "Resposta gerada", "Citações presentes"],
    expectedDurationMs: 500,
    actualDurationMs: 480,
    actualPass: true,
  },
  {
    id: "bench-004",
    name: "Fazer pergunta sem documentos relevantes",
    category: "Pipeline de Q&A",
    passCriteria: ["Consulta recebida", "Mensagem graciosa de 'sem resultados'", "Sem citações alucinadas"],
    expectedDurationMs: 400,
    actualDurationMs: 420,
    actualPass: false,
    failureReason: "O modelo alucinou uma citação em vez de dizer 'sem resultados'",
  },
  {
    id: "bench-005",
    name: "Excluir documento importado",
    category: "Pipeline de Documentos",
    passCriteria: ["Documento removido da lista", "Chunks removidos do índice", "Sem dados órfãos"],
    expectedDurationMs: 150,
    actualDurationMs: 145,
    actualPass: true,
  },
  {
    id: "bench-006",
    name: "Acesso simultâneo de usuários",
    category: "Segurança",
    passCriteria: ["Usuários isolados", "Sem vazamento de dados entre usuários", "Desempenho dentro do SLA"],
    expectedDurationMs: 300,
    actualDurationMs: 850,
    actualPass: false,
    failureReason: "Vazamento de dados entre usuários detectado + tempo de resposta excedeu o SLA (850ms > 500ms)",
  },
  {
    id: "bench-007",
    name: "Continuidade da sessão após reinício",
    category: "Confiabilidade",
    passCriteria: ["Estado persistido", "Sessão recuperada", "Sem perda de dados"],
    expectedDurationMs: 200,
    actualDurationMs: 180,
    actualPass: true,
  },
  {
    id: "bench-008",
    name: "Limitação de taxa da API (Rate limiting)",
    category: "Segurança",
    passCriteria: ["Limite de taxa aplicado", "Resposta 429 após o limite", "Tráfego legítimo não afetado"],
    expectedDurationMs: 100,
    actualDurationMs: 100,
    actualPass: true,
  },
];

// ---------------------------------------------------------------------------
// Simulação de execução
// ---------------------------------------------------------------------------

function executeBenchmark(tasks: BenchmarkTask[]): BenchmarkResult[] {
  return tasks.map((task) => ({
    id: task.id,
    name: task.name,
    category: task.category,
    criteriaTotal: task.passCriteria.length,
    criteriaPassed: task.actualPass ? task.passCriteria.length : Math.floor(task.passCriteria.length * 0.5),
    pass: task.actualPass,
    expectedMs: task.expectedDurationMs,
    actualMs: task.actualDurationMs,
    durationDelta: task.actualDurationMs - task.expectedDurationMs,
    failureReason: task.failureReason,
  }));
}

// ---------------------------------------------------------------------------
// Relatórios
// ---------------------------------------------------------------------------

function pad(s: string, len: number): string {
  return s.length >= len ? s : s + " ".repeat(len - s.length);
}

function run(): void {
  console.log("\n" + "=".repeat(100));
  console.log("  EXECUTOR DE BENCHMARK -- Relatório de Execução de Tarefas");
  console.log("=".repeat(100));

  const results = executeBenchmark(benchmarkTasks);

  // Resultados detalhados
  const header = `| ${pad("ID", 10)}| ${pad("Tarefa", 35)}| ${pad("Categoria", 18)}| ${pad("Passou?", 8)}| ${pad("Critérios", 10)}| ${pad("Esperado", 10)}| ${pad("Real", 10)}| ${pad("Delta", 8)}|`;
  const sep = `|${"-".repeat(12)}|${"-".repeat(37)}|${"-".repeat(20)}|${"-".repeat(10)}|${"-".repeat(12)}|${"-".repeat(12)}|${"-".repeat(12)}|${"-".repeat(10)}|`;
  console.log("\n" + header);
  console.log(sep);

  for (const r of results) {
    const passLabel = r.pass ? "PASSOU" : "FALHOU";
    const criteriaLabel = `${r.criteriaPassed}/${r.criteriaTotal}`;
    const deltaLabel = r.durationDelta >= 0 ? `+${r.durationDelta}ms` : `${r.durationDelta}ms`;
    const marker = r.pass ? "  " : ">>";

    console.log(
      `${marker}| ${pad(r.id, 10)}| ${pad(r.name, 35)}| ${pad(r.category, 18)}| ${pad(passLabel, 8)}| ${pad(criteriaLabel, 10)}| ${pad(r.expectedMs + "ms", 10)}| ${pad(r.actualMs + "ms", 10)}| ${pad(deltaLabel, 8)}|`
    );
  }

  // Detalhes das falhas
  const failures = results.filter((r) => !r.pass);
  if (failures.length > 0) {
    console.log("\n" + "-".repeat(100));
    console.log("  DETALHES DAS FALHAS");
    console.log("-".repeat(100));
    for (const f of failures) {
      console.log(`\n  [${f.id}] ${f.name}`);
      console.log(`    Categoria:    ${f.category}`);
      console.log(`    Critérios:    ${f.criteriaPassed}/${f.criteriaTotal} aprovados`);
      console.log(`    Motivo:       ${f.failureReason ?? "Desconhecido"}`);
      console.log(`    Tempo:        Esperado ${f.expectedMs}ms, real ${f.actualMs}ms (delta: ${f.durationDelta >= 0 ? "+" : ""}${f.durationDelta}ms)`);
    }
  }

  // Resumo
  console.log("\n" + "=".repeat(100));
  console.log("  RESUMO POR CATEGORIA");
  console.log("=".repeat(100) + "\n");

  const categories = [...new Set(results.map((r) => r.category))];
  const catHeader = `| ${pad("Categoria", 20)}| ${pad("Total", 8)}| ${pad("Passaram", 10)}| ${pad("Falharam", 10)}| ${pad("Taxa", 12)}|`;
  const catSep = `|${"-".repeat(22)}|${"-".repeat(10)}|${"-".repeat(12)}|${"-".repeat(12)}|${"-".repeat(14)}|`;
  console.log(catHeader);
  console.log(catSep);

  for (const cat of categories) {
    const catResults = results.filter((r) => r.category === cat);
    const catPassed = catResults.filter((r) => r.pass).length;
    const catFailed = catResults.filter((r) => !r.pass).length;
    const rate = Math.round((catPassed / catResults.length) * 100);

    console.log(`| ${pad(cat, 20)}| ${pad(String(catResults.length), 8)}| ${pad(String(catPassed), 10)}| ${pad(String(catFailed), 10)}| ${pad(rate + "%", 12)}|`);
  }

  // Geral
  const totalPassed = results.filter((r) => r.pass).length;
  const totalFailed = results.filter((r) => !r.pass).length;
  console.log("\n" + "-".repeat(100));
  console.log(`  GERAL: ${totalPassed}/${results.length} passaram (${Math.round((totalPassed / results.length) * 100)}%), ${totalFailed} falhas`);
  console.log("=".repeat(100) + "\n");
}

run();
