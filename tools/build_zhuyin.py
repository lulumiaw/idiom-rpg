# -*- coding: utf-8 -*-
"""成語神話卷軸：注音字型建置工具
用法：python3 tools/build_zhuyin.py [字型資料夾，內含 BpmfIansui-Regular.ttf 與 BpmfZihiKaiStd-Regular.ttf]
 1. 掃描 index.html 內所有中文字串，用 pypinyin 判斷多音字讀音，對應到字型的異體字選擇子，寫回 index.html 的 VSM 表。
 2. （有給字型資料夾時）把兩款字型裁成 Big5 常用字＋遊戲用字的 woff2，放到 fonts/。
需要：pip install pypinyin fonttools brotli"""
import re,sys,os
from fontTools.ttLib import TTFont
from pypinyin import lazy_pinyin,Style
here=os.path.dirname(os.path.abspath(__file__));root=os.path.dirname(here)
html_p=os.path.join(root,'index.html');html=open(html_p,encoding='utf-8').read()
fdir=next((a for a in sys.argv[1:] if not a.startswith('--')),None)
FONTS={'fonts/BpmfIansui.woff2':'BpmfIansui-Regular.ttf','fonts/BpmfZihiKai.woff2':'BpmfZihiKaiStd-Regular.ttf'}
def altmap(path):
    f=TTFont(path);g=f['glyf'];m={}
    for n in f.getGlyphOrder():
        k=re.match(r'^uni([0-9A-F]{4,5})\.ss(\d\d)$',n)
        if not k or k.group(2)=='00':continue
        gl=g[n]
        if gl.isComposite() and gl.components[0].glyphName.startswith('z_'):
            m.setdefault(chr(int(k.group(1),16)),{})[gl.components[0].glyphName[2:]]=int(k.group(2))
    return m
src=fdir or '/mnt/skills/plugins/comic-poem-worksheet-generator/assets/fonts/zhuyin'
A=altmap(os.path.join(src,'BpmfIansui-Regular.ttf'));Z=altmap(os.path.join(src,'BpmfZihiKaiStd-Regular.ttf'))
def vs(c,r):
    r=r.replace('ü','v')
    i=A.get(c,{}).get(r)
    return chr(0xE01E0+i) if i and Z.get(c,{}).get(r)==i else ''   # 兩款字型索引一致才插入
HAN=re.compile(r'[\u4e00-\u9fff]+')
# 人工校正表：tools/zhuyin_fixes.txt，每行「詞語 字=拼音」（拼音用數字調，如 sheng1），優先於自動判斷
FIXES=[]
fp=os.path.join(here,'zhuyin_fixes.txt')
if os.path.exists(fp):
    for ln in open(fp,encoding='utf-8'):
        ln=ln.split('#')[0].split()
        if len(ln)>=2:FIXES.append((ln[0],[(ln[0].index(x.split('=')[0]),x.split('=')[1]) for x in ln[1:]]))
ORD=set('第初十百千萬零〇唯統之')   # 這些字後面的「一」是序數／數字，唸原調 ㄧ
def tone(p):return int(p[-1]) if p[-1].isdigit() else 5
def rules(run,py):
    """依教育部國語辭典的變調標示調整：一、不 的變調，以及「不勝」的勝(ㄕㄥ)。"""
    py=list(py)
    for w,fx in FIXES:
        for m in re.finditer(re.escape(w),run):
            for off,pp in fx:py[m.start()+off]=pp
    for i,c in enumerate(run):
        if c=='勝' and i and run[i-1]=='不':py[i]='sheng1'
    base=list(py)
    t=lambda j:1 if run[j]=='一' else 4 if run[j]=='不' else tone(base[j])
    for i,c in enumerate(run):
        nxt=i+1<len(run)
        if c=='一':
            py[i]='yi1' if (not nxt or (i and run[i-1] in ORD)) else ('yi2' if t(i+1)==4 else 'yi4')
        elif c=='不' and base[i] in('bu4','bu2'):
            py[i]='bu2' if nxt and t(i+1)==4 else 'bu4'
    return py
def conv(s):
    def f(m):
        run=m.group(0);py=lazy_pinyin(run,style=Style.TONE3,neutral_tone_with_five=True,v_to_u=False)
        if len(py)!=len(run):return run
        py=rules(run,py)
        return ''.join(c+vs(c,p) for c,p in zip(run,py))
    return HAN.sub(f,s)
body=html[html.index('<script>'):]
body=re.sub(r'/\*VSM_BEGIN\*/.*?/\*VSM_END\*/','',body,flags=re.S)   # 不要把上一次產生的讀音表當成原文
strs={p for m in re.findall(r'"([^"\n`]*[\u4e00-\u9fff][^"\n`]*)"',body) if '$' not in m and '<' not in m for p in m.split('{n}') if HAN.search(p)}
strs|={p for m in re.findall(r'[\u4e00-\u9fff][\u4e00-\u9fff，。！？、：；「」『』（）…]*',body) for p in m.split('{n}') if HAN.search(p)}  # 連介面文字（樣板字串內的中文）也一併處理
vsm={s:conv(s) for s in strs}
vsm={k:v for k,v in vsm.items() if k!=v}
js='{'+','.join('"%s":"%s"'%(k,''.join('\\u{%x}'%ord(c) if ord(c)>=0xE0100 else c for c in v)) for k,v in sorted(vsm.items()))+'}'
html=re.sub(r'/\*VSM_BEGIN\*/.*?/\*VSM_END\*/',lambda m:'/*VSM_BEGIN*/const VSM='+js+';/*VSM_END*/',html,flags=re.S)
open(html_p,'w',encoding='utf-8').write(html)
print('VSM 條目',len(vsm))
if fdir or '--fonts' in sys.argv:
    from fontTools import subset
    os.makedirs(os.path.join(root,'fonts'),exist_ok=True)
    cs=set(chr(i) for i in range(0x20,0x7f))|set(chr(i) for i in range(0x3000,0x3040))|set(chr(i) for i in range(0xFF00,0xFFF0))|set(c for c in html if ord(c)>0x7f and ord(c)<0xE000)
    for b in (range(0xA4,0xC7),):
        for a in b:
            for t in range(0x40,0xFF):
                try:cs.add(bytes([a,t]).decode('big5'))
                except:pass
    uni=sorted(ord(c) for c in cs)+list(range(0xE01E0,0xE01F0))
    for out,fn in FONTS.items():
        o=subset.Options();o.layout_features=['*'];o.flavor='woff2';o.notdef_outline=True;o.name_IDs=['*'];o.glyph_names=True
        f=TTFont(os.path.join(src,fn));s=subset.Subsetter(o);s.populate(unicodes=uni);s.subset(f)
        f.flavor='woff2';f.save(os.path.join(root,out));print(out,os.path.getsize(os.path.join(root,out))//1024,'KB')
