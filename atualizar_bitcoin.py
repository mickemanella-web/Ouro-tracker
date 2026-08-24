"""
Atualizador automatico de retornos anuais do Bitcoin - Carteira Permanente
Segue exatamente o mesmo metodo do atualizar_dados.py: baixa precos via
yfinance (sem chave de API, sem conta em nenhum servico externo) e calcula
o retorno total de cada ano civil.

Por que trocamos a CoinGecko pelo yfinance:
A CoinGecko passou a exigir cadastro + chave de API gratuita em 2026, o que
significava mais uma conta externa pra manter. O Yahoo Finance ja tem o
ticker BTC-USD com historico desde 2014, e o yfinance acessa sem
autenticacao nenhuma - a mesma biblioteca que ja usamos pra VTI, TLT, GLD
e BIL no atualizar_dados.py.
"""
import json
from datetime import datetime, timezone
import pandas as pd
import yfinance as yf

TICKER = "BTC-USD"
# Bitcoin so tem historico confiavel no Yahoo Finance a partir de 2014
# (antes disso o volume de negociacao era baixo demais pra representar um
# preco de mercado real).
ANO_INICIAL = 2014
DATA_INICIO = f"{ANO_INICIAL - 1}-01-01"
SAIDA = "retornos_bitcoin.json"


def retorno_anual_bitcoin(inicio: str = DATA_INICIO) -> dict[int, float]:
    """Baixa precos diarios do BTC-USD e retorna {ano: retorno_percentual}."""
    df = yf.download(TICKER, start=inicio, progress=False, auto_adjust=True)
    if df.empty:
        raise RuntimeError(f"Falha ao baixar dados de {TICKER}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    close = df["Close"]
    close.index = pd.to_datetime(close.index)

    retornos: dict[int, float] = {}
    for ano in sorted(set(close.index.year)):
        if ano < ANO_INICIAL:
            continue
        serie_ano = close[close.index.year == ano]
        if len(serie_ano) < 2:
            continue
        preco_ini = float(serie_ano.iloc[0])
        preco_fim = float(serie_ano.iloc[-1])
        retornos[ano] = round((preco_fim / preco_ini - 1) * 100, 2)
    return retornos


def main() -> None:
    retornos = retorno_anual_bitcoin()

    # O ano corrente ainda esta em andamento (nao fechou em 31/12), entao um
    # retorno parcial nao e comparavel aos anos completos - mesma regra do
    # atualizar_dados.py. Ele volta a aparecer sozinho, automaticamente, em
    # janeiro.
    ano_atual = datetime.now(timezone.utc).year
    anos = sorted(a for a in retornos if a < ano_atual)

    if not anos:
        raise RuntimeError("Nenhum ano completo de dados do Bitcoin disponivel")

    saida = {
        "years": anos,
        "bitcoin": [retornos[a] for a in anos],
        "fonte": "yfinance (BTC-USD, precos de fechamento no Yahoo Finance)",
        "primeiro_ano_disponivel": ANO_INICIAL,
        "atualizado_em": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }

    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    print(f"OK: {SAIDA} salvo com {len(anos)} anos ({anos[0]}-{anos[-1]})")


if __name__ == "__main__":
    main()
