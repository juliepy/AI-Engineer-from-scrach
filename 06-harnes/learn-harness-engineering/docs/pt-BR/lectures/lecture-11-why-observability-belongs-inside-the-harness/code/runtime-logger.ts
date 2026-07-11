/**
 * runtime-logger.ts
 *
 * Demonstração de um módulo de logging estruturado. Mostra a diferença entre
 * saídas ad-hoc com console.log e logs estruturados em JSON ao diagnosticar
 * uma falha. Inclui um cenário de falha pré-configurado e demonstra como
 * logs estruturados identificam o problema com mais rapidez.
 *
 * Executar:
 * npx tsx docs/lectures/lecture-11-why-observability-belongs-inside-the-harness/code/runtime-logger.ts
 */

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

interface StructuredLogEntry {
  timestamp: string;
  level: "info" | "warn" | "error" | "debug";
  component: string;
  action: string;
  durationMs?: number;
  input?: unknown;
  output?: unknown;
  error?: string;
  correlationId: string;
}

// ---------------------------------------------------------------------------
// Pipeline simulado com uma falha pré-configurada
// ---------------------------------------------------------------------------

const CORRELATION_ID = "req-" + Math.random().toString(36).slice(2, 8);

// Etapas simuladas de um pipeline de perguntas e respostas sobre documentos
interface PipelineStage {
  component: string;
  action: string;
  durationMs: number;
  success: boolean;
  errorMessage?: string;
  input?: unknown;
  output?: unknown;
}

function runPipeline(): PipelineStage[] {
  return [
    {
      component: "DocumentLoader",
      action: "parse_upload",
      durationMs: 45,
      success: true,
      input: { filename: "report.pdf", size: "2.3MB" },
      output: { chunks: 47 },
    },
    {
      component: "ChunkIndexer",
      action: "embed_and_store",
      durationMs: 230,
      success: true,
      input: { chunks: 47 },
      output: { indexed: 47, embeddingDim: 1536 },
    },
    {
      component: "QueryRouter",
      action: "route_query",
      durationMs: 12,
      success: true,
      input: { query: "What is the revenue target?" },
      output: { routedTo: "RetrievalEngine" },
    },
    {
      // FALHA PRÉ-CONFIGURADA: A recuperação retorna 0 resultados devido
      // a uma incompatibilidade de dimensões
      component: "RetrievalEngine",
      action: "semantic_search",
      durationMs: 180,
      success: false,
      errorMessage:
        "Incompatibilidade de dimensão vetorial: embedding da consulta=768, embedding do índice=1536",
      input: { query: "What is the revenue target?", topK: 5 },
      output: { results: 0 },
    },
    {
      component: "AnswerGenerator",
      action: "generate_with_citations",
      durationMs: 1500,
      success: true, // Não falha, mas gera uma resposta ruim
      input: { context: [], query: "What is the revenue target?" },
      output: {
        answer: "Não consegui encontrar informações relevantes.",
        citations: 0,
      },
    },
  ];
}

// ---------------------------------------------------------------------------
// Logging ad-hoc (estilo console.log)
// ---------------------------------------------------------------------------

function printAdHocLog(stages: PipelineStage[]): void {
  console.log("Iniciando pipeline de perguntas e respostas sobre documentos...");
  console.log("Usuário enviou report.pdf");

  for (const stage of stages) {
    if (stage.success) {
      console.log(
        `${stage.component}: ${stage.action} concluído (${stage.durationMs}ms)`
      );
    } else {
      console.log(`${stage.component}: algo deu errado`);
    }
  }

  console.log(
    "Pipeline finalizado. Resposta: Não consegui encontrar informações relevantes."
  );
}

// ---------------------------------------------------------------------------
// Logging estruturado (JSON)
// ---------------------------------------------------------------------------

function printStructuredLog(stages: PipelineStage[]): StructuredLogEntry[] {
  const entries: StructuredLogEntry[] = [];

  for (const stage of stages) {
    entries.push({
      timestamp: new Date().toISOString(),
      level: stage.success ? "info" : "error",
      component: stage.component,
      action: stage.action,
      durationMs: stage.durationMs,
      input: stage.input,
      output: stage.output,
      error: stage.errorMessage,
      correlationId: CORRELATION_ID,
    });
  }

  return entries;
}

// ---------------------------------------------------------------------------
// Diagnóstico baseado em logs estruturados
// ---------------------------------------------------------------------------

function diagnoseFromStructured(entries: StructuredLogEntry[]): string[] {
  const diagnosis: string[] = [];

  // Encontrar erros
  const errors = entries.filter((e) => e.level === "error");

  if (errors.length > 0) {
    diagnosis.push("ERROS ENCONTRADOS:");

    for (const err of errors) {
      diagnosis.push(`  - ${err.component}.${err.action}: ${err.error}`);
    }
  }

  // Verificar picos de latência
  const slowStages = entries.filter((e) => (e.durationMs ?? 0) > 1000);

  if (slowStages.length > 0) {
    diagnosis.push("PICOS DE LATÊNCIA:");

    for (const s of slowStages) {
      diagnosis.push(`  - ${s.component}.${s.action}: ${s.durationMs}ms`);
    }
  }

  // Verificar falhas em cascata
  const emptyOutputs = entries.filter((e) => {
    const out = e.output as Record<string, unknown> | undefined;

    return (
      out &&
      typeof out === "object" &&
      "results" in out &&
      (out.results as number) === 0
    );
  });

  if (emptyOutputs.length > 0) {
    diagnosis.push("SAÍDAS VAZIAS (possível efeito cascata):");

    for (const e of emptyOutputs) {
      diagnosis.push(`  - ${e.component}.${e.action}: retornou 0 resultados`);
    }
  }

  return diagnosis;
}

// ---------------------------------------------------------------------------
// Relatórios
// ---------------------------------------------------------------------------

function pad(s: string, len: number): string {
  return s.length >= len ? s : s + " ".repeat(len - s.length);
}

function run(): void {
  const pipeline = runPipeline();

  console.log("\n" + "=".repeat(90));
  console.log("  DEMONSTRAÇÃO DE OBSERVABILIDADE -- Logging Ad-hoc vs Estruturado");
  console.log("=".repeat(90));

  // --- Saída ad-hoc ---
  console.log("\n" + "-".repeat(90));
  console.log("  CENÁRIO A: Saída com console.log ad-hoc");
  console.log("-".repeat(90) + "\n");

  printAdHocLog(pipeline);

  console.log("\n  Diagnóstico a partir dos logs ad-hoc: ??? Difícil saber o que aconteceu.");
  console.log("  A mensagem de falha é vaga: 'algo deu errado'.");
  console.log("  Sem dimensões, sem dados de entrada/saída, sem ID de correlação.");

  // --- Saída estruturada ---
  console.log("\n" + "-".repeat(90));
  console.log("  CENÁRIO B: Saída com logs JSON estruturados");
  console.log("-".repeat(90) + "\n");

  const structuredEntries = printStructuredLog(pipeline);

  const header = `| ${pad("Timestamp", 26)}| ${pad("Nível", 6)}| ${pad(
    "Componente",
    20
  )}| ${pad("Ação", 25)}| ${pad("Duração", 9)}| Erro?`;

  const sep = `|${"-".repeat(28)}|${"-".repeat(8)}|${"-".repeat(
    22
  )}|${"-".repeat(27)}|${"-".repeat(11)}|${"-".repeat(30)}`;

  console.log(header);
  console.log(sep);

  for (const entry of structuredEntries) {
    const hasError = entry.error ? entry.error.slice(0, 30) : "";
    const marker = entry.level === "error" ? ">>" : "  ";

    console.log(
      `${marker}| ${pad(entry.timestamp, 26)}| ${pad(
        entry.level,
        6
      )}| ${pad(entry.component, 20)}| ${pad(
        entry.action,
        25
      )}| ${pad(String(entry.durationMs) + "ms", 9)}| ${hasError}`
    );
  }

  // --- Diagnóstico ---
  console.log("\n" + "-".repeat(90));
  console.log("  DIAGNÓSTICO AUTOMATIZADO A PARTIR DOS LOGS ESTRUTURADOS");
  console.log("-".repeat(90) + "\n");

  const errors = structuredEntries.filter((e) => e.level === "error");

  for (const err of errors) {
    console.log(`  CAUSA RAIZ: ${err.component}.${err.action}`);
    console.log(`  Erro: ${err.error}`);
    console.log(`  Entrada: ${JSON.stringify(err.input)}`);
    console.log(`  Saída: ${JSON.stringify(err.output)}`);
    console.log(`  ID de Correlação: ${err.correlationId}`);
  }

  // Impacto downstream
  console.log("\n  IMPACTO NAS ETAPAS SEGUINTES:");

  const answerGen = structuredEntries.find(
    (e) => e.component === "AnswerGenerator"
  );

  if (answerGen) {
    const out = answerGen.output as Record<string, unknown>;

    console.log(
      `  AnswerGenerator recebeu contexto vazio (${JSON.stringify(
        answerGen.input
      )})`
    );

    console.log(
      `  Produziu a resposta: "${out.answer}" com ${out.citations} citações`
    );
  }

  // Resumo comparativo
  console.log("\n" + "=".repeat(90));
  console.log("  COMPARAÇÃO");
  console.log("=".repeat(90) + "\n");

  const cHeader = `| ${pad("Métrica", 35)}| ${pad(
    "Logs Ad-hoc",
    18
  )}| ${pad("Logs Estruturados", 18)}|`;

  const cSep = `|${"-".repeat(37)}|${"-".repeat(20)}|${"-".repeat(20)}|`;

  console.log(cHeader);
  console.log(cSep);

  console.log(
    `| ${pad("Causa raiz identificável", 35)}| ${pad("Não", 18)}| ${pad(
      "Sim",
      18
    )}|`
  );

  console.log(
    `| ${pad("Entradas/saídas rastreáveis", 35)}| ${pad(
      "Não",
      18
    )}| ${pad("Sim", 18)}|`
  );

  console.log(
    `| ${pad("Correlação entre etapas", 35)}| ${pad(
      "Não",
      18
    )}| ${pad("Sim", 18)}|`
  );

  console.log(
    `| ${pad("Interpretável por máquina", 35)}| ${pad(
      "Não",
      18
    )}| ${pad("Sim", 18)}|`
  );

  console.log(
    `| ${pad("Tempo para diagnóstico", 35)}| ${pad(
      "Minutos (manual)",
      18
    )}| ${pad("Segundos (automático)", 18)}|`
  );

  console.log(
    "\n  O logging estruturado transforma a depuração de um processo baseado em suposições em uma análise determinística.\n"
  );
}

run();