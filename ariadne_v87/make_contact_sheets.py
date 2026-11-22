from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'

def contact(files, name, cols):
    if not files: raise RuntimeError('missing actual blender renders')
    ims=[Image.open(p).convert('RGBA') for p in files]
    w,h=ims[0].size
    sheet=Image.new('RGB',(cols*w,((len(ims)+cols-1)//cols)*(h+34)),(222,220,216))
    dr=ImageDraw.Draw(sheet)
    for i,(im,p) in enumerate(zip(ims,files)):
        x=(i%cols)*w;y=(i//cols)*(h+34)
        bg=Image.new('RGBA',im.size,(16,30,44,255))
        bg.alpha_composite(im)
        sheet.paste(bg.convert('RGB'),(x,y+34))
        dr.text((x+10,y+10),p.stem,fill=(15,15,16))
    sheet.save(OUT/name)

if __name__=='__main__':
    images=sorted((OUT/'render_24').glob('VIEW_*.png'))
    if len(images)!=24: raise RuntimeError('expected exactly 24 Blender render files')
    contact(images,'Ariadne_V87_24View_Engineering.png',6)
    keys=[OUT/'render_24'/('VIEW_%03d.png'%n) for n in (0,45,90,135,180,270)]
    contact(keys,'Ariadne_V87_6View_Engineering.png',3)
