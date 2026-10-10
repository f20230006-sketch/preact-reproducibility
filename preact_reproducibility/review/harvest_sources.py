"""Cache primary-source metadata and full texts for an auditable targeted review.

Full texts are local reading copies; do not redistribute without license checks.
"""
import json, re, time, hashlib
from pathlib import Path
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
IDS=['2602.03338','2608.03222','2605.06455','2606.05414','2605.08715','2607.27443','2604.15075','2609.02783','2605.15206','2608.23670','2609.25647','2508.00500','2509.02360','2605.06737','2602.02475','2601.12294','2605.12925','2609.34415','2210.03629','2303.11366','2504.08942','2310.17552','2608.02464','2503.18666','2607.09996','2505.00212','2503.13657','2307.13854','2308.03688','2310.06770','2505.23419','1706.04599','2603.20260','2607.09510','2604.12147','2509.10401','2512.06749','2509.25370','2505.08638','2602.11348']

def main():
    cache=ROOT/'sources'; cache.mkdir(parents=True,exist_ok=True)
    records=[]
    for aid in IDS:
        path=cache/(aid+'.html')
        try:
            if not path.exists():
                response=requests.get('https://arxiv.org/abs/'+aid,timeout=45)
                response.raise_for_status(); path.write_text(response.text,encoding='utf8'); time.sleep(3)
            soup=BeautifulSoup(path.read_text(encoding='utf8'),'html.parser')
            def meta(name): return [x.get('content') for x in soup.find_all('meta',attrs={'name':name})]
            abstract=soup.select_one('blockquote.abstract')
            history=soup.select_one('.submission-history')
            comments=soup.select_one('td.tablecell.comments')
            rec={'arxiv_id':aid,'title':(meta('citation_title') or [''])[0],
                 'authors':meta('citation_author'),'date':(meta('citation_date') or [''])[0],
                 'doi':(meta('citation_doi') or [''])[0],'comments':comments.get_text(' ',strip=True) if comments else '',
                 'history':history.get_text(' ',strip=True) if history else '',
                 'abstract':abstract.get_text(' ',strip=True) if abstract else '',
                 'source_url':'https://arxiv.org/abs/'+aid,
                 'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),
                 'metadata_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            version=re.findall(r'\[v(\d+)\]',rec['history']); rec['version']='v'+max(version,key=int) if version else 'v1'
            htmlurl='https://arxiv.org/html/'+aid+rec['version']
            fullpath=cache/(aid+'.txt')
            if not fullpath.exists():
                resp=requests.get(htmlurl,timeout=45); time.sleep(3)
                if resp.status_code==200:
                    fs=BeautifulSoup(resp.text,'html.parser')
                    for tag in fs(['script','style','nav','header','footer']): tag.decompose()
                    fullpath.write_text(fs.get_text(' ',strip=True),encoding='utf8')
                    rec['fulltext_url']=htmlurl
                else:
                    pdfpath=cache/(aid+'.pdf')
                    resp=requests.get('https://arxiv.org/pdf/'+aid+rec['version'],timeout=60); time.sleep(3)
                    if resp.status_code==200 and resp.content.startswith(b'%PDF'):
                        pdfpath.write_bytes(resp.content)
                        import subprocess
                        subprocess.run(['pdftotext','-layout',str(pdfpath),str(fullpath)],check=True)
                        rec['fulltext_url']='https://arxiv.org/pdf/'+aid+rec['version']
            rec['fulltext_available']=fullpath.exists()
            if fullpath.exists() and 'fulltext_url' not in rec: rec['fulltext_url']=htmlurl if not (cache/(aid+'.pdf')).exists() else 'https://arxiv.org/pdf/'+aid+rec['version']
            if fullpath.exists(): rec['fulltext_sha256']=hashlib.sha256(fullpath.read_bytes()).hexdigest()
            records.append(rec)
            (ROOT/'source_metadata.json').write_text(json.dumps(records,indent=2),encoding='utf8')
            print(aid,rec['version'],rec['title'],rec['fulltext_available'],flush=True)
        except Exception as exc:
            print(aid,'ERROR',str(exc),flush=True)

if __name__=='__main__': main()
