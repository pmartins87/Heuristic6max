# ADR-013 — HJ/CO: fronteira econômica antes de alterar ranges

**20/11/2026 — Decisão MANTER estratégia imutável.**

A v0.9 acrescenta três relatórios e 11 testes. HJ vs CO: fold condicional 77,5377%, call 14,0392%, 4bet 8,4231%, com pot odds imediatas de call 31,4286% para 3bet de 8 BB. A9o e KJo são RFI 100% e fold 100% VS_3BET; AQo também. **Não se conclui** que RFI, fold ou call têm EV melhor a partir disso.

O contrafactual `RFI_REMOVE` reduz matematicamente o fold no nó **pela remoção de mãos que se renderiam**, mas perde oportunidade de RFI; `FOLD_TO_CALL_25PP` reduz fold sem demonstrar equity, rake ou EQR. Nenhuma das duas melhorias estatísticas de fold significa melhoria de EV.

Call: equilíbrio algébrico sob modelo de pote terminal de 17,5 BB depende de rake/cap hipotéticos e realização arbitrária. 4bet: modelo de zero-equidade exige desistência total de cerca de 60,91% ao aumentar para 21,2 BB (não EV real). Não inferir estratégia ótima destas fronteiras.

**Gate G2-a HOLD, G2-b bloqueado; G1 segue sem replays reais.** Alterar somente após evidência por classe e premissas da plataforma-alvo, com testes de regressão e diff auditável. DeepCrusher/CrusherTBP intocados.
