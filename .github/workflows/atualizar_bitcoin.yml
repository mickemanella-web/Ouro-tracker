"""
Atualiza os retornos anuais historicos do Bitcoin (BTC-USD).

Segue o mesmo padrao do script atualizar_precos_ouro.py do repositorio Ouro-tracker,
gerando um arquivo JSON com "years" e "bitcoin" (retorno percentual anual).

Fonte de dados: CoinGecko API (publica, sem necessidade de chave de API).
Documentacao: https://www.coingecko.com/en/api/documentation

O Bitcoin so tem dados de mercado confiaveis a partir de ~2013-2014 (antes disso
o volume de negociacao era baixo demais para representar um preco de mercado real).
Por isso o dataset comeca em 2014.
"""

import json
import time
from datetime import date
import urllib.request

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
ANO_INICIAL = 2014  # primeiro ano com dado de mercado confiavel
ANO_FINAL = date.today().year

SAIDA_JSON = "retornos_bitcoin.json"


def timestamp_unix(ano, mes, dia):
    import calendar
    return calendar.timegm(date(ano, mes, dia).timetuple())


def preco_proximo_de(data_alvo):
    """Busca o preco de fechamento do BTC-USD mais proximo da data informada."""
    inicio = timestamp_unix(data_alvo.year, data_alvo.month, data_alvo.day)
    fim = inicio + 60 * 60 * 24 * 5  # janela de 5 dias, caso a data exata falte

    url = f"{COINGECKO_URL}?vs_currency=usd&from={inicio}&to={fim}"
    with urllib.request.urlopen(url) as resp:
        dados = json.loads(resp.read().decode())

    precos = dados.get("prices", [])
    if not precos:
        raise ValueError(f"Sem dados de preco proximos a {data_alvo}")

    # primeiro preco disponivel na janela
    return precos[0][1]


def calcular_retornos_anuais():
    anos = []
    retornos = []

    preco_anterior = preco_proximo_de(date(ANO_INICIAL - 1, 12, 31))

    for ano in range(ANO_INICIAL, ANO_FINAL + 1):
        # 31/dez, exceto no ano corrente (usa o dia de hoje)
        if ano == ANO_FINAL:
            data_ref = date.today()
        else:
            data_ref = date(ano, 12, 31)

        preco_atual = preco_proximo_de(data_ref)
        retorno_pct = round((preco_atual / preco_anterior - 1) * 100, 2)

        anos.append(ano)
        retornos.append(retorno_pct)

        preco_anterior = preco_atual
        time.sleep(1.5)  # respeitar rate limit gratuito da CoinGecko

    return anos, retornos


def main():
    anos, retornos = calcular_retornos_anuais()

    saida = {
        "years": anos,
        "bitcoin": retornos,
        "fonte": "CoinGecko API",
        "primeiro_ano_disponivel": ANO_INICIAL,
        "atualizado_em": date.today().isoformat(),
    }

    with open(SAIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(saida, f, indent=2, ensure_ascii=False)

    print(f"Arquivo {SAIDA_JSON} atualizado com {len(anos)} anos de dados.")


if __name__ == "__main__":
    main()
