name: Atualizar dados do simulador

on:
  schedule:
    # Todos os dias as 06:00 UTC (03:00 no horario de Brasilia)
    - cron: '0 6 * * *'
  workflow_dispatch: {}   # permite rodar manualmente pelo botao "Run workflow" no GitHub

jobs:
  atualizar:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Instalar dependencias
        run: pip install yfinance pandas

      - name: Atualizar preco do ouro (script existente)
        run: python atualizar_precos_ouro.py

      - name: Atualizar retornos anuais (todos os ativos)
        run: python atualizar_dados.py

      - name: Commitar mudancas
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add precos_ouro.csv retornos_anuais.json
          git diff --staged --quiet || git commit -m "Atualizacao automatica de dados $(date -u +'%Y-%m-%d')"
          git push
