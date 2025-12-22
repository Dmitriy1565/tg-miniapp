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
  setStatus("Ошибка загрузки тарифов: " + e.message);
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

async function buyPlan(planId) {
  try {
    setStatus("Создаю заказ...");
    const data = await post("/api/order/create", { plan_id: planId });
    setStatus("✅ Заказ создан: #" + data.order_id);
  } catch (e) {
    setStatus("Ошибка покупки: " + e.message);
  }
}

document.getElementById("myOrderBtn").onclick = async () => {
  try {
    setStatus("Загружаю заказ...");
    const data = await post("/api/order/last", {});
    const order = data.order;
    lastOrderId = order.id;

lastOrderId = order.id;

if (order.status === "created") {
  payBtn.style.display = "block";
} else {
  payBtn.style.display = "none";
}
if (order.status === "paid") {
  accessBtn.style.display = "block";
} else {
  accessBtn.style.display = "none";
}




    if (!order) {
      setStatus("У тебя пока нет заказов.");
      return;
    }

    const p = order.plan;
    setStatus(
      `Последний заказ #${order.id}: ${p.name} (${p.days} дней) — ${p.price} ₽, статус: ${order.status}`
    );
  } catch (e) {
    setStatus("Ошибка: " + e.message);
  }
};

const payBtn = document.getElementById("payBtn");
let lastOrderId = null;

payBtn.onclick = async () => {
  try {
    if (!lastOrderId) return;
    setStatus("Помечаю как оплачено...");
    await post("/api/order/mark_paid", { order_id: lastOrderId });
    setStatus("✅ Оплачено (тест)!");
    payBtn.style.display = "none";
  } catch (e) {
    setStatus("Ошибка оплаты: " + e.message);
  }
};

const accessBtn = document.getElementById("accessBtn");
const accessBox = document.getElementById("accessBox");

accessBtn.onclick = async () => {
  try {
    setStatus("Получаю доступ...");
    const data = await post("/api/order/access", {});
    accessBox.innerHTML = `<div class="note"><b>Твой код доступа:</b><br>${data.access_code}<br><small>Это заглушка. Позже тут будет VPN-конфиг.</small></div>`;
    setStatus("✅ Доступ выдан!");
  } catch (e) {
    setStatus("Ошибка: " + e.message);
  }
};

