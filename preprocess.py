import pandas as pd

df = pd.read_parquet('Bluehouse.parquet')
df.청원내용 = df.청원내용.str.replace('\t', '', regex=True)
df.청원내용 = df.청원내용.str.replace('\r', '', regex=True)
df.청원내용 = df.청원내용.str.replace('\n', ' ', regex=True)
df.청원내용 = df.청원내용.str.replace('\s+', ' ', regex=True)
df.청원내용 = df.청원내용.str.strip()

df.답변원고 = df.답변원고.str.replace('\t', '', regex=True)
df.답변원고 = df.답변원고.str.replace('\r', ' ', regex=True)
df.답변원고 = df.답변원고.str.replace('\n', '', regex=True)
df.답변원고 = df.답변원고.str.replace('\s+', ' ', regex=True)
df.답변원고 = df.답변원고.str.strip()

df.number = df.number.astype(int)

df.to_parquet('Bluehouse_dump.parquet')
