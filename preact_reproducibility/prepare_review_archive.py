"""Create an anonymous local review ZIP; does not publish or submit anything."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent
OUT=WORK/'release'


def main():
    OUT.mkdir(exist_ok=True)
    files=[]
    for path in ROOT.rglob('*'):
        if not path.is_file():continue
        relative=path.relative_to(ROOT)
        if any(part in {'data','sources','__pycache__','.venv','.git'} for part in relative.parts):continue
        if path.suffix in {'.pyc','.log','.aux'}:continue
        files.append((path,'preact_reproducibility/'+relative.as_posix()))
    paper=WORK/'paper_mosicom2026'
    for name in ['preact_mosicom2026.tex','author_metadata.json','intervention_protocol.tex','major_revision_response.md','v5_revision_response.md','README.md']:
        files.append((paper/name,'paper_mosicom2026/'+name))
    # The native compiler checks/updates the editor preview, but does not export.
    # Never include an older disk PDF as if it represented the current source.
    pdf=paper/'preact_mosicom2026.pdf'
    pdf_current=pdf.exists() and pdf.stat().st_mtime >= (paper/'preact_mosicom2026.tex').stat().st_mtime
    if pdf_current:files.append((pdf,'paper_mosicom2026/'+pdf.name))
    for path in sorted((paper/'figures').glob('*.pdf')):
        files.append((path,'paper_mosicom2026/figures/'+path.name))
    manifest=[{'path':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path,name in sorted(files,key=lambda z:z[1])]
    content=json.dumps({'scope':'Reproducibility archive with user-supplied author details; raw traces and copied paper full texts excluded.',
                        'main_pdf_included':pdf_current,'pdf_note':'Export the current editor preview before including a manuscript PDF; stale exports are excluded.',
                        'files':manifest},indent=2).encode()
    (OUT/'archive_manifest.json').write_bytes(content)
    zip_path=OUT/'PreAct_review_archive.zip'
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path,name in files:archive.write(path,name)
        archive.writestr('archive_manifest.json',content)
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.testzip() is None
        for item in manifest:assert hashlib.sha256(archive.read(item['path'])).hexdigest()==item['sha256']
        assert all('/sources/' not in name and '/data/' not in name for name in archive.namelist())
    digest=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    (OUT/'PreAct_review_archive.sha256').write_text(digest+'  '+zip_path.name+'\n',encoding='ascii')
    print('Archive validated:',len(files),'files;',zip_path.stat().st_size,'bytes;',digest)


if __name__=='__main__':main()
