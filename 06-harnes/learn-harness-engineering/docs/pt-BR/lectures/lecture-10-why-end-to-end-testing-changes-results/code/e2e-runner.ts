/**
 * e2e-runner.ts
 *
 * Um harness mínimo de testes E2E. Define casos de teste como sequências
 * de ações do usuário (importar documento -> indexar -> fazer pergunta ->
 * verificar citação). Simula sua execução e demonstra a diferença entre
 * "testes unitários passam" e "o pipeline completo funciona".
 *
 * Executar: npx tsx docs/lectures/lecture-10-why-end-to-end-testing-changes-results/code/e2e-runner.ts
 */

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

interface PipelineStep {
  name: string;
  unitTestPasses: boolean;
  // Comportamento real simulado dentro do pipeline
  actualBehavior: "works" | "fails" | "partial";
  failureReason?: string;
}

interface TestCase {
  name: string;
  steps: PipelineStep[];
}

interface TestResult {
  testCase: string;
  unitTestsPassed: number;
  unitTestsTotal: number;
  unitTestResult: "PASS" | "FAIL";
  e2eResult: "PASS" | "FAIL";
  e2eFailureStep?: string;
  e2eFailureReason?: string;
}

// ---------------------------------------------------------------------------
// Casos de teste — cenários realistas onde testes unitários passam,
// mas o E2E falha
// ---------------------------------------------------------------------------

const testCases: TestCase[] = [
  {
    name: "Importar documento e fazer uma pergunta",
    steps: [
      {
        name: "Processar documento enviado",
        unitTestPasses: true,
        actualBehavior: "works",
      },
      {
        name: "Armazenar fragmentos do documento",
        unitTestPasses: true,
        actualBehavior: "works",
      },
      {
        name: "Indexar fragmentos para recuperação",
        unitTestPasses: true,
        actualBehavior: "partial", // Indexa, mas com dimensões de embedding incorretas
        failureReason: "Incompatibilidade de dimensão de embedding entre indexador e recuperador",
      },
      {
        name: "Recuperar fragmentos relevantes",
        unitTestPasses: true, // O teste unitário usa dados simulados com dimensões corretas
        actualBehavior: "fails",
        failureReason: "Resultados vazios devido à incompatibilidade de dimensões da etapa anterior",
      },
      {
        name: "Gerar resposta com citações",
        unitTestPasses: true, // O teste unitário recebe fragmentos já recuperados
        actualBehavior: "fails",
        failureReason: "Nenhum fragmento recuperado, portanto a resposta não possui citações",
      },
    ],
  },
  {
    name: "Excluir documento e verificar remoção",
    steps: [
      {
        name: "Encontrar documento pelo ID",
        unitTestPasses: true,
        actualBehavior: "works",
      },
      {
        name: "Excluir registro do documento",
        unitTestPasses: true,
        actualBehavior: "works",
      },
      {
        name: "Remover fragmentos indexados",
        unitTestPasses: true,
        actualBehavior: "fails", // Fragmentos órfãos permanecem no índice
        failureReason: "A consulta de limpeza do índice excedeu o tempo limite e deixou fragmentos órfãos",
      },
      {
        name: "Verificar que o documento não aparece nos resultados de busca",
        unitTestPasses: true, // O teste unitário simula a busca
        actualBehavior: "fails",
        failureReason: "Fragmentos órfãos da etapa anterior ainda aparecem nos resultados",
      },
    ],
  },
  {
    name: "Acesso concorrente de múltiplos usuários",
    steps: [
      {
        name: "Usuário A importa documento",
        unitTestPasses: true,
        actualBehavior: "works",
      },
      {
        name: "Usuário B importa documento",
        unitTestPasses: true,
        actualBehavior: "works",
      },
      {
        name: "Usuário A consulta seu documento",
        unitTestPasses: true,
        actualBehavior: "partial", // Contaminação cruzada de resultados
        failureReason: "Recuperação sem escopo por usuário, retornando fragmentos do documento do Usuário B",
      },
      {
        name: "Verificar que apenas resultados do Usuário A foram retornados",
        unitTestPasses: true,
        actualBehavior: "fails",
        failureReason: "Os resultados incluem documentos de outros usuários",
      },
    ],
  },
];

// ---------------------------------------------------------------------------
// Executar testes
// ---------------------------------------------------------------------------

function runUnitTests(tc: TestCase): { passed: number; total: number } {
  const passed = tc.steps.filter((s) => s.unitTestPasses).length;
  return { passed, total: tc.steps.length };
}

function runE2ETest(tc: TestCase): { pass: boolean; failureStep?: string; failureReason?: string } {
  // Pipeline: se qualquer etapa falhar de fato, todo o E2E falha
  for (const step of tc.steps) {
    if (step.actualBehavior === "fails") {
      return {
        pass: false,
        failureStep: step.name,
        failureReason: step.failureReason ?? "Falha desconhecida",
      };
    }
    // "partial" significa que a etapa tecnicamente conclui,
    // mas cria problemas para etapas posteriores
  }

  // Verifica se houve alguma etapa "partial"
  const partialSteps = tc.steps.filter((s) => s.actualBehavior === "partial");

  if (partialSteps.length > 0) {
    // Nesta simulação, etapas parciais sempre levam a falhas posteriores
    // caso não exista uma etapa explícita marcada como "fails"
    return {
      pass: false,
      failureStep: partialSteps[partialSteps.length - 1].name,
      failureReason:
        partialSteps[partialSteps.length - 1].failureReason ?? "Conclusão parcial",
    };
  }

  return { pass: true };
}

// ---------------------------------------------------------------------------
// Relatórios
// ---------------------------------------------------------------------------

function pad(s: string, len: number): string {
  return s.length >= len ? s : s + " ".repeat(len - s.length);
}

function run(): void {
  console.log("\n" + "=".repeat(95));
  console.log("  EXECUTOR DE TESTES E2E -- Testes Unitários vs Pipeline Completo");
  console.log("=".repeat(95));

  const results: TestResult[] = testCases.map((tc) => {
    const unit = runUnitTests(tc);
    const e2e = runE2ETest(tc);

    return {
      testCase: tc.name,
      unitTestsPassed: unit.passed,
      unitTestsTotal: unit.total,
      unitTestResult: unit.passed === unit.total ? "PASS" : "FAIL",
      e2eResult: e2e.pass ? "PASS" : "FAIL",
      e2eFailureStep: e2e.failureStep,
      e2eFailureReason: e2e.failureReason,
    };
  });

  // Detalhes por caso de teste
  for (let i = 0; i < testCases.length; i++) {
    const tc = testCases[i];
    const r = results[i];

    console.log("\n  Caso de Teste: " + tc.name);
    console.log("  " + "-".repeat(70));

    const stepHeader = `  | ${pad("Etapa", 40)}| ${pad("Teste Unitário", 11)}| ${pad("E2E Real", 12)}|`;
    const stepSep = `  |${"-".repeat(42)}|${"-".repeat(13)}|${"-".repeat(14)}|`;
    console.log(stepHeader);
    console.log(stepSep);

    for (const step of tc.steps) {
      const utLabel = step.unitTestPasses ? "PASS" : "FAIL";

      let e2eLabel: string;
      if (step.actualBehavior === "works") e2eLabel = "PASS";
      else if (step.actualBehavior === "partial") e2eLabel = "PARCIAL*";
      else e2eLabel = "FAIL";

      const marker = step.actualBehavior !== "works" ? ">>" : "  ";

      console.log(
        `${marker}| ${pad(step.name, 40)}| ${pad(utLabel, 11)}| ${pad(e2eLabel, 12)}|`
      );
    }

    if (r.e2eFailureStep) {
      console.log(`\n  Falha E2E em: ${r.e2eFailureStep}`);
      console.log(`  Motivo: ${r.e2eFailureReason}`);
    }
  }

  // Comparação resumida
  console.log("\n" + "=".repeat(95));
  console.log("  COMPARAÇÃO: Testes Unitários vs Testes E2E");
  console.log("=".repeat(95) + "\n");

  const header = `| ${pad("Caso de Teste", 35)}| ${pad("Testes Unitários", 15)}| ${pad("Resultado E2E", 12)}| Divergência`;
  const sep = `|${"-".repeat(37)}|${"-".repeat(17)}|${"-".repeat(14)}|${"-".repeat(30)}`;

  console.log(header);
  console.log(sep);

  for (const r of results) {
    const utLabel = `${r.unitTestsPassed}/${r.unitTestsTotal} ${r.unitTestResult}`;
    const discrepancy =
      r.unitTestResult === "PASS" && r.e2eResult === "FAIL";

    const discLabel = discrepancy
      ? "UNIT PASS MAS E2E FAIL"
      : "Consistente";

    console.log(
      `| ${pad(r.testCase, 35)}| ${pad(utLabel, 15)}| ${pad(r.e2eResult, 12)}| ${discLabel}`
    );
  }

  const falseConfidence = results.filter(
    (r) => r.unitTestResult === "PASS" && r.e2eResult === "FAIL"
  ).length;

  console.log("\n  Quantidade de falsos positivos de confiança: " + falseConfidence + " de " + results.length);
  console.log(
    "  Os testes unitários passam, mas os testes E2E revelam falhas de integração que os testes unitários não conseguem detectar.\n"
  );
}

run();