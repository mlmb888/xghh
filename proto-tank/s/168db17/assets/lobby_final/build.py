import numpy as np,json
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
from scipy import ndimage
A='/cursor/stores/store-007f6979-ce17-497b-be2a-e6a80b535532/grok-bot/agents/869d05f2-ebcd-4b95-8e2d-7db95bdf2cfe/attachments/'
S=2.5;W,H=360,640
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(pt):return ImageFont.truetype(FONT,round(pt*S),index=2)
NAVY=(14,26,58,238);LINE=(47,168,255,255);INK=(10,16,40,255);GOLD=(255,206,84,255);CY=(47,212,255,255)
L={'design_size_pt':[W,H],'export_scale':S,'grid_pt':8,'font':{'family':'Source Han Sans SC Bold / 思源黑体 Bold','file':'NotoSansCJK-Bold.ttc','license':'SIL OFL 1.1'},'layers':[],'texts':[]}
# ---- background (no UI)
bg=Image.open(A+'443726dcf0a5974ec3bca4b264cd63e9484ca9dd9247b92aed01b7a80fe74d13.jpg').convert('RGB')
a=np.array(bg).astype(float)/255;a=1-(1-a)**1.5
yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]];cx,cy=a.shape[1]*0.5,a.shape[0]*0.52
r=np.sqrt(((xx-cx)/(a.shape[1]*.42))**2+((yy-cy)/(a.shape[0]*.17))**2);sh=np.clip(1-0.25*np.exp(-r**2*1.2),0.7,1)[...,None]
bg=Image.fromarray((np.clip(a*sh,0,1)*255).astype(np.uint8)).resize((round(W*S),round(H*S)),Image.LANCZOS);bg.save('bg.png')
L['layers'].append(dict(name='bg',file='bg.png',x=0,y=0,w=W,h=H,z=0))
# ---- car layer
car=Image.open('../concept/v6/jeep_34.png').convert('RGBA')
cw=232;ch=round(cw*car.height/car.width);car=car.resize((round(cw*S),round(ch*S)),Image.LANCZOS)
c=np.array(car).astype(float);v=c[...,:3].max(-1,keepdims=True);c[...,:3]=np.clip(c[...,:3]*np.where(v<200,np.minimum(1.2,200/np.maximum(v,1)),1),0,255);car=Image.fromarray(c.astype(np.uint8),'RGBA')
_a=car.getchannel('A');car=ImageEnhance.Color(car.convert('RGB')).enhance(1.1).convert('RGBA');car.putalpha(_a)
car.save('car.png');cx0=(W-cw)//2;cy0=376-ch
L['layers'].append(dict(name='car',file='car.png',x=cx0,y=cy0,w=cw,h=ch,z=1,note='战车 3/4 展示图；与战斗 v6/jeep_top.png 同一设计'))
# ---- icons
ic=np.array(Image.open(A+'831033fdd1dd133b01a860823bc3f48215daaa81a77993ea14a6ebb5edf09aa7.jpg').convert('RGB')).astype(int)
g=(ic[...,1]-np.maximum(ic[...,0],ic[...,2])>50)&(ic[...,1]>120)
names=['gift','medal','calendar','megaphone','chest','mail','fuel','coin','diamond','core','shop','wrench','swords','house','bolt','plus']
cell=ic.shape[0]//4;icons={}
for i,n in enumerate(names):
  r_,c_=divmod(i,4);sl=(slice(r_*cell,(r_+1)*cell),slice(c_*cell,(c_+1)*cell))
  m=~g[sl];m=ndimage.binary_opening(m,iterations=2);lab,k=ndimage.label(m);sz=ndimage.sum(m,lab,range(1,k+1));m=np.isin(lab,1+np.where(sz>sz.max()*0.08)[0])
  rgb=ic[sl].copy();mx=np.maximum(rgb[...,0],rgb[...,2]);sp=rgb[...,1]>mx+10;rgb[...,1][sp]=mx[sp]+10
  im=Image.fromarray(rgb.astype(np.uint8)).convert('RGBA');im.putalpha(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.8)));im=im.crop(im.getbbox());icons[n]=im
def iconfit(n,pt):
  im=icons[n];k=pt*S/max(im.size);return im.resize((max(1,round(im.width*k)),max(1,round(im.height*k))),Image.LANCZOS)
# ---- component drawing helpers (all at 2.5x)
def panel(w,h,r=8,fill=NAVY,line=LINE,lw=1.5):
  im=Image.new('RGBA',(round(w*S),round(h*S)));d=ImageDraw.Draw(im);q=round(lw*S)
  d.rounded_rectangle((0,0,im.width-1,im.height-1),round(r*S),fill=INK);d.rounded_rectangle((q,q,im.width-1-q,im.height-1-q),round((r-1)*S),fill=fill,outline=line,width=q)
  d.line((round(r*S),q*2,im.width-round(r*S),q*2),fill=(255,255,255,40),width=q)
  return im
def comp(name,im,x,y,w,h,z=2,**kw):
  im.save('ui/'+name+'.png');L['layers'].append(dict(name=name,file='ui/'+name+'.png',x=x,y=y,w=w,h=h,z=z,**kw))
def text(id,s,x,y,pt,color,anchor='mm',stroke=None):
  L['texts'].append(dict(id=id,text=s,x=x,y=y,size_pt=pt,color='#%02X%02X%02X'%color[:3],anchor=anchor,stroke=stroke))
# avatar
av=Image.open(A+'6538919b65ef4ae293751c9df8862ff61eef4efb7574954064e2470b1e629dad.jpg').convert('RGB').crop((180,60,900,780)).resize((round(36*S),round(36*S)))
fr=panel(40,40,8);m=Image.new('L',av.size,0);ImageDraw.Draw(m).rounded_rectangle((0,0,av.width-1,av.height-1),round(6*S),fill=255);fr.paste(av,(round(2*S),round(2*S)),m)
comp('avatar_frame',fr,16,16,40,40)
lv=panel(24,12,4,fill=(10,40,90,255),line=CY,lw=1);comp('avatar_level_badge',lv,24,48,24,12,z=3);text('avatar_level','Lv.27',36,54,8,(255,255,255))
# currencies
cur=[('fuel','24/30'),('coin','18,640'),('diamond','320'),('core','35')]
for i,(n,val) in enumerate(cur):
  x=64+i*72;comp(f'currency_{n}_bg',panel(64,32,8),x,20,64,32)
  ii=iconfit(n,20);comp(f'icon_{n}',ii,x+4,26,round(ii.width/S),round(ii.height/S),z=3)
  if n!='fuel':
    p=iconfit('plus',14);comp(f'currency_{n}_plus',p,x+46,29,14,14,z=3)
  text(f'currency_{n}',val,x+26,36,9.5,(255,255,255),'lm',stroke='#0A1028 1pt')
# rescue banner
comp('rescue_banner_bg',panel(208,40,8),16,64,208,40)
bar=Image.new('RGBA',(round(176*S),round(8*S)));d=ImageDraw.Draw(bar);d.rounded_rectangle((0,0,bar.width-1,bar.height-1),round(4*S),fill=(20,40,80,255));comp('rescue_bar_track',bar,24,88,176,8,z=3)
fill=Image.new('RGBA',(round(176*S*.64),round(8*S)));ImageDraw.Draw(fill).rounded_rectangle((0,0,fill.width-1,fill.height-1),round(4*S),fill=CY);comp('rescue_bar_fill',fill,24,88,round(176*.64),8,z=4,note='宽度按进度缩放，0.64=3842/6000')
text('rescue_title','累计救援',24,76,8,(170,200,235),'lm');text('rescue_level','Lv.12 避难所',72,76,10,GOLD[:3],'lm',stroke='#0A1028 1pt');text('rescue_value','3,842 / 6,000 人',208,76,8,(255,255,255),'rm')
# side buttons
side=[('left',16,['gift','medal','calendar'],['首充','战令','签到']),('right',296,['megaphone','chest','mail'],['活动','宝箱','邮件'])]
for side_n,x,ics,labs in side:
  for j,(n,lab) in enumerate(zip(ics,labs)):
    y=112+j*72;comp(f'side_{side_n}_{j}_bg',panel(48,48,8),x,y,48,48)
    ii=iconfit(n,34);comp(f'icon_{n}',ii,x+24-round(ii.width/S/2),y+24-round(ii.height/S/2),round(ii.width/S),round(ii.height/S),z=3)
    text(f'side_{n}_label',lab,x+24,y+56,9,(255,255,255),stroke='#0A1028 1.2pt')
red=Image.new('RGBA',(round(10*S),)*2);ImageDraw.Draw(red).ellipse((0,0,red.width-1,red.height-1),fill=(240,60,50,255),outline=INK,width=3);comp('reddot',red,58,108,10,10,z=4)
# nameplate
comp('nameplate_bg',panel(184,40,8,line=(150,110,255,255)),88,384,184,40)
text('car_name','荒原铁犀 · 史诗 ★4',180,396,9.5,(220,205,255));dm=iconfit('diamond',10)
text('power_label','战力',150,413,8,(170,200,235));text('power_value','12,860',196,413,11,GOLD[:3],stroke='#0A1028 1pt')
# chapter card
comp('chapter_card_bg',panel(328,72,8),16,432,328,72)
th=Image.open('../concept/battle_v6.png').convert('RGB').crop((0,140,720,560)).resize((round(96*S),round(56*S)),Image.LANCZOS)
tf=Image.new('RGBA',(round(100*S),round(60*S)),INK);tf.paste(th,(round(2*S),round(2*S)));d=ImageDraw.Draw(tf);d.rectangle((0,0,tf.width-1,tf.height-1),outline=LINE,width=round(1.5*S))
comp('chapter_thumb',tf,40,438,100,60,z=3,note='章节缩略图，按章节替换')
for nm,xx,pts in [('chapter_arrow_l',20,[(14,0),(0,10),(14,20)]),('chapter_arrow_r',328,[(0,0),(14,10),(0,20)])]:
  im=Image.new('RGBA',(round(16*S),round(22*S)));ImageDraw.Draw(im).polygon([(round(px*S)+2,round(py*S)+2) for px,py in pts],fill=(140,210,255,255),outline=INK);comp(nm,im,xx-0 if nm.endswith('l') else xx-2,457,16,22,z=3)
text('chapter_title','第 3 章 · 死城加油站',152,456,12,(255,255,255),'lm',stroke='#0A1028 1pt');text('chapter_sub','救援目标 8 人   最高 2/3 波',152,482,8.5,(170,200,235),'lm')
# go button
gb=Image.new('RGBA',(round(328*S),round(56*S)));d=ImageDraw.Draw(gb)
d.rounded_rectangle((0,0,gb.width-1,gb.height-1),round(12*S),fill=INK)
for k in range(gb.height-12):
  t=k/(gb.height-12);col=(255,int(222-50*t),int(110-80*t),255);d.line((10,6+k,gb.width-10,6+k),fill=col)
mask=Image.new('L',gb.size,0);ImageDraw.Draw(mask).rounded_rectangle((6,6,gb.width-7,gb.height-7),round(10*S),fill=255)
base=Image.new('RGBA',gb.size);ImageDraw.Draw(base).rounded_rectangle((0,0,gb.width-1,gb.height-1),round(12*S),fill=INK);base.paste(gb,(0,0),mask)
ImageDraw.Draw(base).rounded_rectangle((round(10*S),round(5*S),gb.width-round(10*S),round(18*S)),round(6*S),fill=(255,245,200,90))
comp('go_button',base,16,512,328,56,z=2,note='最醒目元素')
fi=iconfit('fuel',20);comp('go_fuel_icon',fi,252,530,round(fi.width/S),round(fi.height/S),z=3)
text('go_label','出 发',164,540,24,(90,30,0));text('go_cost','-5',280,540,14,(90,30,0),'lm')
# tab bar
comp('tabbar_bg',panel(328,56,8),16,576,328,56)
tabs=[('shop','商店'),('wrench','战车改装'),('swords','出征'),('house','基地'),('bolt','天赋')]
for i,(n,lab) in enumerate(tabs):
  x=16+i*66;on=(n=='swords')
  if on:
    hl=panel(64,64,10,fill=(30,50,100,250),line=GOLD,lw=2);comp('tab_active_bg',hl,x+1,568,64,64,z=3)
  ii=iconfit(n,30 if on else 24);comp(f'tab_icon_{n}',ii,x+33-round(ii.width/S/2),(584 if on else 586),round(ii.width/S),round(ii.height/S),z=4)
  text(f'tab_{n}',lab,x+33,622,9 if not on else 10,GOLD[:3] if on else (220,230,245),stroke='#0A1028 1pt')
json.dump(L,open('layout.json','w'),ensure_ascii=False,indent=1)
# ---- compose final
out=Image.open('bg.png').convert('RGBA')
sh=Image.new('RGBA',out.size);ImageDraw.Draw(sh).ellipse((round(56*S),round(330*S),round(304*S),round(384*S)),fill=(20,14,8,150));out=Image.alpha_composite(out,sh.filter(ImageFilter.GaussianBlur(20)))
glow=Image.new('RGBA',out.size);ImageDraw.Draw(glow).rounded_rectangle((round(12*S),round(508*S),round(348*S),round(572*S)),round(14*S),fill=(255,180,40,150));out=Image.alpha_composite(out,glow.filter(ImageFilter.GaussianBlur(18)))
for ly in sorted(L['layers'],key=lambda l:l['z']):
  im=Image.open(ly['file']).convert('RGBA');out.alpha_composite(im,(round(ly['x']*S),round(ly['y']*S)))
d=ImageDraw.Draw(out)
for t in L['texts']:
  col=tuple(int(t['color'][i:i+2],16) for i in (1,3,5));sw=0
  if t['stroke']:sw=round(float(t['stroke'].split()[1][:-2])*S)
  d.text((round(t['x']*S),round(t['y']*S)),t['text'],font=F(t['size_pt']),fill=col,anchor=t['anchor'],stroke_width=sw,stroke_fill=(10,16,40))
out.convert('RGB').save('lobby_final.png')
# ---- grid check
gc=out.copy();d=ImageDraw.Draw(gc)
for x in range(0,W+1,8):d.line((x*S,0,x*S,H*S),fill=(255,0,255,60) if x%32 else (255,0,255,130),width=1)
for y in range(0,H+1,8):d.line((0,y*S,W*S,y*S),fill=(255,0,255,60) if y%32 else (255,0,255,130),width=1)
for x in (16,W-16):d.line((x*S,0,x*S,H*S),fill=(0,255,120,255),width=3)
for ly in L['layers'][1:]:
  d.rectangle((ly['x']*S,ly['y']*S,(ly['x']+ly['w'])*S,(ly['y']+ly['h'])*S),outline=(255,255,0,200),width=2)
fs=ImageFont.truetype(FONT,26,index=2)
for (x,y,s) in [(18,100,'边距16'),(300,100,'边距16'),(18,640*S-50,'卡片/按钮/底栏 左右均 16pt')]:d.text((x*S if x<300 else x*S,y if y>200 else y*S),s,font=fs,fill=(0,255,120))
d.text((cx0*S,(cy0-10)*S),f'战车 {cw}×{ch}pt 居中 x={cx0}',font=fs,fill=(255,255,0))
gc.convert('RGB').save('grid_check.png')
print(len(L['layers']),'layers',len(L['texts']),'texts',cx0,cy0,cw,ch)
