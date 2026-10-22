import json
from PIL import Image, ImageDraw, ImageFont
W,H,T=27,96,40
g=[['.']*W for _ in range(H)]
def rect(x0,y0,x1,y1,c):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1): g[y][x]=c
# outer ruins walls
rect(0,0,0,H-1,'#');rect(W-1,0,W-1,H-1,'#')
# main road (center) south->north
rect(11,0,15,95,'r')
# river row 70-72, single bridge at center x11-15
rect(1,70,25,72,'~');rect(11,70,15,72,'=')
# north river 2 (rows 30-31) bridges left x3-6 & right x20-23 only (fork forced)
rect(1,30,25,31,'~');rect(3,30,6,31,'=');rect(20,30,23,31,'=')
# central ruin block separating fork rows 33-62
rect(8,34,18,62,'#')
# left/right branch roads
rect(3,32,7,63,'r');rect(19,32,23,63,'r')
rect(3,63,23,66,'r');rect(3,28,23,29,'r')
# dead-end at south-west by river (old QA issue) blocked by building
rect(1,73,8,79,'#')
# boss arena plaza rows 4-18
rect(4,4,22,18,'p')
tiles=[''.join(r) for r in g]
objs={
"camps":[
 {"id":"A","x":19,"y":80,"w":4,"h":3,"survivors":7,"gate_hp":150,"guards":6,"note":"开局教学营地，出生点右前方"},
 {"id":"C","x":2,"y":45,"w":5,"h":4,"survivors":9,"gate_hp":300,"guards":14,"elites":2,"note":"左岔：人多危险"},
 {"id":"D","x":20,"y":50,"w":4,"h":3,"survivors":7,"gate_hp":200,"guards":8,"note":"右岔：人少+补给"},
 {"id":"E","x":3,"y":22,"w":4,"h":3,"survivors":7,"gate_hp":250,"guards":10},
 {"id":"F","x":20,"y":22,"w":4,"h":3,"survivors":7,"gate_hp":250,"guards":10,"miniboss":"mutant_chief"},
 {"id":"G","x":12,"y":20,"w":3,"h":3,"survivors":7,"gate_hp":300,"guards":12,"note":"Boss 场前最后一营"}],
"helipads":[
 {"id":"H1","x":13,"y":67,"r":2,"type":"mid","note":"过桥后中途送人点，不限时"},
 {"id":"H2","x":13,"y":2,"r":2,"type":"final","countdown_s":60,"note":"Boss 死后或 T=180s 起直升机倒计时"}],
"spawners":[
 {"id":"horde_S","x":13,"y":95,"type":"chase_horde","start_s":35,"interval_s":4,"count":6,"speed_ratio":0.85,"note":"追击尸潮，从南沿主路推进"},
 {"id":"sp_L","x":2,"y":40,"type":"ambush","trigger":"tr_left","count":12},
 {"id":"sp_R","x":24,"y":56,"type":"ambush","trigger":"tr_right","count":6},
 {"id":"sp_N","x":13,"y":26,"type":"wave","start_s":120,"interval_s":6,"count":8}],
"enemies":[
 {"id":"elite1","type":"elite","x":5,"y":43},{"id":"elite2","type":"elite","x":5,"y":52},
 {"id":"chief","type":"mutant_chief","x":21,"y":25,"hp":1200},
 {"id":"boss","type":"giant_mutant","x":13,"y":10,"arms":2,"spawn":"tr_boss"}],
"obstacles":[
 {"type":"wreck_car","x":12,"y":86,"w":2,"h":1},{"type":"wreck_car","x":15,"y":60,"w":2,"h":1},
 {"type":"wreck_bus","x":4,"y":57,"w":3,"h":1,"note":"左岔窄口，过车需贴墙滑"},
 {"type":"barricade","x":11,"y":69,"w":5,"h":1,"hp":80,"note":"桥南路障，开局第一个可打破物"},
 {"type":"barricade","x":19,"y":32,"w":5,"h":1,"hp":120},
 {"type":"barricade","x":3,"y":32,"w":5,"h":1,"hp":120},
 {"type":"fuel_barrel","x":4,"y":48,"w":1,"h":1,"blast_r":2,"count_hint":"左营地周围3个"},
 {"type":"fuel_barrel","x":6,"y":44,"w":1,"h":1,"blast_r":2},{"type":"fuel_barrel","x":3,"y":50,"w":1,"h":1,"blast_r":2},
 {"type":"debris","x":17,"y":14,"w":2,"h":2},{"type":"debris","x":7,"y":8,"w":2,"h":2}],
"pickups":[
 {"type":"supply_crate","x":21,"y":44,"gives":"repair_50%+free_card"},
 {"type":"supply_crate","x":21,"y":58,"gives":"ammo_burst_10s"}],
"triggers":[
 {"id":"tr_intro","x":11,"y":88,"w":5,"h":4,"on_enter":"hint_arrow:A"},
 {"id":"tr_bridge","x":11,"y":72,"w":5,"h":2,"on_enter":"hint:过桥北上"},
 {"id":"tr_left","x":3,"y":60,"w":5,"h":2,"on_enter":"spawn:sp_L;banner:左路 人多·危险"},
 {"id":"tr_right","x":19,"y":60,"w":5,"h":2,"on_enter":"spawn:sp_R;banner:右路 补给"},
 {"id":"tr_boss","x":4,"y":18,"w":19,"h":1,"on_enter":"spawn:boss;lock_camera_y:4-18"}],
"card_pickups":{"rule":"每交付/击杀累计经验满即三选一","target_times":[30,70,110,150,185]}
}
lvl={"id":"1-1","tile_pt":T,"cols":W,"rows":H,"origin":"左上(0,0)，y向南增大；出生点在南端","spawn":{"x":13,"y":92,"face":"N"},
"legend":{".":"废城地面 可走","r":"柏油路 可走","p":"广场 可走","#":"楼体/墙 不可走 沿墙滑","~":"河 不可走","=":"桥 可走"},
"capacity":30,"total_survivors":44,"stars_pct":[55,82,95],"stars_count":[25,37,42],
"time_limit_s":240,"tiles":tiles,**objs}
json.dump(lvl,open('level_1_1.json','w'),ensure_ascii=False,indent=1)
# png
S=10;img=Image.new('RGB',(W*S+260,H*S),'white');d=ImageDraw.Draw(img)
col={'.':(222,214,196),'r':(150,150,150),'p':(190,180,160),'#':(80,70,70),'~':(90,150,220),'=':(170,120,70)}
for y in range(H):
  for x in range(W): d.rectangle([x*S,y*S,x*S+S-1,y*S+S-1],fill=col[g[y][x]])
try: f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',11)
except: f=ImageFont.load_default()
for c in objs['camps']:
  d.rectangle([c['x']*S,c['y']*S,(c['x']+c['w'])*S,(c['y']+c['h'])*S],fill=(230,120,40),outline='black');d.text((c['x']*S,c['y']*S-12),f"{c['id']}:{c['survivors']}人",fill='black',font=f)
for h in objs['helipads']:
  d.ellipse([(h['x']-2)*S,(h['y']-2)*S,(h['x']+2)*S,(h['y']+2)*S],outline=(240,200,0),width=3);d.text((h['x']*S+22,h['y']*S),h['id'],fill='black',font=f)
for e in objs['enemies']:
  r=2 if e['type']=='giant_mutant' else 1;d.ellipse([(e['x']-r)*S,(e['y']-r)*S,(e['x']+r)*S,(e['y']+r)*S],fill=(200,0,0));d.text((e['x']*S+12,e['y']*S),e['id'],fill='red',font=f)
for o in objs['obstacles']: d.rectangle([o['x']*S,o['y']*S,(o['x']+o['w'])*S-1,(o['y']+o['h'])*S-1],fill=(40,40,40) if o['type']!='fuel_barrel' else (255,60,0))
for p in objs['pickups']: d.rectangle([p['x']*S,p['y']*S,p['x']*S+9,p['y']*S+9],fill=(0,180,0))
for s in objs['spawners']: d.polygon([(s['x']*S,s['y']*S-6),(s['x']*S-6,s['y']*S+6),(s['x']*S+6,s['y']*S+6)],fill=(120,0,160))
sx,sy=13*S,92*S;d.ellipse([sx-6,sy-6,sx+6,sy+6],fill=(0,90,255));d.text((sx+10,sy),'出生',fill='blue',font=f)
for y in range(0,H,16): d.line([0,y*S,W*S,y*S],fill=(0,0,0)); d.text((2,y*S+2),f'屏{6-y//16}',fill='black',font=f)
L=["图例(1格=40pt,1屏=9x16格)","深灰=楼体/墙  蓝=河  棕=桥","灰=路  橙=营地(人数)","黄圈=接应点 H1中途 H2终点","红点=精英/头目/Boss","紫三角=刷怪点  绿=补给箱","黑=废车/路障/碎石 橙红=油桶","","路线: 出生→A营→桥→H1","→左岔C(9人,2精英,油桶)","  或右岔D(7人,2补给箱)","→北河双桥→E/F(头目)/G","→Boss广场→H2撤离(60s)","尸潮35s起从南追"]
for i,t in enumerate(L): d.text((W*S+10,10+i*18),t,fill='black',font=f)
img.save('map_p0.png')
