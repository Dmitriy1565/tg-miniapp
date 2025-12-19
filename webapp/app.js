const tg = window.Telegram?.WebApp;
tg?.ready();

const statusEl = document.getElementById("status");
const notesEl = document.getElementById("notes");
const inputEl = document.getElementById("noteInput");

function setStatus(text) { statusEl.textContent = text; }

function getUserId() {
  // В Mini App можно получить данные пользователя (если доступны)
  // Для простоты: берём tg.initDataUnsafe.user.id
  const uid = tg?.initDataUnsafe?.user?.id;
  if (!uid) throw new Error("Не удалось получить user_id (открой Mini App через кнопку бота).");
  return uid;
}

async function post(path, payload) {
  // PUBLIC_WEBAPP_URL должен указывать на домен, где доступен backend
  const base = window.location.origin.replace(/\/webapp$/, "");
  const res = await fetch(`${base}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
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
    const user_id = getUserId();
    const text = (inputEl.value || "").trim();
    if (!text) return setStatus("Напиши текст заметки.");
    setStatus("Добавляю...");
    await post("/add", { user_id, text });
    inputEl.value = "";
    setStatus("✅ Добавлено!");
  } catch (e) {
    setStatus("Ошибка: " + e.message);
  }
};

document.getElementById("listBtn").onclick = async () => {
  try {
    const user_id = getUserId();
    setStatus("Загружаю...");
    const data = await post("/list", { user_id });
    renderNotes(data.notes || []);
    setStatus("Готово.");
  } catch (e) {
    setStatus("Ошибка: " + e.message);
  }
};

document.getElementById("clearBtn").onclick = async () => {
  try {
    const user_id = getUserId();
    setStatus("Очищаю...");
    await post("/clear", { user_id });
    renderNotes([]);
    setStatus("🗑 Очищено!");
  } catch (e) {
    setStatus("Ошибка: " + e.message);
  }
};
