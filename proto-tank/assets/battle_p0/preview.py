import json
from PIL import Image,ImageDraw,ImageFont
M=json.load(open('manifest.json'))['assets'];k=0.8
bg=Image.open('/cursor/stores/store-007f6979-ce17-497b-be2a-e6a80b535532/grok-bot/agents/869d05f2-ebcd-4b95-8e2d-7db95bdf2cfe/attachments/912c7b27190be98c480ec0e96cdebc0d0de4819da904af80bf3ad2521a665369.jpg').convert('RGB').resize((720,1280)).convert('RGBA')
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',18,index=2)
c=bg.copy();d=ImageDraw.Draw(c)
d.rectangle((0,0,720,1280),fill=None)
# panel overlay to clear UI area: darken lower-left area for showcase
def P(f,x,y,anchor=None):
  im=Image.open(f).convert('RGBA');im=im.resize((round(im.width*k),round(im.height*k)),Image.LANCZOS)
  ax,ay=(anchor if anchor else (im.width//2,im.height//2));c.alpha_composite(im,(int(x-ax*k) if anchor else int(x-ax),int(y-ay*k) if anchor else int(y-ay)));return im
# assembled jeep
body=M['jeep_body.png'];bx,by=360,900
bim=Image.open('jeep_body.png');P('jeep_body.png',bx,by)
ox,oy=bx-bim.width*k/2,by-bim.height*k/2
def mount(f,hp,rot=0):
  im=Image.open(f).convert('RGBA');piv=M[f]['anchor_pivot']
  if rot:im=im.rotate(rot,expand=False,center=tuple(piv))
  im=im.resize((round(im.width*k),round(im.height*k)),Image.LANCZOS)
  x,y=body['hardpoints'][hp];c.alpha_composite(im,(int(ox+x*k-piv[0]*k),int(oy+y*k-piv[1]*k)))
mount('jeep_turret.png','roof');mount('mount_rocket_pod.png','left');mount('mount_side_cannon.png','right');mount('mount_flamethrower.png','rear',180)
d.text((250,1080),'组装：车顶机枪+左火箭巢+右侧炮+尾喷火',font=F,fill='white',stroke_width=3,stroke_fill=(16,18,42))
# loose mounts row
x=230
for f in ['mount_twin_mg.png','mount_rocket_pod.png','mount_flamethrower.png','mount_side_cannon.png']:
  im=P(f,x+30,1180);x+=80
# zombies & survivor frames
y=470
for pref in ['zombie_walker','zombie_fatty','zombie_runner','survivor_run']:
  for i in range(4):P(f'{pref}_{i}.png',300+i*70,y)
  y+=95
c.convert('RGB').save('batch1_preview.png')
