"""
Atualizador automático do CSV de preços de ouro
"""

import yfinance as yf
import pandas as pd

TICKER = "GLD"
DATA_INICIO = "2010-01-01"
CAMINHO_SAIDA = "precos_ouro.csv"


def atualizar():
    df = yf.download(TICKER, start=DATA_INICIO, progress=False)
    if df.empty:
        raise RuntimeError(f"Falha ao baixar dados de {TICKER}")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    saida = df[["Close"]].reset_index()
    saida.columns = ["data", "preco"]
    saida["data"] = saida["data"].dt.strftime("%Y-%m-%d")
    saida["preco"] = saida["preco"].round(4)
    saida.to_csv(CAMINHO_SAIDA, index=False)

    print(f"OK: {len(saida)} linhas salvas em {CAMINHO_SAIDA}")
    print(f"Último preço: {saida.iloc[-1]['data']} = {saida.iloc[-1]['preco']}")


if __name__ == "__main__":
    atualizar()
