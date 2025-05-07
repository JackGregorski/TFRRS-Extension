console.log("TFRRS extension loaded.");

function createResultPopup(x, y, selectedName) {
  removePopup();

  const container = document.createElement("div");
  container.className = "tfrrs-popup";
  container.style.cssText = `
    position: absolute;
    top: ${y}px;
    left: ${x}px;
    background: #fefefe;
    border: 1px solid #aaa;
    border-radius: 10px;
    padding: 14px;
    z-index: 10000;
    font-size: 14px;
    font-family: sans-serif;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.2);
    width: 280px;
    max-height: 400px;
    overflow-y: auto;
    color: #222;
  `;

  container.innerHTML = `
    <div style="font-weight: 600; font-size: 15px; margin-bottom: 8px;">Looking up: ${selectedName}</div>
    <div id="athlete-results" style="color: #555;">⏳ Searching...</div>
  `;

  document.body.appendChild(container);

  const output = container.querySelector("#athlete-results");

  fetch(`http://localhost:5000/tfrrs_lookup?name=${encodeURIComponent(selectedName)}`)
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        output.innerHTML = `<span style="color: red;">❌ ${data.error}</span>`;
      } else {
        output.innerHTML = `
          <div style="margin-bottom: 8px;"><strong>${data.name}</strong></div>
          ${data.top_marks.map(m => `<div style="margin-bottom: 4px;">${m}</div>`).join("")}

        `;
      }
    })
    .catch(() => {
      output.innerHTML = `<span style="color: red;">❌ Failed to fetch.</span>`;
    });
}

function removePopup() {
  const existing = document.querySelector(".tfrrs-popup");
  if (existing) existing.remove();
}

document.addEventListener("mouseup", (e) => {
  const selection = window.getSelection();
  const text = selection.toString().trim();
  if (text.length > 0) {
    const rect = selection.getRangeAt(0).getBoundingClientRect();
    createResultPopup(rect.left + window.scrollX + 10, rect.top + window.scrollY + 20, text);
  } else {
    removePopup();
  }
});

document.addEventListener("mousedown", removePopup);
