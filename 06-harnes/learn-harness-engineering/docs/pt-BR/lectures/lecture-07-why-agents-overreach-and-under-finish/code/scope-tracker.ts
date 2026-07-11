/**
 * scope-tracker.ts
 *
 * Lê uma lista de funcionalidades e um log de alterações. Impõe a política
 * de apenas uma funcionalidade ativa por vez. Dado um histórico de alterações,
 * sinaliza qualquer mudança fora do escopo da funcionalidade ativa.
 * Demonstra como ocorre o desvio de escopo (*scope drift*) e como o rastreador
 * consegue detectá-lo.
 *
 * Executar: npx tsx docs/lectures/lecture-07-why-agents-overreach-and-under-finish/code/scope-tracker.ts
 */

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

interface Feature {
  id: string;
  name: string;
  status: "active" | "pending" | "done";
}

interface ChangeLogEntry {
  step: number;
  file: string;
  description: string;
  featureId: string; // Funcionalidade à qual esta alteração afirma pertencer
}

// ---------------------------------------------------------------------------
// Dados de exemplo
// ---------------------------------------------------------------------------

const features: Feature[] = [
  { id: "F-001", name: "Endpoint de busca", status: "active" },
  { id: "F-002", name: "Endpoint de exclusão", status: "pending" },
  { id: "F-003", name: "Limitação de taxa", status: "pending" },
  { id: "F-004", name: "Painel do usuário", status: "pending" },
];

// Um log de alterações realista em que o agente gradualmente se afasta da funcionalidade ativa
const changeLog: ChangeLogEntry[] = [
  { step: 1, file: "src/routes/search.ts", description: "Adicionar manipulador da rota de busca", featureId: "F-001" },
  { step: 2, file: "src/routes/search.ts", description: "Adicionar validação dos parâmetros de consulta", featureId: "F-001" },
  { step: 3, file: "src/routes/search.ts", description: "Adicionar paginação dos resultados de busca", featureId: "F-001" },
  { step: 4, file: "src/routes/delete.ts", description: "Adicionar manipulador da rota de exclusão", featureId: "F-002" }, // DESVIO
  { step: 5, file: "src/middleware/rate-limit.ts", description: "Adicionar middleware de limitação de taxa", featureId: "F-003" }, // DESVIO
  { step: 6, file: "src/routes/search.ts", description: "Integrar limitador de taxa à busca", featureId: "F-001" },
  { step: 7, file: "src/dashboard/ui.tsx", description: "Criar componente de layout do painel", featureId: "F-004" }, // DESVIO
  { step: 8, file: "src/routes/search.ts", description: "Adicionar formatação da resposta da busca", featureId: "F-001" },
  { step: 9, file: "src/routes/delete.ts", description: "Adicionar lógica de confirmação de exclusão", featureId: "F-002" }, // DESVIO
  { step: 10, file: "src/routes/search.ts", description: "Adicionar testes da busca", featureId: "F-001" },
];

// ---------------------------------------------------------------------------
// Rastreador de escopo
// ---------------------------------------------------------------------------

interface ScopeCheckResult {
  step: number;
  file: string;
  description: string;
  featureId: string;
  inScope: boolean;
  activeFeature: string;
}

function trackScope(
  featureList: Feature[],
  changes: ChangeLogEntry[]
): ScopeCheckResult[] {
  const activeFeatures = featureList.filter((f) => f.status === "active");
  const activeIds = new Set(activeFeatures.map((f) => f.id));
  const activeNames = activeFeatures.map((f) => f.name).join(", ");

  return changes.map((change) => ({
    step: change.step,
    file: change.file,
    description: change.description,
    featureId: change.featureId,
    inScope: activeIds.has(change.featureId),
    activeFeature: activeNames,
  }));
}

// ---------------------------------------------------------------------------
// Relatórios
// ---------------------------------------------------------------------------

function pad(s: string, len: number): string {
  return s.length >= len ? s : s + " ".repeat(len - s.length);
}

function run(): void {
  const results = trackScope(features, changeLog);

  console.log("\n" + "=".repeat(100));
  console.log("  RASTREADOR DE ESCOPO -- Aplicação de Funcionalidade Única Ativa");
  console.log("=".repeat(100));

  console.log("\n  Funcionalidade ativa: " + features.filter((f) => f.status === "active").map((f) => `${f.id} (${f.name})`).join(", "));
  console.log("  Funcionalidades pendentes: " + features.filter((f) => f.status === "pending").map((f) => `${f.id} (${f.name})`).join(", "));

  // Log detalhado de alterações
  console.log("\n" + "-".repeat(100));
  const header = `| ${pad("Etapa", 5)}| ${pad("Arquivo", 35)}| ${pad("Descrição", 40)}| ${pad("Funcionalidade", 8)}| ${pad("No Escopo", 10)}|`;
  const sep = `|${"-".repeat(7)}|${"-".repeat(37)}|${"-".repeat(42)}|${"-".repeat(10)}|${"-".repeat(12)}|`;
  console.log(header);
  console.log(sep);

  let inScopeCount = 0;
  let driftCount = 0;

  for (const r of results) {
    const scopeLabel = r.inScope ? "OK" : "DESVIO";
    if (r.inScope) inScopeCount++;
    else driftCount++;

    const marker = r.inScope ? "  " : ">>";
    console.log(`${marker}| ${pad(String(r.step), 5)}| ${pad(r.file, 35)}| ${pad(r.description, 40)}| ${pad(r.featureId, 8)}| ${pad(scopeLabel, 10)}|`);
  }

  // Resumo
  console.log("\n" + "=".repeat(100));
  console.log("  RESUMO DOS DESVIOS DE ESCOPO");
  console.log("=".repeat(100) + "\n");

  const sHeader = `| ${pad("Métrica", 40)}| ${pad("Valor", 15)}|`;
  const sSep = `|${"-".repeat(42)}|${"-".repeat(17)}|`;
  console.log(sHeader);
  console.log(sSep);
  console.log(`| ${pad("Total de alterações", 40)}| ${pad(String(results.length), 15)}|`);
  console.log(`| ${pad("Alterações dentro do escopo ativo (F-001)", 40)}| ${pad(String(inScopeCount), 15)}|`);
  console.log(`| ${pad("Alterações fora do escopo ativo (DESVIO)", 40)}| ${pad(String(driftCount), 15)}|`);
  console.log(`| ${pad("Funcionalidades afetadas (total)", 40)}| ${pad(String(new Set(results.map((r) => r.featureId)).size), 15)}|`);

  // Detalhes dos desvios
  const driftFeatures = [...new Set(results.filter((r) => !r.inScope).map((r) => r.featureId))];
  if (driftFeatures.length > 0) {
    console.log("\n  FUNCIONALIDADES COM DESVIO:");
    for (const fid of driftFeatures) {
      const feat = features.find((f) => f.id === fid);
      const driftChanges = results.filter((r) => r.featureId === fid);
      console.log(`    ${fid} (${feat?.name}): ${driftChanges.length} alterações não autorizadas`);
    }
  }

  console.log("\n  Sem um rastreador de escopo, o agente trabalhou silenciosamente em " + driftFeatures.length + " funcionalidades não relacionadas.");
  console.log("  O rastreador detecta esse desvio e aplica a política de apenas uma funcionalidade ativa.\n");
}

run();
