import aiosqlite

DB_PATH = "app.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # таблица заметок (уже была)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 👇 НОВОЕ: таблица тарифов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                days INTEGER NOT NULL,
                price INTEGER NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'created',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # добавить колонку access_code, если её ещё нет
        try:
         await db.execute("ALTER TABLE orders ADD COLUMN access_code TEXT")
        except Exception:
            pass



        # если тарифов ещё нет — добавляем стартовые
        cur = await db.execute("SELECT COUNT(*) FROM plans")
        (count,) = await cur.fetchone()
        if count == 0:
            await db.executemany(
                "INSERT INTO plans (name, days, price) VALUES (?, ?, ?)",
                [
                    ("1 месяц", 30, 299),
                    ("3 месяца", 90, 699),
                    ("12 месяцев", 365, 2499),
                ],
            )

        await db.commit()


async def add_note(user_id: int, text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO notes (user_id, text) VALUES (?, ?)", (user_id, text))
        await db.commit()

async def get_notes(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, text, created_at FROM notes WHERE user_id=? ORDER BY id DESC", (user_id,))
        rows = await cur.fetchall()
        return [{"id": r[0], "text": r[1], "created_at": r[2]} for r in rows]

async def clear_notes(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM notes WHERE user_id=?", (user_id,))
        await db.commit()

async def create_order(user_id: int, plan_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO orders (user_id, plan_id, status) VALUES (?, ?, 'created')",
            (user_id, plan_id),
        )
        await db.commit()
        return cur.lastrowid

async def get_last_order(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            SELECT o.id, o.plan_id, o.status, o.created_at,
                   p.name, p.days, p.price
            FROM orders o
            JOIN plans p ON p.id = o.plan_id
            WHERE o.user_id = ?
            ORDER BY o.id DESC
            LIMIT 1
        """, (user_id,))
        row = await cur.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "plan_id": row[1],
        "status": row[2],
        "created_at": row[3],
        "plan": {"name": row[4], "days": row[5], "price": row[6]},
    }

async def set_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        await db.commit()

async def set_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        await db.commit()

import secrets

async def issue_access_for_order(order_id: int) -> str:
    access = secrets.token_urlsafe(16)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE orders SET access_code=? WHERE id=?",
            (access, order_id),
        )
        await db.commit()
    return access
