(() => {
  const state = { logSeq: 0, generateSince: 0, vscodeUrl: "" };

  const markdownSelect = document.getElementById("markdownSelect");
  const reportsDiv = document.getElementById("reports");
  const toast = document.getElementById("toast");
  const logOutput = document.getElementById("logOutput");
  const statusPill = document.getElementById("fcsStatus");
  const modal = document.getElementById("generateModal");

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2600);
  }

  async function jsonFetch(url, options = {}) {
    const res = await fetch(url, options);
    const isJson = (res.headers.get("content-type") || "").includes("application/json");
    const payload = isJson ? await res.json() : {};
    if (!res.ok) {
      const msg = payload.error || payload.reason || `Request failed (${res.status})`;
      throw new Error(msg);
    }
    return payload;
  }

  async function refreshMarkdownFiles() {
    const data = await jsonFetch("/api/markdown-files");
    markdownSelect.innerHTML = "";
    for (const f of data.files) {
      const opt = document.createElement("option");
      opt.value = f.path;
      opt.textContent = f.name;
      markdownSelect.appendChild(opt);
    }
  }

  async function refreshReports() {
    const data = await jsonFetch("/api/reports");
    if (!data.files.length) {
      reportsDiv.innerHTML = "<p>No reports in test_reports/ yet.</p>";
      return;
    }

    const rows = data.files.map((f) => `
      <tr>
        <td>${f.name}</td>
        <td>${f.size}</td>
        <td>${new Date(f.mtime).toLocaleString()}</td>
        <td>
          <a class="button" href="/api/download?path=${encodeURIComponent(f.path)}">⬇ Download</a>
          <select data-tableid="${f.path}">
            <option value="OUTPUT" ${f.default_tableid === "OUTPUT" ? "selected" : ""}>OUTPUT</option>
            <option value="INPUT" ${f.default_tableid === "INPUT" ? "selected" : ""}>INPUT</option>
          </select>
          <button data-upload="${f.path}" type="button">☁ Upload to FC S</button>
          <button data-delete="${f.path}" type="button">🗑 Delete</button>
        </td>
      </tr>
    `).join("");

    reportsDiv.innerHTML = `<table><thead><tr><th>File</th><th>Size (bytes)</th><th>Modified (UTC)</th><th>Actions</th></tr></thead><tbody>${rows}</tbody></table>`;

    reportsDiv.querySelectorAll("button[data-upload]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const path = btn.getAttribute("data-upload");
        const tableSelect = reportsDiv.querySelector(`select[data-tableid="${CSS.escape(path)}"]`);
        const tableid = tableSelect ? tableSelect.value : "OUTPUT";
        try {
          await jsonFetch("/api/fcs-upload", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              path,
              tableid,
              project_name: document.getElementById("projectName").value,
              date_stamp: document.getElementById("dateStamp").value,
            }),
          });
          showToast("FC S upload completed");
        } catch (err) {
          showToast(err.message);
        }
      });
    });

    reportsDiv.querySelectorAll("button[data-delete]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const path = btn.getAttribute("data-delete");
        try {
          await jsonFetch("/api/delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ path }),
          });
          await refreshReports();
        } catch (err) {
          showToast(err.message);
        }
      });
    });
  }

  async function refreshFcsStatus() {
    try {
      const data = await jsonFetch("/api/fcs-check");
      statusPill.textContent = data.ok ? "FC S: reachable" : "FC S: unavailable";
      statusPill.className = `pill ${data.ok ? "ok" : "bad"}`;
    } catch {
      statusPill.textContent = "FC S: error";
      statusPill.className = "pill bad";
    }
  }

  async function pollLogs() {
    try {
      const data = await jsonFetch(`/api/log/tail?since=${state.logSeq}`);
      for (const entry of data.entries) {
        logOutput.textContent += `[${entry.ts}] [${entry.label}] ${entry.message}\n`;
      }
      state.logSeq = data.next_seq;
      logOutput.scrollTop = logOutput.scrollHeight;
    } catch {
      // Ignore poll failures.
    }
  }

  document.getElementById("syncBtn").addEventListener("click", async () => {
    const body = {
      org: document.getElementById("ado_org").value,
      project: document.getElementById("ado_project").value,
      team: document.getElementById("ado_team").value,
      work_item_type: document.getElementById("ado_work_item_type").value,
      states: document.getElementById("ado_states").value,
      from_date: document.getElementById("ado_from_date").value,
      to_date: document.getElementById("ado_to_date").value,
    };
    try {
      await jsonFetch("/api/sync-devops", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      await refreshMarkdownFiles();
      showToast("DevOps sync finished");
    } catch (err) {
      showToast(err.message);
    }
  });

  document.getElementById("uploadExcelBtn").addEventListener("click", async () => {
    const fileInput = document.getElementById("excelFile");
    if (!fileInput.files.length) {
      showToast("Choose an Excel file first");
      return;
    }

    const form = new FormData();
    form.append("file", fileInput.files[0]);
    try {
      await jsonFetch("/api/upload-excel", { method: "POST", body: form });
      await refreshMarkdownFiles();
      showToast("Excel uploaded and converted");
    } catch (err) {
      showToast(err.message);
    }
  });

  document.getElementById("generateBtn").addEventListener("click", async () => {
    const path = markdownSelect.value;
    if (!path) {
      showToast("Choose a markdown source file");
      return;
    }
    try {
      const data = await jsonFetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path }),
      });
      state.generateSince = data.since;
      state.vscodeUrl = data.vscode_chat_url;
      try {
        await navigator.clipboard.writeText(data.prompt);
        showToast("Prompt copied — paste it into Copilot Chat in VS Code");
      } catch {
        showToast("Copy failed — manually copy from response text");
      }
      modal.showModal();
    } catch (err) {
      showToast(err.message);
    }
  });

  document.getElementById("openVsCodeBtn").addEventListener("click", () => {
    if (state.vscodeUrl) {
      window.location.href = state.vscodeUrl;
    }
  });

  document.getElementById("doneGenerateBtn").addEventListener("click", async () => {
    try {
      const data = await jsonFetch(`/api/tests/diff?since=${encodeURIComponent(state.generateSince)}`);
      showToast(`${data.count} new/changed test file(s) detected`);
      if (window.confirm("Run pytest now?")) {
        await jsonFetch("/api/run-tests", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            project_name: document.getElementById("projectName").value,
            date_stamp: document.getElementById("dateStamp").value,
          }),
        });
        await refreshReports();
        showToast("Tests + exports completed");
      }
    } catch (err) {
      showToast(err.message);
    }
  });

  document.getElementById("closeModalBtn").addEventListener("click", () => modal.close());

  document.getElementById("uploadAllBtn").addEventListener("click", async () => {
    try {
      await jsonFetch("/api/fcs-upload-all", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_name: document.getElementById("projectName").value,
          date_stamp: document.getElementById("dateStamp").value,
        }),
      });
      showToast("Bulk upload completed");
    } catch (err) {
      showToast(err.message);
    }
  });

  document.getElementById("dateStamp").value = new Date().toISOString().slice(0, 10);

  refreshMarkdownFiles();
  refreshReports();
  refreshFcsStatus();
  pollLogs();
  setInterval(pollLogs, 2500);
  setInterval(refreshFcsStatus, 30000);
})();
