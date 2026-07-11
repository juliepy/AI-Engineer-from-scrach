import { existsSync, readFileSync, readdirSync } from "node:fs"
import path from "node:path"

type Finding = {
  docPath: string
  line: number
  ref: string
  message: string
}

const repoRoot = path.resolve(__dirname, "..")
const docsRoot = path.join(repoRoot, "docs")

function walk(dir: string): string[] {
  const entries = readdirSync(dir, { withFileTypes: true }) as Array<{
    name: string
    isDirectory(): boolean
    isFile(): boolean
  }>
  const out: string[] = []
  for (const entry of entries) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) out.push(...walk(full))
    else if (entry.isFile()) out.push(full)
  }
  return out
}

function isProjectDoc(filePath: string): boolean {
  const normalized = filePath.split(path.sep).join("/")
  return /\/docs\/[^/]+\/projects\/project-\d{2}-[^/]+\/index\.md$/.test(normalized)
}

const backtickRe = /`([^`]+)`/g

function validatePathLiteral(
  docPath: string,
  line: number,
  ref: string,
  findings: Finding[],
): void {
  const trimmed = ref.trim()

  if (trimmed === "starter/" || trimmed === "solution/") return
  // Project docs often mention per-project commands like `./init.sh` or `./scripts/*.sh`
  // which are only valid after `cd projects/project-XX/...`. We treat those as context-relative
  // and do not validate them at repo root.
  if (trimmed === "./init.sh" || trimmed.startsWith("./scripts/")) return

  // Only validate repo-relative path literals; avoid false positives like "main / preload / renderer".
  const isRepoRelative =
    trimmed.startsWith("projects/") ||
    trimmed.startsWith("docs/") ||
    trimmed.startsWith("scripts/") ||
    trimmed.startsWith("./")
  if (!isRepoRelative) return

  const normalized = trimmed.startsWith("./") ? trimmed.slice(2) : trimmed
  const abs = path.join(repoRoot, normalized)
  if (!existsSync(abs)) {
    findings.push({
      docPath,
      line,
      ref: trimmed,
      message: `Path does not exist: ${normalized}`,
    })
  }
}

function validateProjectArtifacts(findings: Finding[]): void {
  for (let i = 1; i <= 6; i += 1) {
    const projectId = `project-${String(i).padStart(2, "0")}`
    const projectRoot = path.join(repoRoot, "projects", projectId)
    const starterRoot = path.join(projectRoot, "starter")
    const solutionRoot = path.join(projectRoot, "solution")

    if (!existsSync(projectRoot)) {
      findings.push({
        docPath: "scripts/validate-project-docs.ts",
        line: 1,
        ref: projectRoot,
        message: "Project directory missing",
      })
      continue
    }

    if (!existsSync(starterRoot)) {
      findings.push({
        docPath: "scripts/validate-project-docs.ts",
        line: 1,
        ref: starterRoot,
        message: "starter/ directory missing",
      })
    }

    if (!existsSync(solutionRoot)) {
      findings.push({
        docPath: "scripts/validate-project-docs.ts",
        line: 1,
        ref: solutionRoot,
        message: "solution/ directory missing",
      })
    }

    // Project 01 contract: starter has task prompt only; solution has harness artifacts.
    if (projectId === "project-01") {
      const expectedStarter = ["task-prompt.md"]
      for (const file of expectedStarter) {
        const abs = path.join(starterRoot, file)
        if (!existsSync(abs)) {
          findings.push({
            docPath: "projects/project-01/README.md",
            line: 1,
            ref: `projects/project-01/starter/${file}`,
            message: "Expected file missing for Project 01 starter contract",
          })
        }
      }

      const expectedSolution = ["AGENTS.md", "feature_list.json", "init.sh", "claude-progress.md", "CLAUDE.md"]
      for (const file of expectedSolution) {
        const abs = path.join(solutionRoot, file)
        if (!existsSync(abs)) {
          findings.push({
            docPath: "projects/project-01/README.md",
            line: 1,
            ref: `projects/project-01/solution/${file}`,
            message: "Expected file missing for Project 01 solution contract",
          })
        }
      }
    }

    // Project 02 contract: solution includes continuity docs.
    if (projectId === "project-02") {
      const expectedSolution = [
        "docs/ARCHITECTURE.md",
        "docs/PRODUCT.md",
        "feature_list.json",
        "session-handoff.md",
        "AGENTS.md",
      ]
      for (const rel of expectedSolution) {
        const abs = path.join(solutionRoot, rel)
        if (!existsSync(abs)) {
          findings.push({
            docPath: "projects/project-02/README.md",
            line: 1,
            ref: `projects/project-02/solution/${rel}`,
            message: "Expected artifact missing for Project 02 solution contract",
          })
        }
      }
    }

    // Project 03 contract: solution includes init + handoff + clean-state artifacts.
    if (projectId === "project-03") {
      const expectedSolution = [
        "feature_list.json",
        "init.sh",
        "session-handoff.md",
        "claude-progress.md",
        "clean-state-checklist.md",
        "AGENTS.md",
      ]
      for (const rel of expectedSolution) {
        const abs = path.join(solutionRoot, rel)
        if (!existsSync(abs)) {
          findings.push({
            docPath: "projects/project-03/README.md",
            line: 1,
            ref: `projects/project-03/solution/${rel}`,
            message: "Expected artifact missing for Project 03 solution contract",
          })
        }
      }
    }

    // Project 04 contract: solution includes architecture check + clean-state checklist.
    if (projectId === "project-04") {
      const expectedSolution = [
        "scripts/check-architecture.sh",
        "docs/ARCHITECTURE.md",
        "clean-state-checklist.md",
        "AGENTS.md",
      ]
      for (const rel of expectedSolution) {
        const abs = path.join(solutionRoot, rel)
        if (!existsSync(abs)) {
          findings.push({
            docPath: "projects/project-04/README.md",
            line: 1,
            ref: `projects/project-04/solution/${rel}`,
            message: "Expected artifact missing for Project 04 solution contract",
          })
        }
      }
    }

    // Project 05 contract: three solution variants must include evaluator rubric; plan-gen-eval adds sprint contract.
    if (projectId === "project-05") {
      const variants = ["single-role", "gen-eval", "plan-gen-eval"] as const
      for (const variant of variants) {
        const variantRoot = path.join(solutionRoot, variant)
        if (!existsSync(variantRoot)) {
          findings.push({
            docPath: "projects/project-05/README.md",
            line: 1,
            ref: `projects/project-05/solution/${variant}/`,
            message: "Expected variant directory missing for Project 05 solution contract",
          })
          continue
        }

        const required = ["AGENTS.md", "clean-state-checklist.md", "evaluator-rubric.md"]
        for (const rel of required) {
          const abs = path.join(variantRoot, rel)
          if (!existsSync(abs)) {
            findings.push({
              docPath: "projects/project-05/README.md",
              line: 1,
              ref: `projects/project-05/solution/${variant}/${rel}`,
              message: "Expected artifact missing for Project 05 variant contract",
            })
          }
        }

        if (variant === "plan-gen-eval") {
          const abs = path.join(variantRoot, "sprint-contract.md")
          if (!existsSync(abs)) {
            findings.push({
              docPath: "projects/project-05/README.md",
              line: 1,
              ref: "projects/project-05/solution/plan-gen-eval/sprint-contract.md",
              message: "Expected sprint contract missing for plan-gen-eval variant",
            })
          }
        }
      }
    }

    // Project 06 contract: solution has benchmark and cleanup scripts.
    if (projectId === "project-06") {
      const expected = ["scripts/benchmark.sh", "scripts/cleanup-scanner.sh", "scripts/check-architecture.sh"]
      for (const rel of expected) {
        const abs = path.join(solutionRoot, rel)
        if (!existsSync(abs)) {
          findings.push({
            docPath: "projects/project-06/README.md",
            line: 1,
            ref: `projects/project-06/solution/${rel}`,
            message: "Expected script missing for Project 06 solution contract",
          })
        }
      }
    }
  }
}

function main(): void {
  const mdFiles = walk(docsRoot).filter((p) => p.endsWith(".md") && isProjectDoc(p))
  const findings: Finding[] = []

  for (const filePath of mdFiles) {
    const relDoc = path.relative(repoRoot, filePath).split(path.sep).join("/")
    const content = readFileSync(filePath, "utf-8")
    const lines = content.split("\n")
    for (let i = 0; i < lines.length; i += 1) {
      const lineNo = i + 1
      const line = lines[i]
      if (!line.includes("`")) continue
      for (const match of line.matchAll(backtickRe)) {
        validatePathLiteral(relDoc, lineNo, match[1], findings)
      }
    }
  }

  validateProjectArtifacts(findings)

  if (findings.length === 0) {
    // eslint-disable-next-line no-console
    console.log("OK: no missing repo-relative path literals in project docs.")
    return
  }

  // eslint-disable-next-line no-console
  console.error(`Found ${findings.length} invalid path reference(s):`)
  for (const f of findings) {
    // eslint-disable-next-line no-console
    console.error(`- ${f.docPath}:${f.line} \`${f.ref}\` -> ${f.message}`)
  }
  process.exitCode = 1
}

main()
