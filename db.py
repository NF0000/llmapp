from sqlalchemy import create_engine,text
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL=f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
engine=create_engine(DB_URL,echo=True)

def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_message TEXT NOT NULL,
                assistant_reply TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
def insert_message(user_msg,reply):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO chat_history (user_message,assistant_reply) VALUES(:m,:r)"),
            {"m":user_msg, "r":reply}
        )
        
def get_recent_messages(limit=20):
    with engine.connect() as conn:
        rows=conn.execute(text("SELECT user_message, assistant_reply FROM chat_history ORDER BY id DESC LIMIT :n"),{"n":limit})
        messages=[]
        for user_msg, assistant_reply in rows:
            messages.append({"role":"assistant","content":assistant_reply})
            messages.append({"role":"user","content":user_msg})
        return messages