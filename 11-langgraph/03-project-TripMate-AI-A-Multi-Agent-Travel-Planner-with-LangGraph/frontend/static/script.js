let currentThreadId = localStorage.getItem("travel_thread_id") || null;
let latestAnswerMarkdown = "";

const DEFAULT_NODES = [
    { id: "flight_agent", label: "航班调研" },
    { id: "hotel_agent", label: "酒店调研" },
    { id: "itinerary_agent", label: "行程规划" },
    { id: "final_agent", label: "最终回复" },
];

function setPrompt(text) {
    document.getElementById("userInput").value = text;
}

function setLoading(isLoading) {
    const sendBtn = document.getElementById("sendBtn");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");

    sendBtn.disabled = isLoading;

    if (isLoading) {
        btnText.classList.add("hidden");
        btnLoader.classList.remove("hidden");
    } else {
        btnText.classList.remove("hidden");
        btnLoader.classList.add("hidden");
    }
}

function showError(message) {
    const errorBox = document.getElementById("errorBox");

    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}

function hideError() {
    const errorBox = document.getElementById("errorBox");

    errorBox.classList.add("hidden");
    errorBox.textContent = "";
}

function showResult(answer, threadId) {
    latestAnswerMarkdown = answer;

    const resultSection = document.getElementById("resultSection");
    const resultBox = document.getElementById("resultBox");
    const threadInfo = document.getElementById("threadInfo");

    if (typeof marked !== "undefined") {
        resultBox.innerHTML = marked.parse(answer);
    } else {
        resultBox.innerText = answer;
    }

    threadInfo.textContent = `Thread ID: ${threadId}`;

    resultSection.classList.remove("hidden");

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

function renderProgressNodes(nodes, activeNode = null, doneNodes = new Set()) {
    const container = document.getElementById("progressNodes");
    container.innerHTML = "";

    nodes.forEach((node) => {
        const chip = document.createElement("div");
        let state = "pending";

        if (doneNodes.has(node.id)) {
            state = "done";
        } else if (node.id === activeNode) {
            state = "running";
        }

        chip.className = `progress-node ${state}`;
        chip.dataset.node = node.id;
        chip.innerHTML = `<strong>${node.label}</strong><span>${node.id}</span>`;
        container.appendChild(chip);
    });
}

function showProgressPanel(nodes = DEFAULT_NODES) {
    const panel = document.getElementById("progressPanel");
    panel.classList.remove("hidden");
    document.getElementById("progressLabel").textContent = "准备启动多智能体流程…";
    document.getElementById("progressStep").textContent = `0 / ${nodes.length}`;
    document.getElementById("progressFill").style.width = "0%";
    renderProgressNodes(nodes);
}

function hideProgressPanel() {
    document.getElementById("progressPanel").classList.add("hidden");
}

function updateProgress(event, nodes, doneNodes) {
    const total = event.total || nodes.length || 4;
    const step = event.step || 0;
    const completed = event.status === "done" ? step : Math.max(0, step - 1);
    const fill = Math.max(0, Math.min(100, (completed / total) * 100));

    document.getElementById("progressFill").style.width = `${fill}%`;
    document.getElementById("progressStep").textContent = `${completed} / ${total}`;

    if (event.status === "running") {
        document.getElementById("progressLabel").textContent =
            `正在运行：${event.label}（${event.node}）`;
        renderProgressNodes(nodes, event.node, doneNodes);
    } else if (event.status === "done") {
        doneNodes.add(event.node);
        document.getElementById("progressLabel").textContent =
            `已完成：${event.label}（${event.node}）`;
        renderProgressNodes(nodes, null, doneNodes);
    }
}

async function consumeTravelStream(message) {
    const response = await fetch("/api/travel/stream", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: message,
            thread_id: currentThreadId
        })
    });

    if (!response.ok || !response.body) {
        let errorMessage = "Something went wrong.";
        try {
            const data = await response.json();
            errorMessage = data.error || errorMessage;
        } catch (_) {
            // ignore parse errors
        }
        throw new Error(errorMessage);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let nodes = DEFAULT_NODES.slice();
    const doneNodes = new Set();
    let finalResult = null;

    showProgressPanel(nodes);

    while (true) {
        const { done, value } = await reader.read();
        if (done) {
            break;
        }

        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() || "";

        for (const chunk of chunks) {
            const lines = chunk.split("\n");
            for (const line of lines) {
                if (!line.startsWith("data: ")) {
                    continue;
                }

                const event = JSON.parse(line.slice(6));

                if (event.type === "start") {
                    nodes = event.nodes || nodes;
                    showProgressPanel(nodes);
                } else if (event.type === "progress") {
                    updateProgress(event, nodes, doneNodes);
                } else if (event.type === "result") {
                    finalResult = event;
                    document.getElementById("progressLabel").textContent = "全部节点已完成";
                    document.getElementById("progressFill").style.width = "100%";
                    document.getElementById("progressStep").textContent =
                        `${nodes.length} / ${nodes.length}`;
                    nodes.forEach((node) => doneNodes.add(node.id));
                    renderProgressNodes(nodes, null, doneNodes);
                } else if (event.type === "error") {
                    throw new Error(event.error || "Stream failed.");
                }
            }
        }
    }

    if (!finalResult) {
        throw new Error("Stream ended without a result.");
    }

    return finalResult;
}

async function sendMessage() {
    hideError();

    const input = document.getElementById("userInput");
    const message = input.value.trim();

    if (!message) {
        showError("Please enter your travel request first.");
        return;
    }

    setLoading(true);

    try {
        const data = await consumeTravelStream(message);

        currentThreadId = data.thread_id;
        localStorage.setItem("travel_thread_id", currentThreadId);

        showResult(data.answer, data.thread_id);

        setTimeout(() => {
            hideProgressPanel();
        }, 1600);

    } catch (error) {
        hideProgressPanel();
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

function copyResult() {
    const resultBox = document.getElementById("resultBox");
    const text = resultBox.innerText;

    if (!text) {
        return;
    }

    navigator.clipboard.writeText(text)
        .then(() => {
            const copyBtn = document.querySelector(".copy-btn");
            const oldText = copyBtn.textContent;

            copyBtn.textContent = "Copied!";

            setTimeout(() => {
                copyBtn.textContent = oldText;
            }, 1400);
        })
        .catch(() => {
            showError("Could not copy result.");
        });
}

function downloadPDF() {
    const pdfContent = document.getElementById("pdfContent");

    if (!latestAnswerMarkdown || !pdfContent) {
        showError("No travel plan available to download.");
        return;
    }

    const downloadBtn = document.querySelector(".download-btn");
    const oldText = downloadBtn.textContent;

    downloadBtn.textContent = "Preparing PDF...";
    downloadBtn.disabled = true;

    const options = {
        margin: 0.5,
        filename: "ai-travel-plan.pdf",
        image: {
            type: "jpeg",
            quality: 0.98
        },
        html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: "#ffffff"
        },
        jsPDF: {
            unit: "in",
            format: "a4",
            orientation: "portrait"
        },
        pagebreak: {
            mode: ["avoid-all", "css", "legacy"]
        }
    };

    html2pdf()
        .set(options)
        .from(pdfContent)
        .save()
        .then(() => {
            downloadBtn.textContent = oldText;
            downloadBtn.disabled = false;
        })
        .catch(() => {
            downloadBtn.textContent = oldText;
            downloadBtn.disabled = false;
            showError("Could not download PDF.");
        });
}

document.addEventListener("keydown", function(event) {
    if (event.ctrlKey && event.key === "Enter") {
        sendMessage();
    }
});
