"""Exporta tabelas auditáveis e inventário de nós, sem gerar bot operacional."""
from pathlib import Path
import csv
from rfi_reference import export_csv, TARGETS, RFI_VERSION

ROOT=Path(__file__).parent
export_csv(ROOT / 'RFI_100BB_169x5_DRAFT.csv')
positions=('LJ','HJ','CO','BTN','SB','BB')
rows=[]
for i,pos in enumerate(positions[:-1]):
    rows.append(dict(Node=f'PF.RFI.{pos}',Family='RFI',HeroPosition=pos,
                     VillainPosition='',Entries=169,Status='DRAFT',Decision='RAISE/LIMP/FOLD'))
    for defending_pos in positions[i+1:]:
        rows.append(dict(Node=f'PF.VS_OPEN.{pos}.{defending_pos}',Family='VS_OPEN',
                         HeroPosition=defending_pos,VillainPosition=pos,
                         Entries=169,Status='PENDING',Decision='3BET/CALL/FOLD'))
with (ROOT/'G2_Nodes_Inventory.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader();w.writerows(rows)
print('RFI:',len(TARGETS)*169,'linhas; inventário de nós:',len(rows),
      'RFI=',sum(r['Family']=='RFI' for r in rows),
      'VS_OPEN=',sum(r['Family']=='VS_OPEN' for r in rows))
