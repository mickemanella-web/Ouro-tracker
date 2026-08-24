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
import os
import time
from datetime import date
import urllib.request
import urllib.error

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
ANO_INICIAL = 2014  # primeiro ano com dado de mercado confiavel
ANO_FINAL = date.today().year

SAIDA_JSON = "retornos_bitcoin.json"

# A partir de 2026 a CoinGecko passou a exigir uma chave gratuita (Demo API
# Key) mesmo no plano publico/keyless. A chave fica guardada como Secret no
# GitHub (COINGECKO_API_KEY) e nunca aparece no codigo.
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY", "")


def timestamp_unix(ano, mes, dia):
    import calendar
    return calendar.timegm(date(ano, mes, dia).timetuple())


def preco_proximo_de(data_alvo):
    """Busca o preco de fechamento do BTC-USD mais proximo da data informada."""
    inicio = timestamp_unix(data_alvo.year, data_alvo.month, data_alvo.day)
    fim = inicio + 60 * 60 * 24 * 5  # janela de 5 dias, caso a data exata falte

    url = f"{COINGECKO_URL}?vs_currency=usd&from={inicio}&to={fim}"
    headers = {"User-Agent": "ouro-tracker-bitcoin/1.0"}
    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            dados = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="ignore")
        dica = ""
        if e.code == 401:
            dica = (
                " (a chave da CoinGecko nao foi aceita - verifique se o "
                "Secret COINGECKO_API_KEY no repositorio esta com o valor "
                "certo e se a chave ainda esta ativa no dashboard da CoinGecko)"
            )
        raise RuntimeError(
            f"CoinGecko retornou HTTP {e.code} para {data_alvo}{dica}: {corpo[:300]}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Falha de conexao com a CoinGecko para {data_alvo}: {e.reason}"
        ) from e

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
        time.sleep(2.5)  # respeitar rate limit gratuito da CoinGecko (IP compartilhado no GitHub Actions)

    return anos, retornos


def main():
    if not COINGECKO_API_KEY:
        raise RuntimeError(
            "Variavel de ambiente COINGECKO_API_KEY nao configurada. "
            "Crie uma chave gratuita em coingecko.com/en/developers/dashboard "
            "e salve como Secret do repositorio (Settings > Secrets and "
            "variables > Actions > New repository secret)."
        )

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
