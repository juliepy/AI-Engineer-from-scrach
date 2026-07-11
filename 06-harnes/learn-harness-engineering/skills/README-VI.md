<p align="center">
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/English-d9d9d9"></a>
  <a href="README-CN.md"><img alt="简体中文" src="https://img.shields.io/badge/简体中文-d9d9d9"></a>
  <a href="README-ZH-TW.md"><img alt="繁體中文" src="https://img.shields.io/badge/繁體中文-d9d9d9"></a>
  <a href="README-JA.md"><img alt="日本語" src="https://img.shields.io/badge/日本語-d9d9d9"></a>
  <a href="README-ES.md"><img alt="Español" src="https://img.shields.io/badge/Español-d9d9d9"></a>
  <a href="README-FR.md"><img alt="Français" src="https://img.shields.io/badge/Français-d9d9d9"></a>
  <a href="README-KO.md"><img alt="한국어" src="https://img.shields.io/badge/한국어-d9d9d9"></a>
  <a href="README-AR.md"><img alt="العربية" src="https://img.shields.io/badge/العربية-d9d9d9"></a>
  <a href="README-VI.md"><img alt="Tiếng_Việt" src="https://img.shields.io/badge/Tiếng_Việt-d9d9d9"></a>
  <a href="README-DE.md"><img alt="Deutsch" src="https://img.shields.io/badge/Deutsch-d9d9d9"></a>
  <a href="README-TR.md"><img alt="Türkçe" src="https://img.shields.io/badge/Türkçe-d9d9d9"></a>
</p>

# Skills

Thu muc nay chua cac AI agent skills co the tai su dung cho du an Learn Harness Engineering. Moi skill la mot prompt template doc lap, co the duoc nap boi cac AI coding agent nhu Claude Code, Codex, Cursor va Windsurf.

## Skills hien co

### harness-creator

Skill harness engineering cap production cho AI coding agents. Skill nay giup tao, danh gia va cai thien cac file harness cua agent, gom AGENTS.md, danh sach tinh nang, verification workflows va co che tiep noi phien lam viec.

- **7 mau tham chieu**: Memory Persistence, Skill Runtime, Context Engineering, Tool Registry, Multi-Agent Coordination, Lifecycle & Bootstrap, Gotchas
- **Templates**: AGENTS.md/CLAUDE.md, feature-list.json, init.sh, progress.md, session-handoff.md
- **Scripts**: scaffold, validate, bao cao HTML, structural benchmark
- **10 eval test case tich hop**

Xem tai lieu day du tai [harness-creator/README.md](harness-creator/README.md).

## Cach harness-creator duoc tao

`harness-creator` duoc phat trien bang phuong phap **skill-creator**, meta-skill chinh thuc cua Anthropic de tao, kiem thu va lap lai viec cai thien agent skills theo luong draft → test → evaluate → iterate.

## Skills hoat dong nhu the nao

Moi skill co cau truc chuan:

1. **SKILL.md** — Diem vao, gom YAML frontmatter va huong dan Markdown cho agent.
2. **references/** — Tai lieu bo sung duoc nap vao context khi can.
3. **templates/** — Template khoi dau ma skill co the tao.

Skills dung progressive disclosure: agent ban dau chi thay ten va mo ta, sau do nap SKILL.md khi duoc kich hoat va chi doc tai nguyen kem theo khi can thiet.

## Bao mat

Tat ca file trong thu muc nay da duoc kiem tra bao mat:

- Khong co backdoor, URL an hoac payload duoc ma hoa
- Khong ro ri du lieu hoac credential hardcoded
- Khong co lo hong command injection
- Scripts chi dung module co san cua Node.js
- `init.sh` duoc tao se chay cac lenh verification phat hien tu project

## Giay phep

MIT
