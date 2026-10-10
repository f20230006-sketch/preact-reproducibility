"""Check cited primary records and pin the dataset index used by this analysis."""
import hashlib
import json
import re
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from preact_pilot import DATA_ROOT

ROOT=Path(__file__).resolve().parent


def main():
    source=(ROOT.parent/'paper_mosicom2026/preact_mosicom2026.tex').read_text(encoding='utf8')
    metadata={r['arxiv_id']:r for r in json.loads((ROOT/'review/source_metadata.json').read_text(encoding='utf8'))}
    ids=set(re.findall(r'arXiv:(\d{4}\.\d{4,5})',source))|{'2210.03629','2303.11366'}
    records=[]
    for aid in sorted(ids):
        record={'arxiv_id':aid,'url':'https://arxiv.org/abs/'+aid,'verified_date':'2026-10-10'}
        try:
            response=requests.get(record['url'],timeout=40);response.raise_for_status()
            soup=BeautifulSoup(response.text,'html.parser')
            title=soup.find('meta',attrs={'name':'citation_title'})
            record['primary_title']=title.get('content') if title else None
            record['authors']=[t.get('content') for t in soup.find_all('meta',attrs={'name':'citation_author'})]
            record['identity_matches_snapshot']=record['primary_title']==metadata[aid]['title'] if aid in metadata else None
            record['status']='verified' if title else 'metadata_not_extracted'
        except Exception as exc:record['status']='unverified';record['error']=str(exc)
        records.append(record);print(aid,record['status'],flush=True);time.sleep(3)
    hub=json.loads((ROOT/'results/hub_provenance.json').read_text())
    url='https://huggingface.co/datasets/'+hub['dataset_id']+'/resolve/'+hub['revision']+'/index.jsonl'
    response=requests.get(url,timeout=60);response.raise_for_status()
    local=(DATA_ROOT/'rebench_index.jsonl').read_bytes()
    hub['index_sha256']=hashlib.sha256(local).hexdigest()
    hub['remote_index_sha256']=hashlib.sha256(response.content).hexdigest()
    hub['pinned_index_matches_local']=response.content==local
    hub['index_url']=url
    assert hub['pinned_index_matches_local'],'Current commit differs from the inspected source index; do not claim source pin.'
    selected=[json.loads(line) for line in local.decode('utf8').split('\n') if line.strip() and json.loads(line)['participant_key'] in {'claude-code','gpt-5.6-luna','qwen3.6-27b'}]
    (ROOT/'results/source_index.json').write_text(json.dumps(selected,indent=2),encoding='utf8')
    (ROOT/'results/hub_provenance.json').write_text(json.dumps(hub,indent=2),encoding='utf8')
    (ROOT/'review/bibliography_verification.json').write_text(json.dumps({'records':records,'scope':'Primary identity and hyperlink checks, not independent replication or acceptance verification.'},indent=2),encoding='utf8')


if __name__=='__main__': main()
