"""Run from package root: python -m codec.cli {render,encode,decode,inspect} file"""
import argparse,json,sys,pathlib
from . import native,nemat

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['render','encode','decode','inspect'])
    p.add_argument('file');p.add_argument('--output');p.add_argument('--cost',choices=['bytes','bpe','unigram'],default='bytes')
    a=p.parse_args();s=pathlib.Path(a.file).read_text(encoding='utf-8')
    if a.action=='render':content=json.dumps(native.view(s),ensure_ascii=False,indent=2)
    elif a.action=='decode':content=nemat.decode(s)
    elif a.action=='inspect':
        content=json.dumps({k:{'score':v.score,'bytes':v.result_bytes} for k,v in nemat.candidates(s).items()},ensure_ascii=False,indent=2)
    else:
        score=None
        if a.cost!='bytes':
            import sentencepiece as spm
            path=pathlib.Path(__file__).parents[1]/'bench'/f'neutral_{a.cost}.model'
            model=spm.SentencePieceProcessor(model_file=str(path))
            score=lambda t:len(model.encode(t))
        content=nemat.optimize(s,score).text
    if a.output:pathlib.Path(a.output).write_text(content,encoding='utf-8',newline='\n')
    else:sys.stdout.write(content)

if __name__=='__main__':main()
