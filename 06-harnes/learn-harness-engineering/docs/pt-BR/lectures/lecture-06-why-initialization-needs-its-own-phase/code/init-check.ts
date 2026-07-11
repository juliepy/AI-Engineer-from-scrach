/**
 * init-check.ts
 *
 * Verifica programaticamente os pré-requisitos de inicialização:
 *   - Versão do Node.js
 *   - Dependências instaladas (existência de node_modules)
 *   - Existência do diretório de dados
 *   - Presença dos arquivos de configuração
 *
 * Simula a execução com e sem uma fase explícita de inicialização,
 * demonstrando como pré-requisitos ausentes causam falhas silenciosas posteriormente.
 *
 * Executar: npx tsx docs/lectures/lecture-06-why-initialization-needs-its-own-phase/code/init-check.ts
 */

import * as fs from "node:fs";
import * as path from "node:path";
import * as childProcess from "node:child_process";

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

interface CheckItem {
  name: string;
  category: string;
  check: () => { pass: boolean; detail: string };
  impactIfMissing: string;
}

interface CheckResult {
  name: string;
  category: string;
  passed: boolean;
  detail: string;
  impactIfMissing: string;
}

// ---------------------------------------------------------------------------
// Verificações
// ---------------------------------------------------------------------------

function createChecks(targetDir: string): CheckItem[] {
  return [
    {
      name: "Versão do Node.js >= 18",
      category: "Runtime",
      check: () => {
        try {
          const version = process.version; // ex.: "v20.11.0"
          const major = parseInt(version.replace("v", "").split(".")[0], 10);
          return {
            pass: major >= 18,
            detail: `Detectado: ${version} (necessário >= v18)`,
          };
        } catch {
          return { pass: false, detail: "Não foi possível detectar a versão do Node.js" };
        }
      },
      impactIfMissing: "Recursos do TypeScript e APIs nativas indisponíveis",
    },
    {
      name: "package.json existe",
      category: "Configuração",
      check: () => {
        const p = path.join(targetDir, "package.json");
        const exists = fs.existsSync(p);
        return {
          pass: exists,
          detail: exists ? `Encontrado: ${p}` : "Não encontrado no diretório alvo",
        };
      },
      impactIfMissing: "Não é possível instalar dependências ou executar scripts",
    },
    {
      name: "Dependências instaladas (node_modules)",
      category: "Dependências",
      check: () => {
        const p = path.join(targetDir, "node_modules");
        const exists = fs.existsSync(p);
        return {
          pass: exists,
          detail: exists ? `Encontrado: ${p}` : "node_modules/ não encontrado — execute npm install",
        };
      },
      impactIfMissing: "Todos os imports falham em tempo de execução",
    },
    {
      name: "TypeScript disponível",
      category: "Ferramentas",
      check: () => {
        try {
          const result = childProcess.execSync("npx tsc --version", {
            encoding: "utf-8",
            timeout: 10000,
            stdio: ["pipe", "pipe", "pipe"],
          }).trim();
          return { pass: true, detail: `Detectado: ${result}` };
        } catch {
          return { pass: false, detail: "TypeScript não disponível via npx" };
        }
      },
      impactIfMissing: "Não é possível compilar arquivos TypeScript",
    },
    {
      name: "tsconfig.json existe",
      category: "Configuração",
      check: () => {
        const p = path.join(targetDir, "tsconfig.json");
        const exists = fs.existsSync(p);
        return {
          pass: exists,
          detail: exists ? `Encontrado: ${p}` : "Não encontrado",
        };
      },
      impactIfMissing: "O compilador TypeScript usará configurações padrão, que podem não atender às necessidades do projeto",
    },
    {
      name: "Diretório de código-fonte existe",
      category: "Estrutura",
      check: () => {
        const candidates = ["src", "lib", "app"];
        const found = candidates.filter((d) => {
          const p = path.join(targetDir, d);
          return fs.existsSync(p) && fs.statSync(p).isDirectory();
        });
        return {
          pass: found.length > 0,
          detail: found.length > 0 ? `Encontrado: ${found.join(", ")}` : "Nenhum diretório src/, lib/ ou app/ encontrado",
        };
      },
      impactIfMissing: "O agente não consegue localizar os arquivos-fonte para modificar",
    },
    {
      name: "Diretório de testes existe",
      category: "Estrutura",
      check: () => {
        const candidates = ["test", "tests", "__tests__", "spec"];
        const found = candidates.filter((d) => {
          const p = path.join(targetDir, d);
          return fs.existsSync(p) && fs.statSync(p).isDirectory();
        });
        return {
          pass: found.length > 0,
          detail: found.length > 0 ? `Encontrado: ${found.join(", ")}` : "Nenhum diretório de testes encontrado",
        };
      },
      impactIfMissing: "O agente não consegue localizar ou executar os testes existentes",
    },
    {
      name: "Repositório Git inicializado",
      category: "Controle de Versão",
      check: () => {
        const gitDir = path.join(targetDir, ".git");
        const exists = fs.existsSync(gitDir);
        return {
          pass: exists,
          detail: exists ? "Repositório Git detectado" : "Nenhum diretório .git encontrado",
        };
      },
      impactIfMissing: "Sem capacidade de rollback e sem histórico de alterações",
    },
  ];
}

// ---------------------------------------------------------------------------
// Simulação: com e sem fase de inicialização
// ---------------------------------------------------------------------------

interface SimResult {
  scenario: string;
  checksRun: boolean;
  failuresBeforeWork: number;
  workAttempted: boolean;
  workSucceeded: boolean;
  timeWastedMs: number;
}

function simulateWithoutInit(): SimResult {
  // O agente ignora a inicialização e começa a trabalhar imediatamente.
  // Encontra falhas uma a uma à medida que esbarra em pré-requisitos ausentes.
  const checks = createChecks(process.cwd());
  let failures = 0;
  let timeWasted = 0;

  for (const check of checks) {
    const result = check.check();
    if (!result.pass) {
      failures++;
      timeWasted += 200; // O agente gasta tempo descobrindo cada problema
    }
  }

  return {
    scenario: "SEM FASE DE INICIALIZAÇÃO",
    checksRun: false,
    failuresBeforeWork: 0, // Não verificou previamente
    workAttempted: true,
    workSucceeded: failures === 0,
    timeWastedMs: timeWasted,
  };
}

function simulateWithInit(): SimResult {
  // O agente executa a fase de inicialização primeiro e descobre todos os problemas antecipadamente.
  const checks = createChecks(process.cwd());
  let failures = 0;

  for (const check of checks) {
    if (!check.check().pass) {
      failures++;
    }
  }

  return {
    scenario: "COM FASE DE INICIALIZAÇÃO",
    checksRun: true,
    failuresBeforeWork: failures,
    workAttempted: failures === 0,
    workSucceeded: failures === 0,
    timeWastedMs: 0,
  };
}

// ---------------------------------------------------------------------------
// Relatórios
// ---------------------------------------------------------------------------

function pad(s: string, len: number): string {
  return s.length >= len ? s : s + " ".repeat(len - s.length);
}

function run(): void {
  const targetDir = process.cwd();
  console.log("\n" + "=".repeat(80));
  console.log("  VERIFICAÇÃO DOS PRÉ-REQUISITOS DE INICIALIZAÇÃO");
  console.log("=".repeat(80));
  console.log(`  Alvo: ${targetDir}\n`);

  const checks = createChecks(targetDir);
  const results: CheckResult[] = checks.map((c) => {
    const r = c.check();
    return {
      name: c.name,
      category: c.category,
      passed: r.pass,
      detail: r.detail,
      impactIfMissing: c.impactIfMissing,
    };
  });

  // Relatório detalhado
  const header = `| ${pad("Verificação", 35)}| ${pad("Categoria", 12)}| ${pad("Status", 6)}| Detalhe`;
  const sep = `|${"-".repeat(37)}|${"-".repeat(14)}|${"-".repeat(8)}|${"-".repeat(40)}`;
  console.log(header);
  console.log(sep);

  for (const r of results) {
    const status = r.passed ? "PASSOU" : "FALHOU";
    console.log(`| ${pad(r.name, 35)}| ${pad(r.category, 12)}| ${pad(status, 6)}| ${r.detail}`);
  }

  const passCount = results.filter((r) => r.passed).length;
  const failCount = results.filter((r) => !r.passed).length;

  console.log("\n" + "-".repeat(80));
  console.log(`  Resultados: ${passCount} aprovadas, ${failCount} falharam de um total de ${results.length} verificações`);

  if (failCount > 0) {
    console.log("\n  VERIFICAÇÕES FALHARAM — Impacto se não forem corrigidas:");
    for (const r of results.filter((r) => !r.passed)) {
      console.log(`    - ${r.name}: ${r.impactIfMissing}`);
    }
  }

  // Comparação: com e sem inicialização
  const noInit = simulateWithoutInit();
  const withInit = simulateWithInit();

  console.log("\n" + "=".repeat(80));
  console.log("  COMPARAÇÃO DA FASE DE INICIALIZAÇÃO");
  console.log("=".repeat(80) + "\n");

  const cHeader = `| ${pad("Métrica", 35)}| ${pad("Sem Inicialização", 18)}| ${pad("Com Inicialização", 18)}|`;
  const cSep = `|${"-".repeat(37)}|${"-".repeat(20)}|${"-".repeat(20)}|`;
  console.log(cHeader);
  console.log(cSep);
  console.log(`| ${pad("Pré-requisitos verificados antecipadamente", 35)}| ${pad("Não", 18)}| ${pad("Sim", 18)}|`);
  console.log(`| ${pad("Trabalho iniciado apesar dos problemas", 35)}| ${pad(String(noInit.workAttempted), 18)}| ${pad(String(withInit.workAttempted), 18)}|`);
  console.log(`| ${pad("Tempo perdido descobrindo problemas tardiamente", 35)}| ${pad(noInit.timeWastedMs + "ms", 18)}| ${pad(withInit.timeWastedMs + "ms", 18)}|`);
  console.log(`| ${pad("Trabalho concluído com sucesso", 35)}| ${pad(String(noInit.workSucceeded), 18)}| ${pad(String(withInit.workSucceeded), 18)}|`);

  console.log("\n  Uma fase explícita de inicialização identifica problemas antes que eles desperdicem tempo.\n");
}

run();
