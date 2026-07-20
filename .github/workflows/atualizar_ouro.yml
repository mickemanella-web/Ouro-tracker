name: Atualizar preços do ouro

on:
  schedule:
    - cron: "0 22 * * 1-5"   # 22h UTC = 19h em Brasília (seg a sex, dias úteis)
  workflow_dispatch:          # permite rodar manualmente pelo botão "Run workflow"

permissions:
  contents: write

jobs:
  atualizar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Instalar dependências
        run: pip install yfinance pandas

      - name: Rodar script de atualização
        run: python atualizar_precos_ouro.py

      - name: Commitar CSV atualizado
        run: |
          git config user.name "gold-bot"
          git config user.email "gold-bot@users.noreply.github.com"
          git add precos_ouro.csv
          git diff --staged --quiet || git commit -m "Atualiza preços do ouro"
          git push
