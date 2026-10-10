"""Compare original and revision result JSONs across two analysis environments."""
import argparse
import json
from pathlib import Path

FILES=['preact_pilot_results.json','preact_pilot_audit_results.json','preact_invariance_ablation_results.json',
       'preact_retry_opportunity_results.json','major_revision_results.json']


def compare(reference,candidate,tolerance):
    differences=[];numbers=[]
    def walk(a,b,path=''):
        if isinstance(a,dict) and isinstance(b,dict):
            if set(a)!=set(b):differences.append({'path':path,'reason':'keys differ'})
            for key in sorted(set(a)&set(b)):walk(a[key],b[key],path+'/'+key)
        elif isinstance(a,list) and isinstance(b,list):
            if len(a)!=len(b):differences.append({'path':path,'reason':'length differs'})
            for i,(v,w) in enumerate(zip(a,b)):walk(v,w,path+'/'+str(i))
        elif isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)):
            numbers.append(abs(a-b))
            if abs(a-b)>tolerance:differences.append({'path':path,'reference':a,'candidate':b})
        elif a!=b:differences.append({'path':path,'reference':a,'candidate':b})
    walk(reference,candidate)
    return {'max_absolute_numeric_difference':max(numbers,default=0),'numeric_fields':len(numbers),'mismatches_above_tolerance':differences}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--tolerance',type=float,default=1e-8)
    args=parser.parse_args()
    reports=[]
    for name in FILES:
        a=json.loads((args.reference/name).read_text(encoding='utf8'))
        b=json.loads((args.candidate/name).read_text(encoding='utf8'))
        reports.append({'file':name,**compare(a,b,args.tolerance)})
    args.output.write_text(json.dumps({'scope':'Same source/data numerical rerun in an isolated environment, not independent data collection.',
                           'tolerance':args.tolerance,'reports':reports},indent=2),encoding='utf8')
    assert all(not r['mismatches_above_tolerance'] for r in reports),'Replication mismatch; inspect comparison report.'
    print('All five numerical result files match within',args.tolerance)


if __name__=='__main__':main()
