/**
 * cleanup-scanner.ts
 *
 * Varre o diretório de um projeto em busca de artefatos obsoletos, código morto,
 * violações estruturais e gera um relatório de limpeza. Ajuda a aplicar o
 * princípio de "estado limpo ao final de cada sessão".
 *
 * Uso:
 *   npx tsx cleanup-scanner-pt-br.ts [caminho]
 *   (o padrão é o diretório de trabalho atual)
 *
 * Executar: npx tsx cleanup-scanner-pt-br.ts
 */

import * as fs from "node:fs";
import * as path from "node:path";

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

interface ScanResult {
  category: string;
  check: string;
  severity: "critical" | "warning" | "info";
  found: string[];
  description: string;
}

// ---------------------------------------------------------------------------
// Verificações do Scanner
// ---------------------------------------------------------------------------

interface ScannerCheck {
  category: string;
  name: string;
  severity: "critical" | "warning" | "info";
  description: string;
  scan: (dir: string) => string[];
}

function createChecks(): ScannerCheck[] {
  return [
    {
      category: "Artefatos Obsoletos",
      name: "Arquivos temporários (*.tmp, *.bak, *.swp)",
      severity: "warning",
      description: "Arquivos temporários remanescentes de edição ou processamento",
      scan: (dir) => findFiles(dir, [".tmp", ".bak", ".swp", "~"]),
    },
    {
      category: "Artefatos Obsoletos",
      name: "Arquivos de debug/log no código-fonte",
      severity: "warning",
      description: "Arquivos de log que não deveriam estar na árvore de fontes",
      scan: (dir) => {
        const found: string[] = [];
        const logPatterns = [".log"];
        for (const p of findFiles(dir, logPatterns)) {
          // Apenas sinaliza arquivos de log em diretórios de código-fonte
          if (p.includes("/src/") || p.includes("/lib/") || p.includes("/app/")) {
            found.push(p);
          }
        }
        return found;
      },
    },
    {
      category: "Código Morto",
      name: "Imports não utilizados (detecção por heurística)",
      severity: "info",
      description: "Arquivos que podem conter código não utilizado (varredura heurística)",
      scan: (dir) => {
        const found: string[] = [];
        const srcDirs = ["src", "lib", "app"];
        for (const srcDir of srcDirs) {
          const srcPath = path.join(dir, srcDir);
          if (fs.existsSync(srcPath)) {
            scanForPatterns(srcPath, ["TODO:", "FIXME:", "HACK:", "XXX:"], found, dir);
          }
        }
        return found;
      },
    },
    {
      category: "Violações Estruturais",
      name: "Falta do .gitignore",
      severity: "warning",
      description: "Arquivo .gitignore não encontrado -- risco de commitar artefatos de build",
      scan: (dir) => fs.existsSync(path.join(dir, ".gitignore")) ? [] : [".gitignore (AUSENTE)"],
    },
    {
      category: "Violações Estruturais",
      name: "Artefatos de build no código-fonte",
      severity: "critical",
      description: "Saída compilada (dist/, build/) misturada com o código-fonte",
      scan: (dir) => {
        const found: string[] = [];
        // Verifica se dist/ ou build/ existe dentro de src/
        const dirs = ["src/dist", "src/build", "lib/dist", "lib/build"];
        for (const d of dirs) {
          if (fs.existsSync(path.join(dir, d))) {
            found.push(d + "/");
          }
        }
        return found;
      },
    },
    {
      category: "Violações Estruturais",
      name: "node_modules na árvore de fontes",
      severity: "critical",
      description: "Diretório node_modules encontrado fora da raiz (dependência aninhada)",
      scan: (dir) => {
        const found: string[] = [];
        const srcDirs = ["src", "lib", "app", "test", "tests"];
        for (const srcDir of srcDirs) {
          const nmPath = path.join(dir, srcDir, "node_modules");
          if (fs.existsSync(nmPath)) {
            found.push(srcDir + "/node_modules/");
          }
        }
        return found;
      },
    },
    {
      category: "Limpeza da Sessão",
      name: "Indicador de alterações não commitadas",
      severity: "info",
      description: "Verifica artefatos comuns de sessões incompletas",
      scan: (dir) => {
        const found: string[] = [];
        const indicators = [
          "WIP.md", "EM_PROGRESSO.md", "scratch.ts", "scratch.js",
          "debug.ts", "teste-manual.ts", "temp.ts",
        ];
        for (const f of indicators) {
          if (fs.existsSync(path.join(dir, f))) {
            found.push(f);
          }
        }
        return found;
      },
    },
    {
      category: "Limpeza da Sessão",
      name: "Diretórios vazios",
      severity: "info",
      description: "Diretórios vazios que podem ser remanescentes de trabalho incompleto",
      scan: (dir) => {
        const found: string[] = [];
        const commonDirs = ["src", "lib", "app", "test", "tests", "docs"];
        for (const d of commonDirs) {
          const dp = path.join(dir, d);
          if (fs.existsSync(dp) && fs.statSync(dp).isDirectory()) {
            try {
              const contents = fs.readdirSync(dp);
              if (contents.length === 0) {
                found.push(d + "/");
              }
            } catch {
              // Pula diretórios que não podem ser lidos
            }
          }
        }
        return found;
      },
    },
    {
      category: "Configuração",
      name: "Arquivos de ambiente no código-fonte",
      severity: "critical",
      description: "Arquivos .env que podem conter segredos",
      scan: (dir) => {
        const found: string[] = [];
        const envFiles = [".env", ".env.local", ".env.production", ".env.staging"];
        for (const f of envFiles) {
          if (fs.existsSync(path.join(dir, f))) {
            found.push(f);
          }
        }
        return found;
      },
    },
  ];
}

// ---------------------------------------------------------------------------
// Funções auxiliares
// ---------------------------------------------------------------------------

function findFiles(dir: string, extensions: string[]): string[] {
  const found: string[] = [];

  function walk(current: string, depth: number): void {
    if (depth > 4) return; // Limita a profundidade da recursão
    try {
      const entries = fs.readdirSync(current, { withFileTypes: true });
      for (const entry of entries) {
        // Pula diretórios comuns que não são de código-fonte
        if (entry.isDirectory() && ["node_modules", ".git", "dist", "build", ".next", "coverage"].includes(entry.name)) {
          continue;
        }

        const fullPath = path.join(current, entry.name);
        const relativePath = path.relative(dir, fullPath);

        if (entry.isDirectory()) {
          walk(fullPath, depth + 1);
        } else if (entry.isFile()) {
          if (extensions.some((ext) => entry.name.endsWith(ext))) {
            found.push(relativePath);
          }
        }
      }
    } catch {
      // Pula diretórios que não podem ser lidos
    }
  }

  walk(dir, 0);
  return found;
}

function scanForPatterns(dir: string, patterns: string[], results: string[], baseDir: string): void {
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory()) {
        if (!["node_modules", ".git", "dist", "build"].includes(entry.name)) {
          scanForPatterns(path.join(dir, entry.name), patterns, results, baseDir);
        }
        continue;
      }

      const fullPath = path.join(dir, entry.name);
      if (!entry.name.endsWith(".ts") && !entry.name.endsWith(".tsx") && !entry.name.endsWith(".js")) {
        continue;
      }

      try {
        const content = fs.readFileSync(fullPath, "utf-8");
        const lines = content.split("\n");
        for (let i = 0; i < Math.min(lines.length, 50); i++) {
          for (const pattern of patterns) {
            if (lines[i].includes(pattern)) {
              const relative = path.relative(baseDir, fullPath);
              results.push(`${relative}:${i + 1} contém ${pattern}`);
            }
          }
        }
      } catch {
        // Pula arquivos que não podem ser lidos
      }
    }
  } catch {
    // Pula diretórios que não podem ser lidos
  }
}

// ---------------------------------------------------------------------------
// Relatórios
// ---------------------------------------------------------------------------

function pad(s: string, len: number): string {
  return s.length >= len ? s : s + " ".repeat(len - s.length);
}

function run(): void {
  const targetDir = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();

  console.log("\n" + "=".repeat(90));
  console.log("  CLEANUP SCANNER -- Relatório de Artefatos Obsoletos e Violações");
  console.log("=".repeat(90));
  console.log(`  Varrendo: ${targetDir}\n`);

  const checks = createChecks();
  const results: ScanResult[] = [];

  for (const check of checks) {
    const found = check.scan(targetDir);
    results.push({
      category: check.category,
      check: check.name,
      severity: check.severity,
      found,
      description: check.description,
    });
  }

  // Relatório
  const header = `| ${pad("Categoria", 20)}| ${pad("Verificação", 40)}| ${pad("Gravidade", 10)}| ${pad("Total", 6)}| Detalhes`;
  const sep = `|${"-".repeat(22)}|${"-".repeat(42)}|${"-".repeat(12)}|${"-".repeat(8)}|${"-".repeat(30)}`;
  console.log(header);
  console.log(sep);

  for (const r of results) {
    const count = r.found.length;
    const detail = count > 0 ? r.found.slice(0, 2).join(", ") : "(limpo)";
    const marker = count > 0 && r.severity === "critical" ? ">>" : count > 0 ? " * " : "  ";

    console.log(`${marker}| ${pad(r.category, 20)}| ${pad(r.check, 40)}| ${pad(r.severity, 10)}| ${pad(String(count), 6)}| ${detail}`);
  }

  // Resumo
  const criticals = results.filter((r) => r.severity === "critical" && r.found.length > 0);
  const warnings = results.filter((r) => r.severity === "warning" && r.found.length > 0);
  const infos = results.filter((r) => r.severity === "info" && r.found.length > 0);
  const clean = results.filter((r) => r.found.length === 0);

  console.log("\n" + "=".repeat(90));
  console.log("  RESUMO DE LIMPEZA");
  console.log("=".repeat(90) + "\n");

  console.log(`  Problemas críticos:  ${criticals.length}`);
  console.log(`  Avisos:              ${warnings.length}`);
  console.log(`  Itens informativos:  ${infos.length}`);
  console.log(`  Verificações limpas: ${clean.length}/${results.length}`);

  if (criticals.length > 0) {
    console.log("\n  AÇÃO REQUERIDA (Crítico):");
    for (const c of criticals) {
      console.log(`    - ${c.check}: ${c.found.length} item(s) encontrado(s)`);
      console.log(`      ${c.description}`);
    }
  }

  const totalIssues = results.reduce((s, r) => s + r.found.length, 0);
  if (totalIssues === 0) {
    console.log("\n  O projeto está em um estado limpo. Nenhum problema encontrado.\n");
  } else {
    console.log(`\n  Total de problemas encontrados: ${totalIssues}. Execute este scanner ao final de cada sessão para manter o estado limpo.\n`);
  }
}

run();
