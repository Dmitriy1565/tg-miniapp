const tg = window.Telegram?.WebApp;
tg?.ready();

const statusEl = document.getElementById("status");
const notesEl = document.getElementById("notes");
const inputEl = document.getElementById("noteInput");

function setStatus(text) { statusEl.textContent = text; }



async function post(path, payload) {
  const base = window.location.origin.replace(/\/webapp$/, "");
  const res = await fetch(`${base}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Tg-Init-Data": tg?.initData || "",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text);
  }

  return res.json();
}


function renderNotes(list) {
  notesEl.innerHTML = "";
  if (!list.length) {
    notesEl.innerHTML = `<div class="note">Пока пусто 🙂</div>`;
    return;
  }
  for (const n of list) {
    const div = document.createElement("div");
    div.className = "note";
    div.innerHTML = `${escapeHtml(n.text)}<small>${n.created_at}</small>`;
    notesEl.appendChild(div);
  }
}

function escapeHtml(s) {
  return (s ?? "").replace(/[&<>"']/g, m => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[m]));
}

document.getElementById("addBtn").onclick = async () => {
  try {
    const text = (inputEl.value || "").trim();
    if (!text) return setStatus("Напиши текст заметки.");
    setStatus("Добавляю...");
    await post("/api/add", { text });
    inputEl.value = "";
    setStatus("✅ Добавлено!");
  } catch (e) {
    setStatus("Ошибка: " + e.message);
  }
};

document.getElementById("listBtn").onclick = async () => {
  try {
    setStatus("Загружаю...");
    const data = await post("/api/list", {});
    renderNotes(data.notes || []);
    setStatus("Готово.");
  } catch (e) {
    setStatus("Ошибка: " + e.message);
  }
};

document.getElementById("clearBtn").onclick = async () => {
  try {
    setStatus("Очищаю...");
    await post("/api/clear", {});
    renderNotes([]);
    setStatus("🗑 Очищено!");
  } catch (e) {
    setStatus("Ошибка: " + e.message);
  }
};
async function loadPlans() {
  try {
    setStatus("Загружаю тарифы...");
    const data = await post("/api/plans", {});
    renderPlans(data.plans || []);
    setStatus("");
  } catch (e) {
    setStatus("Ошибка загрузки тарифов");
  }
}
function renderPlans(plans) {
  notesEl.innerHTML = "";

  for (const p of plans) {
    const div = document.createElement("div");
    div.className = "note";
    div.innerHTML = `
      <strong>${p.name}</strong><br>
      <small>${p.days} дней</small><br>
      <b>${p.price} ₽</b><br><br>
      <button onclick="buyPlan(${p.id})">Купить</button>
    `;
    notesEl.appendChild(div);
  }
}
function buyPlan(planId) {
  alert("Покупка тарифа ID = " + planId + " (скоро будет оплата)");
}
loadPlans();
