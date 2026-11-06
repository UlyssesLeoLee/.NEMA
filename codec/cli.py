"""python -m codec.cli [render|check|encode|decode] input [--output PATH] [--cost bytes|bpe|unigram]."""
import argparse, pathlib, json
from .core import parse, render
from .transport import encode, decode

def main():
    p=argparse.ArgumentParser(description='NEMA v1.5 native/transport utilities')
    p.add_argument('command',choices=['render','check','encode','decode'])
    p.add_argument('input')
    p.add_argument('--output');p.add_argument('--cost',choices=['bytes','bpe','unigram'],default='bytes')
    a=p.parse_args();source=pathlib.Path(a.input).read_text(encoding='utf-8')
    if a.command=='check':
        x=parse(source); out=json.dumps({'valid':True,'domains':len(x.domains)},ensure_ascii=False,indent=2)
    elif a.command=='render': out=json.dumps(render(source),ensure_ascii=False,indent=2)
    elif a.command=='decode': out=decode(source)
    else:
        fn=None
        if a.cost!='bytes':
            import sentencepiece as spm
            mdl=pathlib.Path(__file__).resolve().parents[1]/'bench'/'models'/('neutral_bpe.model' if a.cost=='bpe' else 'neutral_unigram.model')
            sp=spm.SentencePieceProcessor(model_file=str(mdl))
            fn=lambda text:len(sp.encode(text))
        choice=encode(source,token_cost=fn)
        out=choice.text
        print(json.dumps({'method':choice.method,'format':choice.format,'score':choice.score,'baseline':choice.baseline_score,'saving_pct':choice.saving_percent},ensure_ascii=False))
    if a.output:pathlib.Path(a.output).write_text(out,encoding='utf-8')
    else:print(out)
if __name__=='__main__': main()
