"""
Atualizador automatico de retornos anuais - Carteira Permanente
Baixa precos ajustados (dividendos reinvestidos) de VTI, TLT, GLD e BIL
via yfinance, calcula o retorno total de cada ano civil, e salva um
JSON consolidado (retornos_anuais.json) usado pelo site ao vivo.
"""

import json
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

TICKERS = {
    "stocks": "VTI",   # Acoes EUA
    "bonds": "TLT",    # Titulos longos do Tesouro (20+ anos)
    "gold": "GLD",     # Ouro
    "cash": "BIL",     # T-Bills / caixa
}

DATA_INICIO = "2006-01-01"
SAIDA = "retornos_anuais.json"

# BIL so existe a partir de 2007-05-30, entao 2006 fica sem dado real.
# Mantemos uma estimativa fixa (taxa media de T-Bills em 2006) so para esse
# ano que nenhum ticker cobre - documentado aqui para ficar rastreavel.
FALLBACK_CASH = {
    2006: 4.8,
}


def retorno_anual(ticker: str, inicio: str = DATA_INICIO) -> dict[int, float]:
    """Baixa precos ajustados e retorna {ano: retorno_percentual}."""
    df = yf.download(ticker, start=inicio, progress=False, auto_adjust=True)
    if df.empty:
        raise RuntimeError(f"Falha ao baixar dados de {ticker}")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    close = df["Close"]
    close.index = pd.to_datetime(close.index)

    retornos: dict[int, float] = {}
    for ano in sorted(set(close.index.year)):
        serie_ano = close[close.index.year == ano]
        if len(serie_ano) < 2:
            continue
        preco_ini = float(serie_ano.iloc[0])
        preco_fim = float(serie_ano.iloc[-1])
        retornos[ano] = round((preco_fim / preco_ini - 1) * 100, 2)

    return retornos


def main() -> None:
    dados: dict[str, dict[int, float]] = {}
    for chave, ticker in TICKERS.items():
        dados[chave] = retorno_anual(ticker)
        print(f"{chave} ({ticker}): {len(dados[chave])} anos calculados")

    # Anos em comum entre stocks, bonds e gold (esses tres cobrem 2006+)
    anos = sorted(set(dados["stocks"]) & set(dados["bonds"]) & set(dados["gold"]))

    def valor_cash(ano: int) -> float:
        if ano in dados["cash"]:
            return dados["cash"][ano]
        if ano in FALLBACK_CASH:
            print(f"  aviso: cash/{ano} sem dado do BIL, usando estimativa fixa")
            return FALLBACK_CASH[ano]
        raise RuntimeError(f"Sem dado de cash para {ano} e sem fallback definido")

    saida = {
        "years": anos,
        "stocks": [dados["stocks"][a] for a in anos],
        "bonds": [dados["bonds"][a] for a in anos],
        "gold": [dados["gold"][a] for a in anos],
        "cash": [valor_cash(a) for a in anos],
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "fonte": "yfinance (VTI, TLT, GLD, BIL - precos ajustados por dividendos)",
    }

    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    print(f"OK: {SAIDA} salvo com {len(anos)} anos ({anos[0]}-{anos[-1]})")


if __name__ == "__main__":
    main()
