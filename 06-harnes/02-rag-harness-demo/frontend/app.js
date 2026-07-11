const questionEl = document.getElementById("question");
const askBtn = document.getElementById("ask-btn");
const statusEl = document.getElementById("status");
const answerEl = document.getElementById("answer");
const hitsEl = document.getElementById("hits");

async function askQuestion() {
  const question = questionEl.value.trim();
  if (!question) {
    statusEl.textContent = "请输入问题";
    return;
  }

  askBtn.disabled = true;
  statusEl.textContent = "检索中…";
  answerEl.textContent = "";
  hitsEl.innerHTML = "";

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k: 3 }),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    answerEl.textContent = data.answer || "（无回答）";
    hitsEl.innerHTML = (data.hits || [])
      .map(
        (hit) => `
          <li>
            <div class="hit-meta">来源: ${hit.doc_id} · 片段 #${hit.chunk_index} · score ${hit.score}</div>
            <div>${hit.text}</div>
          </li>
        `
      )
      .join("");
    statusEl.textContent = `命中 ${data.hits?.length || 0} 条`;
  } catch (err) {
    statusEl.textContent = "请求失败，请确认后端已启动";
    answerEl.textContent = String(err);
  } finally {
    askBtn.disabled = false;
  }
}

askBtn.addEventListener("click", askQuestion);
questionEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    askQuestion();
  }
});
