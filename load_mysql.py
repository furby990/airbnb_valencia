import pandas as pd
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, text

ROOT      = Path(r'C:\Users\User\Desktop\GitHub\PROYECTO FINAL FINAL\airbnb_valencia')
PROCESSED = ROOT / 'data' / 'processed'

conn  = sqlite3.connect(PROCESSED / 'airbnb_valencia.db')
df_l  = pd.read_sql('SELECT * FROM listings', conn)
df_r  = pd.read_sql('SELECT * FROM reviews', conn)
df_s  = pd.read_sql('SELECT * FROM investment_scores', conn)
conn.close()
print(f'SQLite OK: {len(df_l):,} listings, {len(df_r):,} reviews')

engine = create_engine('mysql+pymysql://root:32627787Df.@localhost:3306/airbnb_valencia')

df_l.to_sql('listings',          engine, if_exists='replace', index=False, chunksize=500)
print('listings OK')
df_s.to_sql('investment_scores', engine, if_exists='replace', index=False)
print('investment_scores OK')
df_r.to_sql('reviews',           engine, if_exists='replace', index=False, chunksize=1000)
print('reviews OK - todo cargado')