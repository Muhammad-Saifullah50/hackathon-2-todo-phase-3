import asyncio
import asyncpg
from src.config import settings

async def check_chat_data():
    # Use asyncpg directly
    conn = await asyncpg.connect(settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))

    print("\n=== Chat Threads ===")
    threads = await conn.fetch("SELECT id, user_id, title, created_at FROM chat_threads ORDER BY created_at DESC LIMIT 5")
    for t in threads:
        print(f"{t['id']} | {t['user_id']} | {t['title']} | {t['created_at']}")

    print("\n=== Chat Messages ===")
    messages = await conn.fetch("SELECT id, thread_id, type, role, created_at FROM chat_thread_items ORDER BY created_at DESC LIMIT 10")
    for m in messages:
        print(f"{m['id']} | {m['type']} | {m['role']} | {m['created_at']}")

    if not messages:
        print("No messages found in database!")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_chat_data())
