import aiosqlite

DB_PATH = "app.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
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
