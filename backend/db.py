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
