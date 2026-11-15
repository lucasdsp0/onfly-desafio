# Entrega:
 
Eu corrigi cinco defeitos no CLI, um por commit e fiz um teste novo para cada um . O *pytest -q* passa com 17 testes (5 que já existiam e 12 que eu criei).
 
## Defeitos corrigidos
 

| # | Local | Causa raiz | Commit |
|---|------|-----------|--------|
| 1 | `services/stay_calculator.py` | O código comparava só o número do dia (*checkout.day - checkin.day*), sem olhar mês nem ano, então toda estadia que virava o mês ou o ano dava noites com números negativos. | `82afebc` |
| 2 | `services/currency_converter.py` | A conversão estava dividindo o valor pela taxa ao invés de multiplicar e ainda passava tudo para *float*, o que fazia os centavos perderem precisão. | `f8af5ab` |
| 3 | `services/status_policy.py` | A regra de faturamento só excluía *CANCELLED* (*status != "CANCELLED"*), deixando *NO_SHOW* passar, quando o único status faturável é *CONFIRMED*. | `a618660` |
| 4 | `services/report_builder.py` | A chave do *sorted* colocava o total em ordem crescente, fazendo com que o *top_hotels* ficasse invertido, o correto é total decrescente e desempatando por *hotel_id* crescente. | `4ec8340` |
| 5 | `repositories/csv_reservation_repository.py` | Tinha um *break* interrompendo a leitura quando atingia 200 linhas, sendo que o arquivo contém 300, logo 100 ficavam de fora. | `bec2a2b` |
 
 
## Como investiguei
 
Executei o *pytest -q* e vi 5 falhas. Rodei a amostra e ela retornou Noites: -33 e Total BRL: 5962.41, valores que não batiam com o valor esperado (28 e 7566.00) que estavam nas instruções do README. Rodei também o arquivo completo e ele retornou 200 reservas sendo que o arquivo tem 300 reservas, percebi que não tinha nenhum teste para esse erro, então ele só apareceu comparando o resumo com o arquivo.
 
Os números da amostra também foram me mostrando o que faltava. Corrigi as noites, e a amostra passou de -33 para 29, e esse 1 a mais era o status de *NO_SHOW* entrando na soma, corrigindo o status, as noites fecharam em 28 e o total foi para 5662.41. Sobrou o câmbio para corrigir, e ao corrigi-lo o total chegou a 7566.00. O ranking só ficou certo quando terminei de fazer o último ajuste.

Com a ajuda das regras de negócio e instruções do README, fui corrigindo um defeito por vez.
 
## Como validar
 
Em bash (o README instrui usar `PYTHONPATH=src`):
 
```sh
pip install -r requirements-dev.txt
pytest -q
PYTHONPATH=src python -m onfly_report --input data/exemplo-validacao.csv \
  --rates data/taxas_cambio.csv --output output/exemplo.json
PYTHONPATH=src python -m onfly_report --input data/reservas_hoteis.csv \
  --rates data/taxas_cambio.csv --output output/report.json
```
 
No PowerShell, troque a variável por `$env:PYTHONPATH="src"` antes dos dois comandos do CLI.
 
Use python `>=3.11` (Utilizei o 3.14).
 
## Resultado do pytest
 
```
.................                                                        [100%]
17 passed in 1.11s
```
 
São os 5 testes que já existiam mais 12 novos que eu criei, que ficam em arquivos próprios:
 
- `test_stay_calculator.py`: 4 testes (mesmo mês, virada de mês, virada de ano, vários quartos).
- `test_currency_converter.py`: 3 testes (USD, EUR e um caso que pega erro de *float*).
- `test_status_policy.py`: 3 testes (um por status).
- `test_reservation_repository.py`: 1 teste (lê as 300 reservas do arquivo).
- `test_report_builder.py`: 1 teste (desempate do ranking por *hotel_id*).

Novos testes criados após revisão com IA:

- `test_money_rounding.py`: 9 testes (arredondamento half-up, soma exata sem arredondar por linha, média sobre o total exato e formato do dinheiro).
- `test_aggregations.py`: 13 testes (`by_month` pelo mês do check-in e em ordem crescente; `top_hotels` só com CONFIRMED, ranking por valor em BRL, corte do `--top` e desempate por *hotel_id*).
- `test_readme_sample_and_dataset.py`: 9 testes (confere a amostra e o dataset completo com os valores do README).
- `helpers_extra.py`: funções de apoio dos novos testes, sem alterar o `helpers.py` fornecido.
