"""Build a deliberately SYNTHETIC example evidence bundle from the pinned source.

No observation, bot action or OpenHoldem runtime data is invented. The filled
source SHA is the only value derived from a real project file.
"""
from __future__ import annotations
import json
from pathlib import Path
from evidence_gate import ARTIFACT_EXT,PROTOCOL,catalog,source_digest

HERE=Path(__file__).resolve().parent
TARGET=HERE/'SYNTHETIC_BUNDLE.json'


def render()->str:
    cfg,cases=catalog()
    first=cases['RFI_BTN_PURE']
    empty_artifacts={k:{'path':'','sha256':''} for k in ARTIFACT_EXT}
    payload={
        'protocol':PROTOCOL,'capture_mode':'SYNTHETIC',
        'offline_attested':True,'connected_live':False,
        'openholdem_version':'',
        'openholdem_exe_sha256':'',
        'tablemap_sha256':'',
        'loaded_oppl_sha256':source_digest(cfg),
        'cases':[{
            'case_id':first['case_id'],'session_id':'SYNTHETIC_ONLY',
            'hand_id':'NO_REAL_HAND','eval_index':0,'street':first['street'],
            'symbols':{x:'' for x in first['required_symbols']},
            'reported_best_action':'','reported_action_taken':'',
            'artifacts':empty_artifacts
        }]
    }
    return json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False)+'\n'


def build()->None:
    TARGET.write_text(render(),encoding='utf-8',newline='\n')


if __name__=='__main__':
    build()
    print('Created SYNTHETIC example, no runtime actions or validated OH evidence')
