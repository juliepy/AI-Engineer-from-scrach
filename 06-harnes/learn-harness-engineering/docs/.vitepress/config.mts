/// <reference types="node" />
import { defineConfig } from "vitepress";
import { withMermaid } from "vitepress-plugin-mermaid";

const docsBase = "/learn-harness-engineering/";
const brandLogo = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%23D95C41" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="12.1" y1="11.9" x2="18.9" y2="8.2" /><line x1="12.1" y1="12.1" x2="20.3" y2="12.9" /><line x1="12.2" y1="12.4" x2="16.6" y2="19.1" /><line x1="11.8" y1="12.4" x2="7.3" y2="19.2" /><line x1="11.9" y1="12.1" x2="3.7" y2="13.3" /><line x1="11.8" y1="11.7" x2="7.8" y2="4.4" /></svg>';
const githubRepoTreeLink = "https://github.com/walkinglabs/learn-harness-engineering/tree/main";

const zhLectureItems = [
  { text: "欢迎", link: "/zh/" },
  { text: "模型能力强，不等于执行可靠", link: "/zh/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "Harness 的定义", link: "/zh/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "让代码仓库成为唯一的事实来源", link: "/zh/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "把指令拆分到不同文件里", link: "/zh/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "让跨会话的任务保持上下文连续", link: "/zh/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "让 agent 每次工作前先初始化", link: "/zh/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "给 agent 划清每次任务的边界", link: "/zh/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "用功能清单约束 agent 该做什么", link: "/zh/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "防止 agent 提前宣告完成", link: "/zh/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "跑通完整流程才算真正验证", link: "/zh/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "让 agent 的运行过程可观测", link: "/zh/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "每次会话结束前都做好交接", link: "/zh/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" }
];

const zhProjectItems = [
  { text: "欢迎", link: "/zh/projects/" },
  { text: "提示词驱动 vs 规则驱动", link: "/zh/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "让项目可读并接住上次工作", link: "/zh/projects/project-02-agent-readable-workspace/" },
  { text: "跨会话工作连续性", link: "/zh/projects/project-03-multi-session-continuity/" },
  { text: "运行反馈与行为修正", link: "/zh/projects/project-04-incremental-indexing/" },
  { text: "工作评审与自我验证", link: "/zh/projects/project-05-grounded-qa-verification/" },
  { text: "综合 Agent 工作环境", link: "/zh/projects/project-06-runtime-observability-and-debugging/" }
];

const zhResourceItems = [
  { text: "资料库总览", link: "/zh/resources/" },
  { text: "中文模板", link: "/zh/resources/templates/" },
  { text: "中文参考", link: "/zh/resources/reference/" },
  { text: "高级资源包", link: "/zh/resources/openai-advanced/" }
];

const zhSkillItems = [
  { text: "技能总览", link: "/zh/skills/" }
];

const enLectureItems = [
  { text: "Welcome", link: "/en/" },
  { text: "Why Capable Agents Still Fail", link: "/en/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "What a Harness Actually Is", link: "/en/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "Why the Repository Must Become the System of Record", link: "/en/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "Why One Giant Instruction File Fails", link: "/en/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "Why Long-Running Tasks Lose Continuity", link: "/en/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "Why Initialization Needs Its Own Phase", link: "/en/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "Why Agents Overreach and Under-Finish", link: "/en/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "Why Feature Lists Are Harness Primitives", link: "/en/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "Why Agents Declare Victory Too Early", link: "/en/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "Why End-to-End Testing Changes Results", link: "/en/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "Why Observability Belongs Inside the Harness", link: "/en/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "Why Every Session Must Leave a Clean State", link: "/en/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" }
];

const enProjectItems = [
  { text: "Welcome", link: "/en/projects/" },
  { text: "Prompt-Only vs. Rules-First", link: "/en/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "Agent-Readable Workspace", link: "/en/projects/project-02-agent-readable-workspace/" },
  { text: "Multi-Session Continuity", link: "/en/projects/project-03-multi-session-continuity/" },
  { text: "Runtime Feedback and Scope Control", link: "/en/projects/project-04-incremental-indexing/" },
  { text: "Self-Verification and Role Separation", link: "/en/projects/project-05-grounded-qa-verification/" },
  { text: "Complete Harness (Capstone)", link: "/en/projects/project-06-runtime-observability-and-debugging/" }
];

const enResourceItems = [
  { text: "Overview", link: "/en/resources/" },
  { text: "English Templates", link: "/en/resources/templates/" },
  { text: "English Reference", link: "/en/resources/reference/" },
  { text: "Advanced Pack", link: "/en/resources/openai-advanced/" }
];

const enSkillItems = [
  { text: "Skills Overview", link: "/en/skills/" }
];

const viLectureItems = [
  { text: "Chào mừng", link: "/vi/" },
  { text: "Tại sao các Agent mạnh vẫn thất bại", link: "/vi/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "Harness thực sự là gì", link: "/vi/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "Tại sao Repository phải trở thành Nguồn sự thật", link: "/vi/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "Tại sao một file hướng dẫn khổng lồ lại thất bại", link: "/vi/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "Tại sao các tác vụ dài hạn lại mất tính liên tục", link: "/vi/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "Tại sao quá trình khởi tạo cần một giai đoạn riêng", link: "/vi/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "Tại sao Agent làm quá giới hạn và chưa hoàn thành", link: "/vi/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "Tại sao Feature List là nguyên lý cốt lõi của Harness", link: "/vi/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "Tại sao Agent tuyên bố thành công quá sớm", link: "/vi/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "Tại sao kiểm thử End-to-End thay đổi kết quả", link: "/vi/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "Tại sao tính quan sát thuộc về bên trong Harness", link: "/vi/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "Tại sao mỗi phiên làm việc phải để lại trạng thái sạch", link: "/vi/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" }
];

const viProjectItems = [
  { text: "Chào mừng", link: "/vi/projects/" },
  { text: "Chỉ Prompt vs. Ưu tiên Quy tắc", link: "/vi/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "Không gian làm việc Agent đọc được", link: "/vi/projects/project-02-agent-readable-workspace/" },
  { text: "Tính liên tục đa phiên", link: "/vi/projects/project-03-multi-session-continuity/" },
  { text: "Phản hồi Runtime và Kiểm soát Phạm vi", link: "/vi/projects/project-04-incremental-indexing/" },
  { text: "Tự xác minh và Phân tách Vai trò", link: "/vi/projects/project-05-grounded-qa-verification/" },
  { text: "Harness Hoàn chỉnh", link: "/vi/projects/project-06-runtime-observability-and-debugging/" },
];

const viResourceItems = [
  { text: "Tổng quan", link: "/vi/resources/" },
  { text: "Mẫu tiếng Anh", link: "/vi/resources/templates/" },
  { text: "Tài liệu tham khảo tiếng Anh", link: "/vi/resources/reference/" },
  { text: "Gói Nâng cao", link: "/vi/resources/openai-advanced/" },
];

const viSkillItems = [
  { text: "Tổng quan về Kỹ năng", link: "/vi/skills/" },
];

const ruLectureItems = [
  { text: "Добро пожаловать", link: "/ru/" },
  { text: "Сильная модель ≠ надёжное исполнение", link: "/ru/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "Что такое harness на самом деле", link: "/ru/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "Репозиторий как единый источник правды", link: "/ru/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "Почему один большой файл инструкций не работает", link: "/ru/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "Как сохранять контекст между сессиями", link: "/ru/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "Зачем инициализация — отдельная фаза", link: "/ru/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "Почему агенты делают слишком много или слишком мало", link: "/ru/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "Списки фич как примитивы harness", link: "/ru/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "Почему агенты слишком рано объявляют успех", link: "/ru/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "Только сквозной прогон — настоящая проверка", link: "/ru/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "Наблюдаемость — часть harness", link: "/ru/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "Каждая сессия должна оставлять чистое состояние", link: "/ru/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" },
];

const ruProjectItems = [
  { text: "Добро пожаловать", link: "/ru/projects/" },
  { text: "Только промпты vs правила", link: "/ru/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "Рабочее пространство для агента", link: "/ru/projects/project-02-agent-readable-workspace/" },
  { text: "Непрерывность между сессиями", link: "/ru/projects/project-03-multi-session-continuity/" },
  { text: "Обратная связь и контроль скоупа", link: "/ru/projects/project-04-incremental-indexing/" },
  { text: "Самопроверка и обоснованные ответы", link: "/ru/projects/project-05-grounded-qa-verification/" },
  { text: "Полный harness (капстоун)", link: "/ru/projects/project-06-runtime-observability-and-debugging/" },
];

const ruResourceItems = [
  { text: "Обзор", link: "/ru/resources/" },
  { text: "Шаблоны", link: "/ru/resources/templates/" },
  { text: "Справочник", link: "/ru/resources/reference/" },
  { text: "Расширенный пакет", link: "/ru/resources/openai-advanced/" },
];

const ruSkillItems = [
  { text: "Обзор скиллов", link: "/ru/skills/" },
];

const uzLectureItems = [
  { text: "Xush kelibsiz", link: "/uz/" },
  { text: "Kuchli agentlar nega hali ham yiqiladi", link: "/uz/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "Harness aslida nima", link: "/uz/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "Repozitoriy nega yagona haqiqat manbai boʻlishi kerak", link: "/uz/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "Bitta katta yoʻriqnoma fayli nega ishlamaydi", link: "/uz/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "Uzoq vazifalar nega kontekstni yoʻqotadi", link: "/uz/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "Inisializatsiya nega alohida bosqich boʻlishi kerak", link: "/uz/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "Agentlar nega haddan oshib, oxirigacha yetmaydi", link: "/uz/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "Funksiyalar roʻyxati nega harness primitivi", link: "/uz/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "Agentlar nega vaqtidan oldin gʻalabani eʼlon qiladi", link: "/uz/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "End-to-end testlar nega natijani oʻzgartiradi", link: "/uz/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "Kuzatuvchanlik nega harness ichida boʻlishi kerak", link: "/uz/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "Har bir sessiya nega toza holat qoldirishi kerak", link: "/uz/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" },
];

const uzProjectItems = [
  { text: "Xush kelibsiz", link: "/uz/projects/" },
  { text: "Faqat prompt vs. qoidalar ustuvor", link: "/uz/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "Agent oʻqiy oladigan ish maydoni", link: "/uz/projects/project-02-agent-readable-workspace/" },
  { text: "Koʻp sessiyali davomiylik", link: "/uz/projects/project-03-multi-session-continuity/" },
  { text: "Runtime fikr-mulohaza va skoup nazorati", link: "/uz/projects/project-04-incremental-indexing/" },
  { text: "Oʻz-oʻzini tekshirish va rollarni ajratish", link: "/uz/projects/project-05-grounded-qa-verification/" },
  { text: "Toʻliq harness (yakuniy loyiha)", link: "/uz/projects/project-06-runtime-observability-and-debugging/" },
];

const uzResourceItems = [
  { text: "Umumiy koʻrinish", link: "/uz/resources/" },
  { text: "Shablonlar", link: "/uz/resources/templates/" },
  { text: "Maʼlumotnoma", link: "/uz/resources/reference/" },
  { text: "Kengaytirilgan paket", link: "/uz/resources/openai-advanced/" },
];

const uzSkillItems = [
  { text: "Malakalar umumiy koʻrinishi", link: "/uz/skills/" },
];

const koLectureItems = [
  { text: "환영합니다", link: "/ko/" },
  { text: "유능한 에이전트가 여전히 실패하는 이유", link: "/ko/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "하네스란 무엇인가", link: "/ko/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "저장소가 시스템 오브 레코드(SoR)가 되어야 하는 이유", link: "/ko/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "거대한 단일 지시 파일이 실패하는 이유", link: "/ko/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "장기 작업이 연속성을 잃는 이유", link: "/ko/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "초기화가 별도 단계여야 하는 이유", link: "/ko/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "에이전트가 과도하게 손대고 끝맺지 못하는 이유", link: "/ko/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "기능 목록이 하네스의 기본 단위인 이유", link: "/ko/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "에이전트가 너무 일찍 완료를 선언하는 이유", link: "/ko/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "엔드투엔드 테스트가 결과를 바꾸는 이유", link: "/ko/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "관측 가능성이 하네스 안에 있어야 하는 이유", link: "/ko/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "모든 세션이 클린 상태로 끝나야 하는 이유", link: "/ko/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" },
];

const koProjectItems = [
  { text: "환영합니다", link: "/ko/projects/" },
  { text: "프롬프트 단독 vs 규칙 우선", link: "/ko/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "에이전트가 읽을 수 있는 작업 공간", link: "/ko/projects/project-02-agent-readable-workspace/" },
  { text: "다중 세션 연속성", link: "/ko/projects/project-03-multi-session-continuity/" },
  { text: "런타임 피드백과 범위 제어", link: "/ko/projects/project-04-incremental-indexing/" },
  { text: "자기 검증과 역할 분리", link: "/ko/projects/project-05-grounded-qa-verification/" },
  { text: "완성형 하네스(캡스톤)", link: "/ko/projects/project-06-runtime-observability-and-debugging/" },
];

const koResourceItems = [
  { text: "리소스 모음 개요", link: "/ko/resources/" },
  { text: "한국어 템플릿", link: "/ko/resources/templates/" },
  { text: "한국어 레퍼런스", link: "/ko/resources/reference/" },
  { text: "고급 리소스 팩", link: "/ko/resources/openai-advanced/" },
];

const koSkillItems = [
  { text: "스킬 개요", link: "/ko/skills/" },
];

const jaLectureItems = [
  { text: "ようこそ", link: "/ja/" },
  { text: "強いモデルは信頼できる実行を意味しない", link: "/ja/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "Harness とは何か", link: "/ja/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "リポジトリを唯一の信頼できる情報源にする", link: "/ja/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "指示を複数ファイルに分割する", link: "/ja/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "セッションをまたいでコンテキストを保つ", link: "/ja/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "すべてのエージェントセッション前に初期化する", link: "/ja/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "エージェントのタスク境界を明確にする", link: "/ja/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "機能リストでエージェントの作業を制約する", link: "/ja/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "エージェントの早すぎる完了宣言を防ぐ", link: "/ja/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "End-to-End テストだけが本当の検証である", link: "/ja/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "エージェントのランタイムを観測可能にする", link: "/ja/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "すべてのセッションをきれいな引き継ぎで終える", link: "/ja/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" },
];

const jaProjectItems = [
  { text: "ようこそ", link: "/ja/projects/" },
  { text: "プロンプトのみ vs ルール優先", link: "/ja/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "プロジェクトを読みやすくし、中断地点から再開する", link: "/ja/projects/project-02-agent-readable-workspace/" },
  { text: "セッション再起動後もエージェントが作業を続ける", link: "/ja/projects/project-03-multi-session-continuity/" },
  { text: "ランタイムフィードバックでエージェントの挙動を修正する", link: "/ja/projects/project-04-incremental-indexing/" },
  { text: "エージェントに自分の作業を検証させる", link: "/ja/projects/project-05-grounded-qa-verification/" },
  { text: "完全なエージェント harness を構築する（総合課題）", link: "/ja/projects/project-06-runtime-observability-and-debugging/" },
];

const jaResourceItems = [
  { text: "概要", link: "/ja/resources/" },
  { text: "テンプレート", link: "/ja/resources/templates/" },
  { text: "リファレンス", link: "/ja/resources/reference/" },
  { text: "高度なパック", link: "/ja/resources/openai-advanced/" },
];

const jaSkillItems = [
  { text: "スキル概要", link: "/ja/skills/" },
];

const esLectureItems = [
  { text: "Bienvenido", link: "/es/" },
  { text: "Los modelos fuertes no significan ejecución fiable", link: "/es/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "Qué significa realmente harness", link: "/es/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "Convierte el repositorio en la fuente única de verdad", link: "/es/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "Divide las instrucciones entre archivos", link: "/es/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "Mantén vivo el contexto entre sesiones", link: "/es/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "Inicializa antes de cada sesión del agente", link: "/es/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "Define límites claros para las tareas del agente", link: "/es/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "Usa listas de funciones para limitar al agente", link: "/es/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "Evita que los agentes declaren victoria demasiado pronto", link: "/es/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "Solo las pruebas end-to-end son verificación real", link: "/es/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "Haz observable el runtime del agente", link: "/es/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "Deja un handoff limpio al final de cada sesión", link: "/es/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" },
];

const esProjectItems = [
  { text: "Bienvenido", link: "/es/projects/" },
  { text: "Solo prompt vs reglas primero", link: "/es/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "Haz el proyecto legible y retoma el trabajo", link: "/es/projects/project-02-agent-readable-workspace/" },
  { text: "Mantén al agente trabajando tras reiniciar sesiones", link: "/es/projects/project-03-multi-session-continuity/" },
  { text: "Usa feedback de runtime para corregir el comportamiento", link: "/es/projects/project-04-incremental-indexing/" },
  { text: "Haz que el agente verifique su propio trabajo", link: "/es/projects/project-05-grounded-qa-verification/" },
  { text: "Construye un harness completo (capstone)", link: "/es/projects/project-06-runtime-observability-and-debugging/" },
];

const esResourceItems = [
  { text: "Resumen", link: "/es/resources/" },
  { text: "Plantillas", link: "/es/resources/templates/" },
  { text: "Referencia", link: "/es/resources/reference/" },
  { text: "Paquete avanzado", link: "/es/resources/openai-advanced/" },
];

const esSkillItems = [
  { text: "Resumen de Skills", link: "/es/skills/" },
];

const frLectureItems = [
  { text: "Bienvenue", link: "/fr/" },
  { text: "Les modèles forts ne garantissent pas une exécution fiable", link: "/fr/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "Ce que signifie vraiment harness", link: "/fr/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "Faire du dépôt la source unique de vérité", link: "/fr/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "Répartir les instructions entre fichiers", link: "/fr/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "Garder le contexte vivant entre les sessions", link: "/fr/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "Initialiser avant chaque session d'agent", link: "/fr/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "Définir des limites de tâche claires", link: "/fr/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "Utiliser les listes de fonctionnalités pour contraindre l'agent", link: "/fr/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "Empêcher les agents de déclarer victoire trop tôt", link: "/fr/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "Seul le test end-to-end est une vraie vérification", link: "/fr/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "Rendre le runtime de l'agent observable", link: "/fr/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "Laisser un handoff propre à la fin de chaque session", link: "/fr/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" },
];

const frProjectItems = [
  { text: "Bienvenue", link: "/fr/projects/" },
  { text: "Prompt seul vs règles d'abord", link: "/fr/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "Rendre le projet lisible et reprendre", link: "/fr/projects/project-02-agent-readable-workspace/" },
  { text: "Garder l'agent au travail après les redémarrages", link: "/fr/projects/project-03-multi-session-continuity/" },
  { text: "Utiliser le feedback runtime pour corriger le comportement", link: "/fr/projects/project-04-incremental-indexing/" },
  { text: "Faire vérifier son propre travail par l'agent", link: "/fr/projects/project-05-grounded-qa-verification/" },
  { text: "Construire un harness complet (capstone)", link: "/fr/projects/project-06-runtime-observability-and-debugging/" },
];

const frResourceItems = [
  { text: "Aperçu", link: "/fr/resources/" },
  { text: "Modèles", link: "/fr/resources/templates/" },
  { text: "Référence", link: "/fr/resources/reference/" },
  { text: "Pack avancé", link: "/fr/resources/openai-advanced/" },
];

const frSkillItems = [
  { text: "Aperçu des Skills", link: "/fr/skills/" },
];

const deLectureItems = [
  { text: "Willkommen", link: "/de/" },
  { text: "Starke Modelle bedeuten keine zuverlässige Ausführung", link: "/de/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "Was harness wirklich bedeutet", link: "/de/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "Das Repository zur einzigen Quelle der Wahrheit machen", link: "/de/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "Anweisungen auf Dateien verteilen", link: "/de/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "Kontext über Sessions hinweg erhalten", link: "/de/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "Vor jeder Agenten-Session initialisieren", link: "/de/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "Klare Aufgabengrenzen für Agenten ziehen", link: "/de/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "Feature-Listen nutzen, um Agentenarbeit zu begrenzen", link: "/de/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "Verhindern, dass Agenten zu früh Erfolg melden", link: "/de/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "Nur End-to-End-Tests sind echte Verifikation", link: "/de/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "Die Runtime des Agenten beobachtbar machen", link: "/de/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "Sauberes Handoff am Ende jeder Session", link: "/de/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" },
];

const deProjectItems = [
  { text: "Willkommen", link: "/de/projects/" },
  { text: "Nur Prompt vs Regeln zuerst", link: "/de/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "Das Projekt lesbar machen und weiterarbeiten", link: "/de/projects/project-02-agent-readable-workspace/" },
  { text: "Den Agenten über Session-Neustarts hinweg weiterarbeiten lassen", link: "/de/projects/project-03-multi-session-continuity/" },
  { text: "Runtime-Feedback nutzen, um Agentenverhalten zu korrigieren", link: "/de/projects/project-04-incremental-indexing/" },
  { text: "Den Agenten seine eigene Arbeit verifizieren lassen", link: "/de/projects/project-05-grounded-qa-verification/" },
  { text: "Einen vollständigen Agenten-harness bauen (Capstone)", link: "/de/projects/project-06-runtime-observability-and-debugging/" },
];

const deResourceItems = [
  { text: "Übersicht", link: "/de/resources/" },
  { text: "Vorlagen", link: "/de/resources/templates/" },
  { text: "Referenz", link: "/de/resources/reference/" },
  { text: "Erweitertes Paket", link: "/de/resources/openai-advanced/" },
];

const deSkillItems = [
  { text: "Skills Übersicht", link: "/de/skills/" },
];

const arLectureItems = [
  { text: "مرحبًا", link: "/ar/" },
  { text: "النماذج القوية لا تعني تنفيذًا موثوقًا", link: "/ar/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "ما معنى harness فعليًا", link: "/ar/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "اجعل المستودع مصدر الحقيقة الوحيد", link: "/ar/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "قسّم التعليمات عبر ملفات", link: "/ar/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "حافظ على السياق عبر الجلسات", link: "/ar/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "هيئ قبل كل جلسة وكيل", link: "/ar/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "ارسم حدود مهمة واضحة للوكلاء", link: "/ar/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "استخدم قوائم الميزات لتقييد الوكيل", link: "/ar/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "منع الوكلاء من إعلان النجاح مبكرًا", link: "/ar/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "الاختبار end-to-end هو التحقق الحقيقي", link: "/ar/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "اجعل runtime الوكيل قابلًا للملاحظة", link: "/ar/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "اترك handoff نظيفًا في نهاية كل جلسة", link: "/ar/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" },
];

const arProjectItems = [
  { text: "مرحبًا", link: "/ar/projects/" },
  { text: "Prompt فقط مقابل القواعد أولًا", link: "/ar/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "اجعل المشروع قابلًا للقراءة واستأنف", link: "/ar/projects/project-02-agent-readable-workspace/" },
  { text: "أبقِ الوكيل يعمل بعد إعادة تشغيل الجلسات", link: "/ar/projects/project-03-multi-session-continuity/" },
  { text: "استخدم feedback في runtime لتصحيح سلوك الوكيل", link: "/ar/projects/project-04-incremental-indexing/" },
  { text: "اجعل الوكيل يتحقق من عمله", link: "/ar/projects/project-05-grounded-qa-verification/" },
  { text: "ابنِ harness كاملًا للوكيل (Capstone)", link: "/ar/projects/project-06-runtime-observability-and-debugging/" },
];

const arResourceItems = [
  { text: "نظرة عامة", link: "/ar/resources/" },
  { text: "قوالب", link: "/ar/resources/templates/" },
  { text: "مرجع", link: "/ar/resources/reference/" },
  { text: "حزمة متقدمة", link: "/ar/resources/openai-advanced/" },
];

const arSkillItems = [
  { text: "نظرة عامة على المهارات", link: "/ar/skills/" },
];

const trLectureItems = [
  { text: "Hoş geldiniz", link: "/tr/" },
  { text: "Güçlü Ajanlar Neden Hâlâ Başarısız Olur", link: "/tr/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "Harness Aslında Nedir", link: "/tr/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "Depo Neden Kayıt Sistemi Olmalı", link: "/tr/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "Tek Bir Dev Talimat Dosyası Neden Yetmez", link: "/tr/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "Uzun Süren Görevler Neden Sürekliliği Kaybeder", link: "/tr/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "Başlatma Neden Kendine Ait Bir Aşama Olmalı", link: "/tr/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "Ajanlar Neden Sınırı Aşar ve Bitirmez", link: "/tr/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "Özellik Listeleri Neden Harness’ın Temel Yapı Taşı", link: "/tr/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "Ajanlar Neden Zaferi Çok Erken İlan Eder", link: "/tr/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "Uçtan Uca Test Sonuçları Neden Değiştirir", link: "/tr/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "Gözlemlenebilirlik Neden Harness’ın İçinde Olmalı", link: "/tr/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "Her Oturum Neden Temiz Bir Durumla Bitmeli", link: "/tr/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" },
];

const trProjectItems = [
  { text: "Hoş geldiniz", link: "/tr/projects/" },
  { text: "Yalnızca Prompt vs. Önce Kurallar", link: "/tr/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "Ajanın Okuyabildiği Çalışma Alanı", link: "/tr/projects/project-02-agent-readable-workspace/" },
  { text: "Çok Oturumlu Süreklilik", link: "/tr/projects/project-03-multi-session-continuity/" },
  { text: "Çalışma Zamanı Geri Bildirimi ve Kapsam Kontrolü", link: "/tr/projects/project-04-incremental-indexing/" },
  { text: "Öz-Doğrulama ve Rol Ayrımı", link: "/tr/projects/project-05-grounded-qa-verification/" },
  { text: "Eksiksiz Harness (Bitirme Projesi)", link: "/tr/projects/project-06-runtime-observability-and-debugging/" },
];

const trResourceItems = [
  { text: "Genel Bakış", link: "/tr/resources/" },
  { text: "Şablonlar", link: "/tr/resources/templates/" },
  { text: "Referans", link: "/tr/resources/reference/" },
  { text: "Gelişmiş Paket", link: "/tr/resources/openai-advanced/" },
];

const trSkillItems = [
  { text: "Yetenekler Genel Bakış", link: "/tr/skills/" },
];

const zhTWLectureItems = [
  { text: "歡迎", link: "/zh-TW/" },
  { text: "模型能力強，不等於執行可靠", link: "/zh-TW/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "Harness 到底是什麼", link: "/zh-TW/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "讓程式碼儲存庫成為唯一的事實來源", link: "/zh-TW/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "把指令拆分到不同檔案裡", link: "/zh-TW/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "讓跨工作階段的任務保持脈絡連續", link: "/zh-TW/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "讓 agent 每次工作前先初始化", link: "/zh-TW/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "給 agent 劃清每次任務的邊界", link: "/zh-TW/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "用功能清單約束 agent 該做什麼", link: "/zh-TW/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "防止 agent 提前宣告完成", link: "/zh-TW/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "跑通完整流程才算真正驗證", link: "/zh-TW/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "讓 agent 的運行過程可觀測", link: "/zh-TW/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "每次會話結束前都做好交接", link: "/zh-TW/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" },
];

const zhTWProjectItems = [
  { text: "歡迎", link: "/zh-TW/projects/" },
  { text: "提示詞驅動 vs 規則驅動", link: "/zh-TW/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "讓 agent 看懂項目、接住上次的工作", link: "/zh-TW/projects/project-02-agent-readable-workspace/" },
  { text: "讓 agent 關掉再打開還能接著幹", link: "/zh-TW/projects/project-03-multi-session-continuity/" },
  { text: "用運行反饋修正 agent 的行為", link: "/zh-TW/projects/project-04-incremental-indexing/" },
  { text: "讓 agent 自己檢查自己做的對不對", link: "/zh-TW/projects/project-05-grounded-qa-verification/" },
  { text: "搭建一套完整的 agent 工作環境", link: "/zh-TW/projects/project-06-runtime-observability-and-debugging/" },
];

const zhTWResourceItems = [
  { text: "資料庫總覽", link: "/zh-TW/resources/" },
  { text: "繁體中文範本", link: "/zh-TW/resources/templates/" },
  { text: "繁體中文參考", link: "/zh-TW/resources/reference/" },
  { text: "進階資源包", link: "/zh-TW/resources/openai-advanced/" },
];

const zhTWSkillItems = [
  { text: "技能總覽", link: "/zh-TW/skills/" },
];

const ptBRLectureItems = [
  { text: "Bem-vindo", link: "/pt-BR/" },
  { text: "Por que agentes capazes ainda falham", link: "/pt-BR/lectures/lecture-01-why-capable-agents-still-fail/" },
  { text: "O que realmente é um Harness", link: "/pt-BR/lectures/lecture-02-what-a-harness-actually-is/" },
  { text: "Por que o repositório precisa se tornar a fonte da verdade", link: "/pt-BR/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/" },
  { text: "Por que um único arquivo gigante de instruções falha", link: "/pt-BR/lectures/lecture-04-why-one-giant-instruction-file-fails/" },
  { text: "Por que tarefas de longa duração perdem continuidade", link: "/pt-BR/lectures/lecture-05-why-long-running-tasks-lose-continuity/" },
  { text: "Por que a inicialização precisa de sua própria etapa", link: "/pt-BR/lectures/lecture-06-why-initialization-needs-its-own-phase/" },
  { text: "Por que agentes extrapolam e entregam pela metade", link: "/pt-BR/lectures/lecture-07-why-agents-overreach-and-under-finish/" },
  { text: "Por que listas de funcionalidades são primitivas de Harness", link: "/pt-BR/lectures/lecture-08-why-feature-lists-are-harness-primitives/" },
  { text: "Por que agentes declaram vitória cedo demais", link: "/pt-BR/lectures/lecture-09-why-agents-declare-victory-too-early/" },
  { text: "Por que testes end-to-end mudam os resultados", link: "/pt-BR/lectures/lecture-10-why-end-to-end-testing-changes-results/" },
  { text: "Por que observabilidade pertence ao Harness", link: "/pt-BR/lectures/lecture-11-why-observability-belongs-inside-the-harness/" },
  { text: "Por que toda sessão deve deixar um estado limpo", link: "/pt-BR/lectures/lecture-12-why-every-session-must-leave-a-clean-state/" },
];

const ptBRProjectItems = [
  { text: "Bem-vindo", link: "/pt-BR/projects/" },
  { text: "Apenas Prompt vs. Regras Primeiro", link: "/pt-BR/projects/project-01-baseline-vs-minimal-harness/" },
  { text: "Workspace Legível por Agentes", link: "/pt-BR/projects/project-02-agent-readable-workspace/" },
  { text: "Continuidade entre Múltiplas Sessões", link: "/pt-BR/projects/project-03-multi-session-continuity/" },
  { text: "Feedback em Runtime e Controle de Escopo", link: "/pt-BR/projects/project-04-incremental-indexing/" },
  { text: "Autoverificação e Separação de Papéis", link: "/pt-BR/projects/project-05-grounded-qa-verification/" },
  { text: "Harness Completo (Projeto Final)", link: "/pt-BR/projects/project-06-runtime-observability-and-debugging/" },
];

const ptBRResourceItems = [
  { text: "Visão Geral", link: "/pt-BR/resources/" },
  { text: "Templates em Português", link: "/pt-BR/resources/templates/" },
  { text: "Referência em Português", link: "/pt-BR/resources/reference/" },
  { text: "Pacote Avançado", link: "/pt-BR/resources/openai-advanced/" },
];

const ptBRSkillItems = [
  { text: "Visão Geral das Skills", link: "/pt-BR/skills/" },
];

const jaSourceItems = { lectures: jaLectureItems, projects: jaProjectItems, resources: jaResourceItems, skills: jaSkillItems };
const esSourceItems = { lectures: esLectureItems, projects: esProjectItems, resources: esResourceItems, skills: esSkillItems };
const frSourceItems = { lectures: frLectureItems, projects: frProjectItems, resources: frResourceItems, skills: frSkillItems };
const deSourceItems = { lectures: deLectureItems, projects: deProjectItems, resources: deResourceItems, skills: deSkillItems };
const arSourceItems = { lectures: arLectureItems, projects: arProjectItems, resources: arResourceItems, skills: arSkillItems };
const zhTWSourceItems = { lectures: zhTWLectureItems, projects: zhTWProjectItems, resources: zhTWResourceItems, skills: zhTWSkillItems };
const trSourceItems = { lectures: trLectureItems, projects: trProjectItems, resources: trResourceItems, skills: trSkillItems };

const relinkItems = (items: Array<{ text: string; link: string }>, locale: string) =>
  items.map((item) => ({
    ...item,
    link: item.link.replace(
      /^\/(en|zh|vi|ko|uz|ru|ja|es|fr|de|ar|zh-TW|tr|pt-BR)\//,
      `/${locale}/`,
    ),
  }));

const createLocaleTheme = (
  locale: string,
  sourceItems: {
    lectures: Array<{ text: string; link: string }>;
    projects: Array<{ text: string; link: string }>;
    resources: Array<{ text: string; link: string }>;
    skills: Array<{ text: string; link: string }>;
  },
  labels: {
    lectures: string;
    projects: string;
    resources: string;
    skills: string;
    resourceLibrary: string;
    tryHarness: string;
    outline?: string;
    prev?: string;
    next?: string;
    lastUpdated?: string;
    returnToTop?: string;
    sidebarMenu?: string;
    darkModeSwitch?: string;
    lightModeSwitchTitle?: string;
    darkModeSwitchTitle?: string;
  },
) => {
  const lectures = relinkItems(sourceItems.lectures, locale);
  const projects = relinkItems(sourceItems.projects, locale);
  const resources = relinkItems(sourceItems.resources, locale);
  const skills = relinkItems(sourceItems.skills, locale);

  return {
    nav: [
      { text: labels.lectures, link: lectures[1].link, activeMatch: `^/${locale}/(lectures/.*)?$` },
      { text: labels.projects, link: projects[0].link, activeMatch: `^/${locale}/projects/` },
      { text: labels.resources, link: `/${locale}/resources/`, activeMatch: `^/${locale}/resources/` },
      { text: labels.skills, link: `/${locale}/skills/`, activeMatch: `^/${locale}/skills/` },
      { text: labels.tryHarness, link: `https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/${locale}/resources/templates/index.md`, target: "_blank", rel: "noopener noreferrer" },
    ],
    sidebar: {
      [`/${locale}/projects/`]: [{ text: labels.projects, items: projects }],
      [`/${locale}/resources/`]: [{ text: labels.resourceLibrary, items: resources }],
      [`/${locale}/skills/`]: [{ text: labels.skills, items: skills }],
      [`/${locale}/`]: [{ text: labels.lectures, items: lectures }]
    },
    outline: {
      level: [2, 3],
      ...(labels.outline ? { label: labels.outline } : {})
    },
    docFooter: {
      prev: labels.prev || "Previous",
      next: labels.next || "Next"
    },
    lastUpdated: {
      text: labels.lastUpdated || "Last updated"
    },
    returnToTopLabel: labels.returnToTop || "Return to top",
    sidebarMenuLabel: labels.sidebarMenu || "Menu",
    darkModeSwitchLabel: labels.darkModeSwitch || "Theme",
    lightModeSwitchTitle: labels.lightModeSwitchTitle || "Switch to light theme",
    darkModeSwitchTitle: labels.darkModeSwitchTitle || "Switch to dark theme",
    socialLinks: [{ icon: "github", link: githubRepoTreeLink }]
  };
};

const enSourceItems = {
  lectures: enLectureItems,
  projects: enProjectItems,
  resources: enResourceItems,
  skills: enSkillItems
};

const zhSourceItems = {
  lectures: zhLectureItems,
  projects: zhProjectItems,
  resources: zhResourceItems,
  skills: zhSkillItems
};

export default withMermaid(
  defineConfig({
    base: docsBase,
    title: "Learn Harness Engineering",
    description:
      "A project-based course on designing the environments, state, verification, and control systems that make Codex and Claude Code reliable.",
    cleanUrls: true,
    srcExclude: ["temp/**"],
    ignoreDeadLinks: true,
    head: [['link', { rel: 'icon', type: 'image/svg+xml', href: brandLogo }]],
    themeConfig: {
      logo: brandLogo,
      search: {
        provider: "local"
      },
      socialLinks: [{ icon: "github", link: githubRepoTreeLink }]
    },
    markdown: {
      theme: {
        light: 'github-light',
        dark: 'github-dark'
      },
    },
    mermaid: {
      theme: "base",
      themeVariables: {
        primaryColor: '#F4F3EE',
        primaryBorderColor: '#D1D1D1',
        primaryTextColor: '#1A1A1A',
        lineColor: '#B3B3B3',
        fontFamily: 'Inter, sans-serif',
        fontSize: '18px'
      },
      flowchart: {
        nodeSpacing: 40,
        rankSpacing: 56,
        padding: 12
      },
    },
    locales: {
      en: {
        label: "English",
        lang: "en",
        link: "/en/",
        themeConfig: {
          nav: [
            { text: "Lectures", link: enLectureItems[1].link, activeMatch: '^/en/(lectures/.*)?$' },
            { text: "Projects", link: enProjectItems[0].link, activeMatch: '^/en/projects/' },
            { text: "Library", link: "/en/resources/", activeMatch: '^/en/resources/' },
            { text: "Skills", link: "/en/skills/", activeMatch: '^/en/skills/' },
            { text: "Try Harness ↗", link: "https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/index.md", target: "_blank", rel: "noopener noreferrer" }
          ],
          sidebar: {
            '/en/projects/': [{ text: "Projects", items: enProjectItems }],
            '/en/resources/': [{ text: "Resource Library", items: enResourceItems }],
            '/en/skills/': [{ text: "Skills", items: enSkillItems }],
            '/en/': [{ text: "Lectures", items: enLectureItems }]
          },
          socialLinks: [{ icon: "github", link: githubRepoTreeLink }]
        },
      },
      zh: {
        label: "简体中文",
        lang: "zh-CN",
        link: "/zh/",
        themeConfig: {
          nav: [
            {
              text: "讲义",
              link: zhLectureItems[1].link,
              activeMatch: "^/zh/(lectures/.*)?$",
            },
            {
              text: "项目",
              link: zhProjectItems[0].link,
              activeMatch: "^/zh/projects/",
            },
            {
              text: "资料库",
              link: "/zh/resources/",
              activeMatch: "^/zh/resources/",
            },
            { text: "技能", link: "/zh/skills/", activeMatch: "^/zh/skills/" },
            {
              text: "Try Harness ↗",
              link: "https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/zh/resources/templates/index.md",
              target: "_blank",
              rel: "noopener noreferrer",
            },
          ],
          sidebar: {
            "/zh/projects/": [{ text: "项目", items: zhProjectItems }],
            "/zh/resources/": [{ text: "资料库", items: zhResourceItems }],
            "/zh/skills/": [{ text: "技能", items: zhSkillItems }],
            "/zh/": [{ text: "讲义", items: zhLectureItems }],
          },
          outline: {
            level: [2, 3],
          },
          docFooter: {
            prev: "上一篇",
            next: "下一篇",
          },
          lastUpdated: {
            text: "最后更新于",
          },
          returnToTopLabel: "回到顶部",
          sidebarMenuLabel: "菜单",
          darkModeSwitchLabel: "主题",
          lightModeSwitchTitle: "切换到浅色模式",
          darkModeSwitchTitle: "切换到深色模式",
          socialLinks: [{ icon: "github", link: githubRepoTreeLink }],
        },
      },
      "zh-TW": {
        label: "繁體中文",
        lang: "zh-TW",
        link: "/zh-TW/",
        themeConfig: createLocaleTheme("zh-TW", zhTWSourceItems, {
          lectures: "講義",
          projects: "專案",
          resources: "資源庫",
          skills: "技能",
          resourceLibrary: "資源庫",
          tryHarness: "Try Harness ↗",
          prev: "上一篇",
          next: "下一篇",
          lastUpdated: "最後更新於",
          returnToTop: "回到頂部",
          sidebarMenu: "選單",
          darkModeSwitch: "主題",
          lightModeSwitchTitle: "切換到淺色模式",
          darkModeSwitchTitle: "切換到深色模式",
        }),
      },
      ja: {
        label: "日本語",
        lang: "ja-JP",
        link: "/ja/",
        themeConfig: createLocaleTheme("ja", jaSourceItems, {
          lectures: "講義",
          projects: "プロジェクト",
          resources: "リソース",
          skills: "スキル",
          resourceLibrary: "リソースライブラリ",
          tryHarness: "Try Harness ↗",
          outline: "このページ",
          prev: "前へ",
          next: "次へ",
          lastUpdated: "最終更新",
          returnToTop: "トップへ戻る",
          sidebarMenu: "メニュー",
          darkModeSwitch: "テーマ",
          lightModeSwitchTitle: "ライトモードに切り替え",
          darkModeSwitchTitle: "ダークモードに切り替え",
        }),
      },
      es: {
        label: "Español",
        lang: "es-ES",
        link: "/es/",
        themeConfig: createLocaleTheme("es", esSourceItems, {
          lectures: "Lecciones",
          projects: "Proyectos",
          resources: "Biblioteca",
          skills: "Skills",
          resourceLibrary: "Biblioteca de recursos",
          tryHarness: "Try Harness ↗",
          outline: "En esta página",
          prev: "Anterior",
          next: "Siguiente",
          lastUpdated: "Última actualización",
          returnToTop: "Volver arriba",
          sidebarMenu: "Menú",
          darkModeSwitch: "Tema",
          lightModeSwitchTitle: "Cambiar a tema claro",
          darkModeSwitchTitle: "Cambiar a tema oscuro",
        }),
      },
      fr: {
        label: "Français",
        lang: "fr-FR",
        link: "/fr/",
        themeConfig: createLocaleTheme("fr", frSourceItems, {
          lectures: "Cours",
          projects: "Projets",
          resources: "Bibliothèque",
          skills: "Skills",
          resourceLibrary: "Bibliothèque de ressources",
          tryHarness: "Try Harness ↗",
          outline: "Sur cette page",
          prev: "Précédent",
          next: "Suivant",
          lastUpdated: "Dernière mise à jour",
          returnToTop: "Retour en haut",
          sidebarMenu: "Menu",
          darkModeSwitch: "Thème",
          lightModeSwitchTitle: "Passer au thème clair",
          darkModeSwitchTitle: "Passer au thème sombre",
        }),
      },
      de: {
        label: "Deutsch",
        lang: "de-DE",
        link: "/de/",
        themeConfig: createLocaleTheme("de", deSourceItems, {
          lectures: "Lektionen",
          projects: "Projekte",
          resources: "Bibliothek",
          skills: "Skills",
          resourceLibrary: "Ressourcenbibliothek",
          tryHarness: "Try Harness ↗",
          outline: "Auf dieser Seite",
          prev: "Zurück",
          next: "Weiter",
          lastUpdated: "Zuletzt aktualisiert",
          returnToTop: "Nach oben",
          sidebarMenu: "Menü",
          darkModeSwitch: "Theme",
          lightModeSwitchTitle: "Zum hellen Theme wechseln",
          darkModeSwitchTitle: "Zum dunklen Theme wechseln",
        }),
      },
      tr: {
        label: "Türkçe",
        lang: "tr-TR",
        link: "/tr/",
        themeConfig: createLocaleTheme("tr", trSourceItems, {
          lectures: "Dersler",
          projects: "Projeler",
          resources: "Kütüphane",
          skills: "Yetenekler",
          resourceLibrary: "Kaynak Kütüphanesi",
          tryHarness: "Harness'ı Dene ↗",
          outline: "Bu sayfada",
          prev: "Önceki",
          next: "Sonraki",
          lastUpdated: "Son güncelleme",
          returnToTop: "Başa dön",
          sidebarMenu: "Menü",
          darkModeSwitch: "Tema",
          lightModeSwitchTitle: "Açık temaya geç",
          darkModeSwitchTitle: "Koyu temaya geç",
        }),
      },
      ar: {
        label: "العربية",
        lang: "ar-SA",
        link: "/ar/",
        themeConfig: createLocaleTheme("ar", arSourceItems, {
          lectures: "المحاضرات",
          projects: "المشاريع",
          resources: "المكتبة",
          skills: "المهارات",
          resourceLibrary: "مكتبة الموارد",
          tryHarness: "Try Harness ↗",
          outline: "في هذه الصفحة",
          prev: "السابق",
          next: "التالي",
          lastUpdated: "آخر تحديث",
          returnToTop: "العودة إلى الأعلى",
          sidebarMenu: "القائمة",
          darkModeSwitch: "السمة",
          lightModeSwitchTitle: "التبديل إلى السمة الفاتحة",
          darkModeSwitchTitle: "التبديل إلى السمة الداكنة",
        }),
      },
      vi: {
        label: "Tiếng Việt",
        lang: "vi-VN",
        link: "/vi/",
        themeConfig: {
          nav: [
            {
              text: "Bài giảng",
              link: viLectureItems[1].link,
              activeMatch: "^/vi/(lectures/.*)?$",
            },
            {
              text: "Dự án",
              link: viProjectItems[0].link,
              activeMatch: "^/vi/projects/",
            },
            {
              text: "Tài nguyên",
              link: "/vi/resources/",
              activeMatch: "^/vi/resources/",
            },
            {
              text: "Kỹ năng",
              link: "/vi/skills/",
              activeMatch: "^/vi/skills/",
            },
            {
              text: "Try Harness ↗",
              link: "https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/resources/templates/index.md",
              target: "_blank",
              rel: "noopener noreferrer",
            },
          ],
          sidebar: {
            "/vi/projects/": [{ text: "Dự án", items: viProjectItems }],
            "/vi/resources/": [
              { text: "Thư viện Tài nguyên", items: viResourceItems },
            ],
            "/vi/skills/": [{ text: "Kỹ năng", items: viSkillItems }],
            "/vi/": [{ text: "Bài giảng", items: viLectureItems }],
          },
          outline: {
            level: [2, 3],
          },
          docFooter: {
            prev: "Trang trước",
            next: "Trang sau",
          },
          lastUpdated: {
            text: "Cập nhật lần cuối",
          },
          returnToTopLabel: "Trở lên trên cùng",
          sidebarMenuLabel: "Menu",
          darkModeSwitchLabel: "Giao diện",
          lightModeSwitchTitle: "Chuyển sang chế độ sáng",
          darkModeSwitchTitle: "Chuyển sang chế độ tối",
          socialLinks: [{ icon: "github", link: githubRepoTreeLink }],
        },
      },
      ko: {
        label: "한국어",
        lang: "ko",
        link: "/ko/",
        themeConfig: {
          nav: [
            {
              text: "강의",
              link: koLectureItems[1].link,
              activeMatch: "^/ko/(lectures/.*)?$",
            },
            {
              text: "프로젝트",
              link: koProjectItems[0].link,
              activeMatch: "^/ko/projects/",
            },
            {
              text: "리소스 모음",
              link: "/ko/resources/",
              activeMatch: "^/ko/resources/",
            },
            { text: "스킬", link: "/ko/skills/", activeMatch: "^/ko/skills/" },
            {
              text: "Try Harness ↗",
              link: "https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ko/resources/templates/index.md",
              target: "_blank",
              rel: "noopener noreferrer",
            },
          ],
          sidebar: {
            "/ko/projects/": [{ text: "프로젝트", items: koProjectItems }],
            "/ko/resources/": [{ text: "리소스 모음", items: koResourceItems }],
            "/ko/skills/": [{ text: "스킬", items: koSkillItems }],
            "/ko/": [{ text: "강의", items: koLectureItems }],
          },
          outline: {
            level: [2, 3],
            label: "이 페이지에서",
          },
          docFooter: {
            prev: "이전",
            next: "다음",
          },
          lastUpdated: {
            text: "마지막 업데이트",
          },
          returnToTopLabel: "맨 위로",
          sidebarMenuLabel: "메뉴",
          darkModeSwitchLabel: "테마",
          lightModeSwitchTitle: "라이트 모드로 전환",
          darkModeSwitchTitle: "다크 모드로 전환",
          socialLinks: [{ icon: "github", link: githubRepoTreeLink }],
        },
      },
      uz: {
        label: "Oʻzbek",
        lang: "uz",
        link: "/uz/",
        themeConfig: {
          nav: [
            {
              text: "Maʼruzalar",
              link: uzLectureItems[1].link,
              activeMatch: "^/uz/(lectures/.*)?$",
            },
            {
              text: "Loyihalar",
              link: uzProjectItems[0].link,
              activeMatch: "^/uz/projects/",
            },
            {
              text: "Kutubxona",
              link: "/uz/resources/",
              activeMatch: "^/uz/resources/",
            },
            {
              text: "Malakalar",
              link: "/uz/skills/",
              activeMatch: "^/uz/skills/",
            },
            {
              text: "Harness'ni sinash ↗",
              link: "https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/uz/resources/templates/index.md",
              target: "_blank",
              rel: "noopener noreferrer",
            },
          ],
          sidebar: {
            "/uz/projects/": [{ text: "Loyihalar", items: uzProjectItems }],
            "/uz/resources/": [
              { text: "Resurslar kutubxonasi", items: uzResourceItems },
            ],
            "/uz/skills/": [{ text: "Malakalar", items: uzSkillItems }],
            "/uz/": [{ text: "Maʼruzalar", items: uzLectureItems }],
          },
          outline: {
            level: [2, 3],
            label: "Ushbu sahifada",
          },
          docFooter: {
            prev: "Oldingi",
            next: "Keyingi",
          },
          lastUpdated: {
            text: "Oxirgi yangilanish",
          },
          returnToTopLabel: "Yuqoriga qaytish",
          sidebarMenuLabel: "Menyu",
          darkModeSwitchLabel: "Mavzu",
          lightModeSwitchTitle: "Yorugʻ rejimga oʻtish",
          darkModeSwitchTitle: "Qorongʻi rejimga oʻtish",
          socialLinks: [{ icon: "github", link: githubRepoTreeLink }],
        },
      },
      ru: {
        label: "Русский",
        lang: "ru",
        link: "/ru/",
        themeConfig: {
          nav: [
            {
              text: "Лекции",
              link: ruLectureItems[1].link,
              activeMatch: "^/ru/(lectures/.*)?$",
            },
            {
              text: "Проекты",
              link: ruProjectItems[0].link,
              activeMatch: "^/ru/projects/",
            },
            {
              text: "Материалы",
              link: "/ru/resources/",
              activeMatch: "^/ru/resources/",
            },
            {
              text: "Скиллы",
              link: "/ru/skills/",
              activeMatch: "^/ru/skills/",
            },
            {
              text: "Try Harness ↗",
              link: "https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ru/resources/templates/index.md",
              target: "_blank",
              rel: "noopener noreferrer",
            },
          ],
          sidebar: {
            "/ru/projects/": [{ text: "Проекты", items: ruProjectItems }],
            "/ru/resources/": [{ text: "Материалы", items: ruResourceItems }],
            "/ru/skills/": [{ text: "Скиллы", items: ruSkillItems }],
            "/ru/": [{ text: "Лекции", items: ruLectureItems }],
          },
          outline: {
            level: [2, 3],
            label: "На этой странице",
          },
          docFooter: {
            prev: "Предыдущая",
            next: "Следующая",
          },
          lastUpdated: {
            text: "Последнее обновление",
          },
          returnToTopLabel: "Наверх",
          sidebarMenuLabel: "Меню",
          darkModeSwitchLabel: "Тема",
          lightModeSwitchTitle: "Включить светлую тему",
          darkModeSwitchTitle: "Включить тёмную тему",
          socialLinks: [{ icon: "github", link: githubRepoTreeLink }],
        },
      },
      "pt-BR": {
        label: "Português (Brasil)",
        lang: "pt-BR",
        link: "/pt-BR/",
        themeConfig: {
          nav: [
            {
              text: "Aulas",
              link: ptBRLectureItems[1].link,
              activeMatch: "^/pt-BR/(lectures/.*)?$",
            },
            {
              text: "Projetos",
              link: ptBRProjectItems[0].link,
              activeMatch: "^/pt-BR/projects/",
            },
            {
              text: "Recursos",
              link: "/pt-BR/resources/",
              activeMatch: "^/pt-BR/resources/",
            },
            {
              text: "Skills",
              link: "/pt-BR/skills/",
              activeMatch: "^/pt-BR/skills/",
            },
            {
              text: "Experimente Harness ↗",
              link: "https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/pt-BR/resources/templates/index.md",
              target: "_blank",
              rel: "noopener noreferrer",
            },
          ],
          sidebar: {
            "/pt-BR/projects/": [{ text: "Projetos", items: ptBRProjectItems }],
            "/pt-BR/resources/": [
              { text: "Biblioteca de recursos", items: ptBRResourceItems },
            ],
            "/pt-BR/skills/": [{ text: "Skills", items: ptBRSkillItems }],
            "/pt-BR/": [{ text: "Aulas", items: ptBRLectureItems }],
          },
          outline: {
            level: [2, 3],
            label: "Nesta página",
          },
          docFooter: {
            prev: "Página anterior",
            next: "Próxima página",
          },
          lastUpdated: {
            text: "Última atualização",
          },
          returnToTopLabel: "Retornar ao topo",
          sidebarMenuLabel: "Menu",
          darkModeSwitchLabel: "Tema",
          lightModeSwitchTitle: "Ativar tema claro",
          darkModeSwitchTitle: "Ativar tema escuro",
          socialLinks: [{ icon: "github", link: githubRepoTreeLink }],
        },
      },
    },
  }),
);
