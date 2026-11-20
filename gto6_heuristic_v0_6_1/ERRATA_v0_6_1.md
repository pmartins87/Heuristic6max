# ERRATA — v0.6.1 (20/11/2026)

O relatório v0.6 de preservação foi produzido **antes** da regeneração do SHA256SUMS.txt, e indevidamente assinalou todos os 51 arquivos-base como SAME. Após empacotar v0.6, o manifesto SHA256SUMS.txt necessariamente diferiu da v0.5 por incluir novos arquivos.

A comparação correta é: **50/50 arquivos de conteúdo ancestral byte-identical; 1/1 manifesto SHA256SUMS.txt regenerado conforme esperado**, e cada manifesto é validado contra sua própria versão. Nenhum range, roteiro, teste estratégico ou cálculo da v0.6 foi alterado nesta correção de metadados.

Use V05_PRESERVATION_AUDIT_v0_6_1.csv. O arquivo LEGACY_SUPERSEDED é mantido apenas para rastreabilidade histórica.
