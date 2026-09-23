"""Vector-only 2D callouts around unchanged Blender renders; PDFs, SVGs and previews."""
from pathlib import Path
from io import BytesIO
import json, base64, math, html, argparse
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
import pypdfium2 as pdfium

MODELS=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("scenes",nargs="*",help="Scene basenames; omit for all figures.")
parser.add_argument("--renders",type=Path,default=MODELS/"renders"/"archive")
parser.add_argument("--manifest",type=Path,default=MODELS/"clean_model_manifest.json")
parser.add_argument("--output",type=Path,default=MODELS/"generated"/"labels")
args=parser.parse_args()
ROOT=args.output.resolve()
ROOT.mkdir(parents=True,exist_ok=True)
SIDES={
'01':{1:'L',2:'R',3:'L'},'02':{1:'L',2:'L',3:'R'},
'03':{1:'L',2:'R',3:'R'},'04':{1:'L',2:'L',3:'L',4:'R',5:'R',6:'R'},
'05':{1:'L',2:'L',3:'R',4:'R',5:'R'},'06':{1:'L',2:'R',3:'L',4:'R',5:'R'},
'08':{1:'L',2:'L',3:'L',4:'R',5:'R',6:'R'}}
NAVY=(.025,.12,.18);GREY=(.20,.28,.32)
def svgtext(x,y,text,size=11,bold=False,anchor='start'):
    return f'<text x="{x:.3f}" y="{y:.3f}" fill="#112d3d" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{html.escape(text)}</text>'

records=json.loads(args.manifest.read_text(encoding="utf-8"))
unknown=set(args.scenes)-{record["stem"] for record in records}
if unknown:parser.error("Unknown scene(s): "+", ".join(sorted(unknown)))
verification=[]
for rec in records:
    stem=rec['stem'];num=stem[:2];wide=num in {'07','08'}
    if args.scenes and stem not in args.scenes:continue
    W=400.0 if wide else 237.6;H=W*1750/2600
    rowh=14.3;anchors=rec['anchors'];rows=(len(anchors)+1)//2
    legend_h=rows*rowh+9;floor=legend_h+5
    alpha=Image.open(args.renders/(stem+'_clean.png')).convert('RGBA')
    crop=alpha.getchannel('A').point(lambda a:255 if a>5 else 0).getbbox()
    assert crop is not None
    crop=(max(0,crop[0]-8),max(0,crop[1]-8),min(alpha.width,crop[2]+8),min(alpha.height,crop[3]+8))
    region=alpha.crop(crop);cw,ch=region.size
    image_left=24;image_right=W-24;image_bottom=floor+3;image_top=H-9
    if num=='07':image_top=H-37
    scale=min((image_right-image_left)/cw,(image_top-image_bottom)/ch)
    iw,ih=cw*scale,ch*scale;ix=(W-iw)/2;iy=image_bottom+(image_top-image_bottom-ih)/2
    # A quality-96 RGB JPEG controls PDF size; the original RGBA PNG is preserved.
    white=Image.new('RGB',region.size,'white');white.paste(region,mask=region.getchannel('A'))
    jpg=BytesIO();white.save(jpg,format='JPEG',quality=96,subsampling=0,optimize=True);jpeg=jpg.getvalue()
    (ROOT/(stem+'_background.jpg')).write_bytes(jpeg)
    c=canvas.Canvas(str(ROOT/(stem+'.pdf')),pagesize=(W,H),pageCompression=1)
    c.setTitle(stem.replace('_',' ')+' — flat vector labels')
    c.setAuthor('BLUESHIELD FILTER project')
    c.setFillColorRGB(1,1,1);c.rect(0,0,W,H,fill=1,stroke=0)
    c.drawImage(ImageReader(BytesIO(jpeg)),ix,iy,width=iw,height=ih)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="white"/>',f'<image x="{ix}" y="{H-iy-ih}" width="{iw}" height="{ih}" href="data:image/jpeg;base64,{base64.b64encode(jpeg).decode()}"/>']
    pts=[]
    for a in anchors:
        px=a['u']*alpha.width;py=(1-a['v'])*alpha.height
        ax=ix+(px-crop[0])*scale;ay=iy+(crop[3]-py)*scale
        pts.append({**a,'ax':ax,'ay':ay})
    if num=='08':
        perimeter={1:(30,248),2:(30,86),3:(180,258),4:(390,238),5:(357,75),6:(390,160)}
        for a in pts:a['bx'],a['by']=perimeter[a['number']]
    elif num=='07':
        ordered=sorted(pts,key=lambda a:a['ax'])
        previous=-100
        for a in ordered:
            a['bx']=max(14,min(W-14,a['ax']));a['by']=H-14
            assert a['bx']-previous>17
            previous=a['bx']
    else:
        for side in ['L','R']:
            group=sorted([a for a in pts if SIDES[num][a['number']]==side],key=lambda a:-a['ay'])
            top=image_top-10;bottom=image_bottom+10
            if len(group)==1:ys=[(top+bottom)/2]
            else:ys=[top-(top-bottom)*i/(len(group)-1) for i in range(len(group))]
            for a,by in zip(group,ys):a['bx']=10 if side=='L' else W-10;a['by']=by
    circles=[]
    for a in pts:
        bx,by,ax,ay=a['bx'],a['by'],a['ax'],a['ay'];r=7.0
        # Leaders are routed from external circles; no text sits over the 3D model.
        if num=='08':
            routes={1:[(bx+r,by),(72,by),(ax,ay)],2:[(bx+r,by),(80,by),(80,ay-15),(ax,ay)],3:[(bx,by-r),(bx,240),(ax,ay)],4:[(bx-r,by),(335,by),(335,201),(ax,ay)],5:[(bx-r,by),(322,by),(322,108),(ax,ay)],6:[(bx-r,by),(360,by),(ax,ay)]}
            line=routes[a['number']]
        elif num=='07':line=[(bx,by-r),(bx,ay+8),(ax,ay)]
        elif bx<W/2:line=[(bx+r,by),(max(bx+r+2,ix-5),by),(ax,ay)]
        else:line=[(bx-r,by),(min(bx-r-2,ix+iw+5),by),(ax,ay)]
        c.setStrokeColorRGB(*GREY);c.setLineWidth(.55)
        p=c.beginPath();p.moveTo(*line[0])
        for xy in line[1:]:p.lineTo(*xy)
        c.drawPath(p)
        c.setFillColorRGB(*NAVY);c.circle(ax,ay,1.15,stroke=0,fill=1)
        c.circle(bx,by,r,stroke=0,fill=1);c.setFillColorRGB(1,1,1);c.setFont('Helvetica-Bold',10.5);c.drawCentredString(bx,by-3.6,str(a['number']))
        xy=' '.join(f'{x:.3f},{H-y:.3f}' for x,y in line)
        svg.append(f'<polyline points="{xy}" fill="none" stroke="#334752" stroke-width="0.55"/><circle cx="{ax:.3f}" cy="{H-ay:.3f}" r="1.15" fill="#062b3c"/><circle cx="{bx:.3f}" cy="{H-by:.3f}" r="7" fill="#062b3c"/>')
        svg.append(f'<text x="{bx:.3f}" y="{H-by+3.6:.3f}" fill="white" font-family="Arial,Helvetica,sans-serif" font-weight="700" font-size="10.5" text-anchor="middle">{a["number"]}</text>')
        circles.append((bx,by,r))
    for i,(x,y,r) in enumerate(circles):
        assert all(math.hypot(x-x2,y-y2)>r+r2+2 for x2,y2,r2 in circles[:i])
        assert y-r>legend_h
    # A fixed two-column 11-pt legend stays legible at the native print width.
    legend_rects=[]
    for i,a in enumerate(anchors):
        col=i%2;row=i//2;x=7+col*(W/2);y=legend_h-13-row*rowh
        c.setFillColorRGB(*NAVY);c.setFont('Helvetica-Bold',11);c.drawString(x,y,str(a['number']))
        c.setFont('Helvetica',11);c.drawString(x+13,y,a['label'])
        textw=stringWidth(a['label'],'Helvetica',11)
        assert textw+13<W/2-12,(stem,a['label'],textw)
        assert y>=3
        svg.append(svgtext(x,H-y,str(a['number']),11,True));svg.append(svgtext(x+13,H-y,a['label']))
        legend_rects.append([x,y-2,x+13+textw,y+11])
    c.showPage();c.save();svg.append('</svg>')
    (ROOT/(stem+'.svg')).write_text('\n'.join(svg),encoding='utf-8')
    doc=pdfium.PdfDocument(str(ROOT/(stem+'.pdf')));page=doc[0]
    page.render(scale=2600/W).to_pil().save(ROOT/(stem+'.png'))
    verification.append({'file':stem+'.pdf','page_points':[W,H],'legend_font_pt':11,'render_pixels':[2600,1750],'geometry_unchanged':rec['geometry_unchanged'],'jpeg_quality':96,'callouts':[{'number':a['number'],'label':a['label'],'anchor':[a['ax'],a['ay']],'circle':[a['bx'],a['by']]} for a in pts],'legend_rects':legend_rects})
    print('LABELED_FIGURE_READY',stem,flush=True)
if args.scenes and (ROOT/'label_layout_verification.json').exists():
    prior=json.loads((ROOT/'label_layout_verification.json').read_text())
    touched={v['file'] for v in verification}
    verification=sorted([v for v in prior if v['file'] not in touched]+verification,key=lambda v:v['file'])
(ROOT/'label_layout_verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
print('ALL_LABELED_FIGURES_READY',len(verification),flush=True)

