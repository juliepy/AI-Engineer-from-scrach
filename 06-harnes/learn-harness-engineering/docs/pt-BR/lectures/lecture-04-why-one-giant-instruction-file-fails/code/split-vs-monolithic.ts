/**
 * split-vs-monolithic.ts
 *
 * Cria um arquivo de instruções monolítico (~200 linhas) e depois mostra como
 * dividir em 4 arquivos focados reduz drasticamente o contexto necessário
 * para qualquer consulta. Simula um “agente” procurando uma regra específica
 * e mede quantas linhas ele precisa ler em cada abordagem.
 *
 * Run: npx tsx docs/lectures/lecture-04-why-one-giant-instruction-file-fails/code/split-vs-monolithic.ts
 */

// ---------------------------------------------------------------------------
// Arquivo de instruções monolítico simulado (200 linhas de regras)
// ---------------------------------------------------------------------------

const monolithicInstructions: { lineNumber: number; section: string; content: string }[] = [];

// Seção 1: Visão Geral do Projeto (linhas 1-50)
for (let i = 1; i <= 50; i++) {
  monolithicInstructions.push({
    lineNumber: i,
    section: "Visão Geral do Projeto",
    content: i === 25 ? "Este projeto utiliza React 18 com TypeScript em modo strict." : `Detalhe da visão geral linha ${i}`,
  });
}

// Seção 2: Regras de Estilo de Código (linhas 51-100)
for (let i = 51; i <= 100; i++) {
  monolithicInstructions.push({
    lineNumber: i,
    section: "Estilo de Código",
    content:
      i === 72
        ? "REGRA: Sempre use tipos de retorno explícitos em funções exportadas."
        : i === 78
          ? "REGRA: Use const assertions para arrays imutáveis."
          : `Detalhe da regra de estilo linha ${i}`,
  });
}

// Seção 3: Padrões de Teste (linhas 101-150)
for (let i = 101; i <= 150; i++) {
  monolithicInstructions.push({
    lineNumber: i,
    section: "Testes",
    content:
      i === 120
        ? "REGRA: Todo novo endpoint deve possuir testes de integração."
        : i === 135
          ? "REGRA: Arquivos de teste devem espelhar a estrutura dos arquivos fonte."
          : `Detalhe de testes linha ${i}`,
  });
}

// Seção 4: Regras de Deploy (linhas 151-200)
for (let i = 151; i <= 200; i++) {
  monolithicInstructions.push({
    lineNumber: i,
    section: "Deploy",
    content:
      i === 175
        ? "REGRA: Nunca fazer deploy às sextas-feiras. A janela de deploy é de terça a quinta, das 10h às 15h."
        : `Detalhe de deploy linha ${i}`,
  });
}

// ---------------------------------------------------------------------------
// Arquivos de instrução divididos (4 arquivos focados)
// ---------------------------------------------------------------------------

const splitInstructions: Record<string, { lineNumber: number; section: string; content: string }[]> = {
  "01-project-overview.md": monolithicInstructions.filter((l) => l.section === "Visão Geral do Projeto"),
  "02-code-style.md": monolithicInstructions.filter((l) => l.section === "Estilo de Código"),
  "03-testing.md": monolithicInstructions.filter((l) => l.section === "Testes"),
  "04-deployment.md": monolithicInstructions.filter((l) => l.section === "Deploy"),
};

// ---------------------------------------------------------------------------
// Consultas simuladas -- o agente precisa encontrar regras específicas
// ---------------------------------------------------------------------------

interface Query {
  description: string;
  targetRule: string;
  relevantSection: string;
}

const queries: Query[] = [
  {
    description: "Encontrar a regra sobre tipos de retorno",
    targetRule: "tipos de retorno explícitos",
    relevantSection: "Estilo de Código",
  },
  {
    description: "Encontrar a regra da janela de deploy",
    targetRule: "deploy às sextas-feiras",
    relevantSection: "Deploy",
  },
  {
    description: "Encontrar a regra de testes de integração",
    targetRule: "testes de integração",
    relevantSection: "Testes",
  },
  {
    description: "Encontrar a regra da estrutura de arquivos de teste",
    targetRule: "espelhar a estrutura dos arquivos fonte",
    relevantSection: "Testes",
  },
];

// ---------------------------------------------------------------------------
// Simulação de busca
// ---------------------------------------------------------------------------

function searchMonolithic(query: Query): { linesRead: number; found: boolean } {
  // O agente precisa escanear desde o topo, lendo cada linha até encontrar a regra.
  // No pior caso, ele lê todas as linhas.
  let linesRead = 0;
  let found = false;

  for (const line of monolithicInstructions) {
    linesRead++;
    if (line.content.toLowerCase().includes(query.targetRule.toLowerCase())) {
      found = true;
      break;
    }
  }

  return { linesRead, found };
}

function searchSplit(query: Query): { linesRead: number; found: boolean; fileAccessed: string } {
  // O agente sabe em qual arquivo procurar baseado na seção.
  // Ele lê apenas as linhas daquele arquivo.
  const fileMap: Record<string, string> = {
    "Visão Geral do Projeto": "01-project-overview.md",
    "Estilo de Código": "02-code-style.md",
    Testes: "03-testing.md",
    Deploy: "04-deployment.md",
  };

  const targetFile = fileMap[query.relevantSection];
  const lines = splitInstructions[targetFile];
  let linesRead = 0;
  let found = false;

  for (const line of lines) {
    linesRead++;
    if (line.content.toLowerCase().includes(query.targetRule.toLowerCase())) {
      found = true;
      break;
    }
  }

  return { linesRead, found, fileAccessed: targetFile };
}

// ---------------------------------------------------------------------------
// Relatório
// ---------------------------------------------------------------------------

function pad(s: string, len: number): string {
  return s.length >= len ? s : s + " ".repeat(len - s.length);
}

function run(): void {
  console.log("\n" + "=".repeat(90));
  console.log("  ARQUIVOS DE INSTRUÇÃO MONOLÍTICOS vs DIVIDIDOS");
  console.log("=".repeat(90));

  console.log("\n  Arquivo monolítico: 1 arquivo, " + monolithicInstructions.length + " linhas no total");
  console.log("  Arquivos divididos: 4 arquivos, ~" + Math.round(monolithicInstructions.length / 4) + " linhas cada\n");

  const header = `| ${pad("Consulta", 42)}| ${pad("Monolítico (linhas)", 22)}| ${pad("Dividido (linhas)", 20)}| ${pad("Arquivo Acessado", 22)}| Economia`;
  const sep = `|${"-".repeat(44)}|${"-".repeat(24)}|${"-".repeat(22)}|${"-".repeat(24)}|${"-".repeat(10)}`;
  console.log(header);
  console.log(sep);

  let totalMono = 0;
  let totalSplit = 0;

  for (const q of queries) {
    const mono = searchMonolithic(q);
    const split = searchSplit(q);
    totalMono += mono.linesRead;
    totalSplit += split.linesRead;

    const savings = Math.round(((mono.linesRead - split.linesRead) / mono.linesRead) * 100);
    console.log(
      `| ${pad(q.description, 42)}| ${pad(String(mono.linesRead), 22)}| ${pad(String(split.linesRead), 20)}| ${pad(split.fileAccessed, 22)}| ${savings}%`
    );
  }

  console.log(sep);
  const avgMono = Math.round(totalMono / queries.length);
  const avgSplit = Math.round(totalSplit / queries.length);
  console.log(
    `| ${pad("MÉDIA", 42)}| ${pad(String(avgMono), 22)}| ${pad(String(avgSplit), 20)}| ${pad("(arquivo direcionado)", 22)}| ${Math.round(((avgMono - avgSplit) / avgMono) * 100)}%`
  );

  console.log("\n" + "=".repeat(90));
  console.log("  PRINCIPAL INSIGHT");
  console.log("=".repeat(90));
  console.log("  Com um arquivo monolítico, o agente precisa escanear até " + monolithicInstructions.length + " linhas para cada consulta.");
  console.log("  Com arquivos divididos, ele lê apenas o arquivo relevante de aproximadamente " + Math.round(monolithicInstructions.length / 4) + " linhas.");
  console.log("  Isso significa menor uso da janela de contexto, menos alucinações e execução mais rápida.\n");
}

run();