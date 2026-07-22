from sqlalchemy import create_engine

DB_URL = "postgresql+psycopg2://podft:podft-secret@localhost:5432/analytics"
engine = create_engine(DB_URL)
