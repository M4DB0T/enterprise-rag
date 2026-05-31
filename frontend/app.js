const askForm = document.querySelector("#askForm");
const uploadForm = document.querySelector("#uploadForm");
const feedbackForm = document.querySelector("#feedbackForm");
const refreshDocumentsButton = document.querySelector("#refreshDocuments");
const refreshLogsButton = document.querySelector("#refreshLogs");

const askStatus = document.querySelector("#askStatus");
const uploadStatus = document.querySelector("#uploadStatus");
const feedbackStatus = document.querySelector("#feedbackStatus");
const answerText = document.querySelector("#answerText");
const sourcesList = document.querySelector("#sourcesList");
const documentsList = document.querySelector("#documentsList");
const logsList = document.querySelector("#logsList");
const uploadMessage = document.querySelector("#uploadMessage");

let lastQuestion = "";
let lastAnswer = "";

function setStatus(element, text) {
  element.textContent = text;
}

function renderEmpty(element, text) {
  element.className = "list empty";
  element.textContent = text;
}

function createItem(title, meta, tags = []) {
  const item = document.createElement("article");
  item.className = "item";

  const titleElement = document.createElement("p");
  titleElement.className = "item-title";
  titleElement.textContent = title;
  item.appendChild(titleElement);

  if (meta) {
    const metaElement = document.createElement("p");
    metaElement.className = "item-meta";
    metaElement.textContent = meta;
    item.appendChild(metaElement);
  }

  if (tags.length > 0) {
    const row = document.createElement("div");
    row.className = "score-row";

    tags.forEach((tag) => {
      const pill = document.createElement("span");
      pill.className = "pill";
      pill.textContent = tag;
      row.appendChild(pill);
    });

    item.appendChild(row);
  }

  return item;
}

function formatScore(value) {
  if (value === null || value === undefined) {
    return null;
  }

  return Number(value).toFixed(3);
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok || data.error) {
    throw new Error(data.error || data.detail || `Request failed: ${response.status}`);
  }

  return data;
}

function renderSources(sources) {
  sourcesList.innerHTML = "";
  sourcesList.className = "list";

  if (!sources || sources.length === 0) {
    renderEmpty(sourcesList, "No sources returned.");
    return;
  }

  sources.forEach((source, index) => {
    const tags = [
      source.retrieval_source ? `source: ${source.retrieval_source}` : null,
      source.chunk_index !== undefined && source.chunk_index !== null ? `chunk: ${source.chunk_index}` : null,
      formatScore(source.hybrid_score) ? `hybrid: ${formatScore(source.hybrid_score)}` : null,
      formatScore(source.reranker_score) ? `rerank: ${formatScore(source.reranker_score)}` : null,
      formatScore(source.vector_distance) ? `distance: ${formatScore(source.vector_distance)}` : null
    ].filter(Boolean);

    sourcesList.appendChild(
      createItem(
        source.filename || `Source ${index + 1}`,
        "Retrieved context used for the generated answer.",
        tags
      )
    );
  });
}

async function loadDocuments() {
  renderEmpty(documentsList, "Loading documents...");

  try {
    const data = await fetchJson("/documents");
    documentsList.innerHTML = "";
    documentsList.className = "list";

    if (!data.documents || data.documents.length === 0) {
      renderEmpty(documentsList, "No documents indexed yet.");
      return;
    }

    data.documents.forEach((document) => {
      documentsList.appendChild(
        createItem(
          document.filename || document.document_id,
          `Document ID: ${document.document_id}`,
          [`chunks: ${document.chunk_count}`]
        )
      );
    });
  } catch (error) {
    renderEmpty(documentsList, "Could not load documents.");
    documentsList.classList.add("error");
  }
}

async function loadLogs() {
  renderEmpty(logsList, "Loading logs...");

  try {
    const data = await fetchJson("/logs");
    logsList.innerHTML = "";
    logsList.className = "list";

    if (!data.logs || data.logs.length === 0) {
      renderEmpty(logsList, "No recent requests logged yet.");
      return;
    }

    data.logs.forEach((log) => {
      logsList.appendChild(
        createItem(
          log.question,
          log.answer,
          [
            log.retrieval_method,
            log.model_name,
            log.latency_seconds !== null && log.latency_seconds !== undefined
              ? `${Number(log.latency_seconds).toFixed(2)}s`
              : null,
            log.created_at
          ].filter(Boolean)
        )
      );
    });
  } catch (error) {
    renderEmpty(logsList, "Could not load logs.");
    logsList.classList.add("error");
  }
}

askForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = new FormData(askForm).get("question").trim();

  if (!question) {
    return;
  }

  setStatus(askStatus, "Thinking");
  answerText.textContent = "Retrieving context and generating an answer...";
  answerText.classList.add("muted");
  renderEmpty(sourcesList, "Waiting for sources...");

  try {
    const data = await fetchJson("/ask-hybrid", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question })
    });

    lastQuestion = question;
    lastAnswer = data.answer || "";
    answerText.textContent = lastAnswer || "No answer returned.";
    answerText.classList.remove("muted");
    renderSources(data.sources);
    setStatus(askStatus, "Answered");
    await loadLogs();
  } catch (error) {
    answerText.textContent = error.message;
    answerText.classList.add("error");
    setStatus(askStatus, "Error");
  }
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const fileInput = document.querySelector("#pdfInput");

  if (!fileInput.files.length) {
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  setStatus(uploadStatus, "Uploading");
  uploadMessage.textContent = "Uploading and indexing PDF...";
  uploadMessage.className = "message muted";

  try {
    const data = await fetchJson("/upload", {
      method: "POST",
      body: formData
    });

    setStatus(uploadStatus, "Complete");
    uploadMessage.textContent = data.message || "Upload complete.";
    uploadForm.reset();
    await loadDocuments();
  } catch (error) {
    setStatus(uploadStatus, "Error");
    uploadMessage.textContent = error.message;
    uploadMessage.className = "message error";
  }
});

feedbackForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!lastQuestion || !lastAnswer) {
    setStatus(feedbackStatus, "Ask first");
    return;
  }

  const formData = new FormData(feedbackForm);
  setStatus(feedbackStatus, "Saving");

  try {
    await fetchJson("/feedback", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        question: lastQuestion,
        answer: lastAnswer,
        rating: formData.get("rating"),
        comment: formData.get("comment") || null
      })
    });

    setStatus(feedbackStatus, "Saved");
    feedbackForm.reset();
  } catch (error) {
    setStatus(feedbackStatus, "Error");
  }
});

refreshDocumentsButton.addEventListener("click", loadDocuments);
refreshLogsButton.addEventListener("click", loadLogs);

loadDocuments();
loadLogs();
