/**
 * repo-reader.ts
 *
 * Lê a estrutura de diretórios de um repositório e atribui uma pontuação
 * de discoverability (capacidade de descoberta).
 * Verifica: AGENTS.md, docs/, documentação de arquitetura, rastreamento
 * de features, arquivos de handoff e outros sinais de um repositório que
 * funciona como system of record.
 *
 * Uso:
 *   npx tsx docs/lectures/lecture-03.../code/repo-reader.ts [caminho]
 *   (usa o diretório atual por padrão se nenhum caminho for informado)
 *
 * Executar:
 *   npx tsx docs/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/code/repo-reader.ts
 */

import * as fs from "node:fs";
import * as path from "node:path";

// ---------------------------------------------------------------------------
// Critérios de pontuação
// ---------------------------------------------------------------------------

interface Check {
  name: string;
  description: string;
  maxPoints: number;
  check: (dir: string) => { points: number; found: string[]; missing: string[] };
}

const checks: Check[] = [
  {
    name: "AGENTS.md / CLAUDE.md",
    description: "Arquivo de instruções legível para agentes na raiz do repo",
    maxPoints: 15,
    check: (dir) => {
      const candidates = ["AGENTS.md", "CLAUDE.md", ".claude/CLAUDE.md"];
      const found = candidates.filter((f) => fs.existsSync(path.join(dir, f)));
      return {
        points: found.length > 0 ? 15 : 0,
        found,
        missing: found.length > 0 ? [] : candidates,
      };
    },
  },
  {
    name: "Diretório de documentação",
    description: "Diretório dedicado docs/ ou documentation/",
    maxPoints: 10,
    check: (dir) => {
      const candidates = ["docs", "documentation", "doc"];
      const found = candidates.filter((f) => {
        const p = path.join(dir, f);
        return fs.existsSync(p) && fs.statSync(p).isDirectory();
      });

      return {
        points: found.length > 0 ? 10 : 0,
        found,
        missing: found.length > 0 ? [] : ["docs/"],
      };
    },
  },
  {
    name: "Documentação de arquitetura",
    description: "Arquivos descrevendo a arquitetura do sistema",
    maxPoints: 15,
    check: (dir) => {
      const patterns = [
        "architecture.md",
        "ARCHITECTURE.md",
        "docs/architecture.md",
        "docs/architecture/",
        "design.md",
        "DESIGN.md",
      ];

      const found = patterns.filter((f) =>
        fs.existsSync(path.join(dir, f))
      );

      return {
        points: found.length > 0 ? 15 : 0,
        found,
        missing:
          found.length > 0
            ? []
            : ["architecture.md ou docs/architecture/"],
      };
    },
  },
  {
    name: "Rastreamento de features",
    description: "Arquivo de lista de features ou rastreamento de tarefas",
    maxPoints: 15,
    check: (dir) => {
      const patterns = [
        "feature_list.json",
        "features.md",
        "FEATURES.md",
        "docs/features.md",
        "tasks.json",
        "TODO.md",
      ];

      const found = patterns.filter((f) =>
        fs.existsSync(path.join(dir, f))
      );

      return {
        points: found.length > 0 ? 15 : 0,
        found,
        missing:
          found.length > 0
            ? []
            : ["feature_list.json ou features.md"],
      };
    },
  },
  {
    name: "Handoff / continuidade de sessão",
    description: "Arquivos para continuidade entre múltiplas sessões",
    maxPoints: 15,
    check: (dir) => {
      const patterns = [
        "HANDOFF.md",
        "handoff.md",
        "SESSION_NOTES.md",
        "docs/handoff.md",
        ".handoff",
        "PROGRESS.md",
      ];

      const found = patterns.filter((f) =>
        fs.existsSync(path.join(dir, f))
      );

      return {
        points: found.length > 0 ? 15 : 0,
        found,
        missing:
          found.length > 0
            ? []
            : ["HANDOFF.md ou PROGRESS.md"],
      };
    },
  },
  {
    name: "Estrutura de testes",
    description: "Diretório de testes ou configuração de testes",
    maxPoints: 10,
    check: (dir) => {
      const patterns = ["test", "tests", "__tests__", "spec"];

      const found = patterns.filter((f) => {
        const p = path.join(dir, f);
        return fs.existsSync(p) && fs.statSync(p).isDirectory();
      });

      return {
        points: found.length > 0 ? 10 : 0,
        found,
        missing:
          found.length > 0 ? [] : ["test/ ou tests/"],
      };
    },
  },
  {
    name: "Arquivos de configuração",
    description: "Configuração do projeto (package.json, tsconfig, etc.)",
    maxPoints: 10,
    check: (dir) => {
      const patterns = [
        "package.json",
        "tsconfig.json",
        "pyproject.toml",
        "Cargo.toml",
        "go.mod",
      ];

      const found = patterns.filter((f) =>
        fs.existsSync(path.join(dir, f))
      );

      return {
        points: found.length > 0 ? 10 : 0,
        found,
        missing:
          found.length > 0
            ? []
            : ["package.json ou equivalente"],
      };
    },
  },
  {
    name: "README",
    description: "Arquivo README na raiz",
    maxPoints: 10,
    check: (dir) => {
      const patterns = [
        "README.md",
        "README.rst",
        "README.txt",
        "README",
      ];

      const found = patterns.filter((f) =>
        fs.existsSync(path.join(dir, f))
      );

      return {
        points: found.length > 0 ? 10 : 0,
        found,
        missing: found.length > 0 ? [] : ["README.md"],
      };
    },
  },
];

// ---------------------------------------------------------------------------
// Geração do relatório
// ---------------------------------------------------------------------------

function pad(s: string, len: number): string {
  return s.length >= len ? s : s + " ".repeat(len - s.length);
}

function scoreRepo(targetDir: string): void {
  const resolved = path.resolve(targetDir);

  if (!fs.existsSync(resolved)) {
    console.error(`  Erro: Diretório não encontrado: ${resolved}`);
    process.exit(1);
  }

  console.log("\n" + "=".repeat(80));
  console.log("  PONTUAÇÃO DE DISCOVERABILITY DO REPOSITÓRIO");
  console.log("=".repeat(80));
  console.log(`  Alvo: ${resolved}\n`);

  const header =
    `| ${pad("Critério", 30)}| ${pad("Pontos", 8)}| ${pad("Status", 10)}| Detalhes`;

  const sep =
    `|${"-".repeat(32)}|${"-".repeat(10)}|${"-".repeat(12)}|${"-".repeat(30)}`;

  console.log(header);
  console.log(sep);

  let totalScore = 0;
  let maxScore = 0;

  for (const check of checks) {
    const result = check.check(resolved);

    totalScore += result.points;
    maxScore += check.maxPoints;

    const status = result.points > 0 ? "PASSOU" : "FALHOU";

    const detail =
      result.found.length > 0
        ? result.found.join(", ")
        : result.missing[0];

    console.log(
      `| ${pad(check.name, 30)}| ${pad(result.points + "/" + check.maxPoints, 8)}| ${pad(status, 10)}| ${detail}`
    );
  }

  // Pontuação final
  console.log("\n" + "-".repeat(80));

  console.log(
    `  PONTUAÇÃO TOTAL: ${totalScore} / ${maxScore}  (${Math.round(
      (totalScore / maxScore) * 100
    )}%)`
  );

  // Nota
  const pct = totalScore / maxScore;

  let grade: string;

  if (pct >= 0.9)
    grade = "A -- Repositório é um forte system of record";
  else if (pct >= 0.7)
    grade = "B -- Boa base, pequenas lacunas";
  else if (pct >= 0.5)
    grade = "C -- Estrutura parcial, lacunas significativas";
  else if (pct >= 0.3)
    grade = "D -- Estrutura mínima, difícil para agentes navegarem";
  else
    grade = "F -- Repositório não possui sinais suficientes de discoverability";

  console.log(`  NOTA: ${grade}`);
  console.log("=".repeat(80) + "\n");
}

// ---------------------------------------------------------------------------
// Principal
// ---------------------------------------------------------------------------

const target = process.argv[2] || process.cwd();
scoreRepo(target);