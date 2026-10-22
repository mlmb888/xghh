import numpy as np,json
from PIL import Image,ImageFilter,ImageOps
from scipy import ndimage
A='/cursor/stores/store-007f6979-ce17-497b-be2a-e6a80b535532/grok-bot/agents/869d05f2-ebcd-4b95-8e2d-7db95bdf2cfe/attachments/'
S=2.5
def key(h):
  j=np.array(Image.open(A+h+'.jpg').convert('RGB')).astype(int)
  g=(j[...,1]-np.maximum(j[...,0],j[...,2])>40)&(j[...,1]>100)
  a=ndimage.binary_opening(~g,iterations=1)
  rgb=j.copy();mx=np.maximum(rgb[...,0],rgb[...,2]);sp=rgb[...,1]>mx+5;rgb[...,1][sp]=mx[sp]+5
  return rgb.astype(np.uint8),a
def comps(a,minsz=2000):
  lab,n=ndimage.label(a);out=[]
  for i,s in enumerate(ndimage.find_objects(lab)):
    m=lab[s]==i+1
    if m.sum()>=minsz:out.append((s,m))
  return out
def rgba(rgb,a,sl=None):
  al=Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6))
  im=Image.fromarray(rgb).convert('RGBA');im.putalpha(al)
  return im
def fit(im,h):return im.resize((max(1,round(im.width*h/im.height)),h),Image.LANCZOS)
M={'scale':2.5,'note':'显示尺寸单位 pt(逻辑像素,设计宽 360)；原图=显示×2.5；锚点为原图像素坐标(x右,y下)','assets':{}}
# --- jeep body
rgb,a=key('7b280d9739e281ed5dbd0025244cc471110e3779e3f8138ef91add329db6e2c1')
lab,n=ndimage.label(a);sz=ndimage.sum(a,lab,range(1,n+1));a=ndimage.binary_fill_holes(lab==1+np.argmax(sz))
body=rgba(rgb,a);bb=body.getbbox();body=body.crop(bb);H=round(165*S);sc=H/body.height;body=fit(body,H);body.save('jeep_body.png')
W=body.width
# roof ring center in source ~ (288,690) of 576x1024 grid -> image is maybe 720x1280
sw,sh=Image.open(A+'7b280d9739e281ed5dbd0025244cc471110e3779e3f8138ef91add329db6e2c1.jpg').size
rx,ry=288/576*sw,690/1024*sh
roof=[round((rx-bb[0])*sc),round((ry-bb[1])*sc)]
hp={'roof':roof,'front':[W//2,round(H*0.06)],'left':[round(W*0.08),round(H*0.45)],'right':[round(W*0.92),round(H*0.45)],'rear':[W//2,round(H*0.9)]}
M['assets']['jeep_body.png']=dict(size=[W,H],display=[round(W/S),round(H/S)],frames=1,anchor_pivot=[W//2,H//2],hardpoints=hp,facing='up',lighting='flat')
# --- mounts
rgb,a=key('951ad0a63bff30aba4c77946d850aa2a4d5632a49b178c5227824942ad5ee41d')
cs=sorted(comps(a,3000),key=lambda c:c[0][1].start)
cs=[c for c in cs if (c[0][0].stop-c[0][0].start)>150][:4]
names=['mount_twin_mg','mount_rocket_pod','mount_flamethrower','mount_side_cannon']
disp={'mount_twin_mg':40,'mount_rocket_pod':36,'mount_flamethrower':40,'mount_side_cannon':48}
for nm,(s,m) in zip(names,cs):
  sub=np.zeros_like(a);sub[s]=m
  im=rgba(rgb,sub).crop((s[1].start,s[0].start,s[1].stop,s[0].stop))
  h=round(disp[nm]*S);im=fit(im,h);im.save(nm+'.png')
  mk=np.array(im)[...,3]>128;ys,xs=np.nonzero(mk[int(h*.45):]);piv=[int(xs.mean()),int(ys.mean()+h*.45)]
  M['assets'][nm+'.png']=dict(size=list(im.size),display=[round(im.width/S),round(im.height/S)],frames=1,anchor_pivot=piv,muzzle=[im.width//2,int(np.nonzero(mk.any(1))[0][0])],facing='up',mount_on=('roof' if nm=='mount_twin_mg' else ('left/right' if nm=='mount_side_cannon' else 'roof/left/right/rear')))
import shutil;shutil.copy('mount_twin_mg.png','jeep_turret.png')
M['assets']['jeep_turret.png']=dict(M['assets']['mount_twin_mg.png']);M['assets']['jeep_turret.png']['note']='默认炮塔层=双管机枪；pivot 对齐 jeep_body hardpoints.roof'
# --- sequence frames
def seq(h,rows,prefix_list,disp_h,fix=None):
  rgb,a=key(h);cs=comps(a,1500)
  # group by row using y centers
  cs=sorted(cs,key=lambda c:(c[0][0].start+c[0][0].stop)/2)
  ys=np.array([(c[0][0].start+c[0][0].stop)/2 for c in cs]);
  groups=[];cur=[cs[0]]
  for c,y,yp in zip(cs[1:],ys[1:],ys[:-1]):
    if y-yp>60:groups.append(cur);cur=[c]
    else:cur.append(c)
  groups.append(cur)
  for gi,(g,pref) in enumerate(zip(groups,prefix_list)):
    g=sorted(g,key=lambda c:c[0][1].start)[:4]
    fr=[]
    for s,m in g:
      sub=np.zeros_like(a);sub[s]=m;im=rgba(rgb,sub).crop((s[1].start,s[0].start,s[1].stop,s[0].stop));fr.append(im)
    if fix and gi in fix:fr[3]=ImageOps.mirror(fr[1])
    while len(fr)<4:fr.append(ImageOps.mirror(fr[len(fr)-2]))
    # uniform scale by median height
    hs=sorted(f.height for f in fr);k=round(disp_h*S)/hs[len(hs)//2]
    fr=[f.resize((round(f.width*k),round(f.height*k)),Image.LANCZOS) for f in fr]
    # align: x by head/torso centroid (top 45%), y by bottom
    cw=max(f.width for f in fr)+16;ch=max(f.height for f in fr)+8
    cw+=cw%2;out=[]
    for i,f in enumerate(fr):
      al=np.array(f)[...,3]>128;top=al[:int(f.height*.45)];cx=np.nonzero(top)[1].mean()
      c=Image.new('RGBA',(cw,ch));x=round(cw/2-cx);y=ch-4-f.height;c.alpha_composite(f,(max(0,x),y));c.save(f'{pref}_{i}.png');out.append(c)
    strip=Image.new('RGBA',(cw*4,ch));[strip.alpha_composite(o,(i*cw,0)) for i,o in enumerate(out)];strip.save(f'{pref}_strip.png')
    M['assets'][f'{pref}_[0-3].png']=dict(size=[cw,ch],display=[round(cw/S),round(ch/S)],frames=4,fps=8,anchor_pivot=[cw//2,ch-6],note='脚底中心为锚点；四帧同尺寸，躯干中心对齐',strip=f'{pref}_strip.png')
seq('004865d29e991c4cb2c1f2a22aa77897be76dc0164feb3a65f31021a5fcec9f8',3,['zombie_walker','zombie_fatty','zombie_runner'],40,fix={2})
seq('ad89a6f8cc2330c43c2174aa3a10e14dd6b170cbb965cc747e866f13597d2869',1,['survivor_run'],36)
json.dump(M,open('manifest.json','w'),ensure_ascii=False,indent=1)
for k,v in M['assets'].items():print(k,v['size'],v['display'],v.get('frames'))
