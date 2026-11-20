"""Offline assembly only; no independent poker strategy in Python."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
PRE=HERE.parent/'vs_3bet_mvp'/'preflop_rfi_vsopen_vs3_draft.oppl'
POST=HERE/'srp_hu_postflop_draft.oppl'
OUT=HERE/'preflop_and_srp_hu_draft.oppl'

def generate():
    previous=PRE.read_text(encoding='utf-8')
    post=POST.read_text(encoding='utf-8')
    if previous.count('##f$preflop##')!=1 or post.count('##f$flop##')!=1 or post.count('##f$turn##')!=1 or post.count('##f$river##')!=1:
        raise ValueError('preflop/postflop section mismatch')
    combined=previous.rstrip()+'\n\n'+post
    OUT.write_text(combined,encoding='utf-8',newline='\n')
    return (len(previous.splitlines()),len(post.splitlines()))

if __name__=='__main__':print('combined',generate())
