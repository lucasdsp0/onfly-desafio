# Declaração de uso de IA

## Ferramenta e modelo

- **Ferramenta:** Claude (Anthropic), pela interface de chat claude.ai.
- **Modelo:** Claude Sonnet 5.5.
- **Sessão registrada:** uma conversa, em 15/11/2026 (`sessao.md`).

## O que a IA fez

Nesta sessão, a partir do projeto já corrigido por mim (zip enviado) e do README do desafio, a IA:

1. Revisou o código, o relatório gerado e o `README-ENTREGA.md` contra cada regra do README: rodou `pytest`, o CLI na amostra e no dataset completo, recalculou os resultados com um script independente e apontou pontos de atenção.
2. Avaliou a qualidade dos 12 testes que eu havia criado, inclusive com teste de mutação (injeção de 34 defeitos no código).
3. Identificou regras de negócio sem teste e escreveu 88 testes novos em 7 arquivos (mais um helper) para cobri-las.
4. Redigiu este documento e o log da sessão.

A IA **não alterou** o código do CLI nem os testes que eu já tinha, e não gerou nenhum arquivo dentro do meu repositório: entregou os arquivos separados para eu avaliar. O que será incorporado ao projeto foi decidido por mim.

## O que eu fiz

- Investiguei e corrigi os 5 defeitos do CLI, um por commit, e escrevi os 12 testes novos correspondentes.
- Escrevi o `entrega/README-ENTREGA.md`.
- Revisei as sugestões da IA e decidi o que adotar apenas test_readme_sample_and_dataset.py, test_money_rounding.py e test_aggregations.py.
- Conferi com `git diff` que os testes fornecidos e os CSVs de `data/` permaneceram inalterados:

