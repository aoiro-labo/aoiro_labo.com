# 記事カバー画像ジェネレータ
# 使い方: リポジトリ直下で  python tools/generate_cover.py content/posts/<記事>.md [複数可]
# front matter の cover_keyword（最強調・白で最大）/ cover_emphasis（アクセント色）/
# cover_image（auto=本文画像から自動選択 / none / URL・パス指定）を読み、
# static/images/cover-<slug>.jpg を生成する。cover: の指定自体は front matter に書いておくこと。

import sys, os, re
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\aoiro\aoiro-labo")
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

def fm_of(path):
    t=open(path,encoding='utf-8').read()
    fm=t.split('---')[1]
    g=lambda pat: (re.search(pat, fm).group(1).strip() if re.search(pat, fm) else '')
    title=g(r'title:\s*"?([^"\n]+)')
    def list_of(key):
        m=re.search(key + r':\s*\[([^\]]*)\]', fm)
        if m:
            return [x.strip().strip('"').strip("'") for x in m.group(1).split(',') if x.strip()]
        b=re.findall(key + r':\s*\n((?:\s*-\s*.+\n)+)', fm)
        if b:
            return [x.strip().strip('"') for x in re.findall(r'-\s*"?([^"\n]+)', b[0])]
        return []
    _cl=list_of('categories'); cat=_cl[0] if _cl else ''
    tags=list_of('tags')
    kw=g(r'cover_keyword:\s*"?([^"\n]+)')
    emph=list_of('cover_emphasis')
    cimg=g(r'cover_image:\s*"?([^"\n]+)')
    slug=g(r'slug:\s*"?([^"\n]+)')
    return title, cat, tags, kw, emph, cimg, slug

BOLD=r"C:\Windows\Fonts\YuGothB.ttc"
REG=r"C:\Windows\Fonts\YuGothM.ttc"
FONT_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
ZEN_MAP={"Regular":"ZenKakuGothicNew-Regular.ttf","Medium":"ZenKakuGothicNew-Medium.ttf","SemiBold":"ZenKakuGothicNew-Medium.ttf","Bold":"ZenKakuGothicNew-Bold.ttf"}
def cover_font(weight, size):
    p = os.path.join(FONT_DIR, ZEN_MAP[weight])
    if os.path.exists(p):
        return ImageFont.truetype(p, size)
    return ImageFont.truetype(BOLD if weight in ("Bold", "SemiBold") else REG, size)

def draw_semi(img, pos, text, size, fill, baseline=False):
    # fabricated SemiBold: supersample the Medium mask and dilate it halfway toward Bold
    ss=4
    f=cover_font("Medium", size*ss)
    w=int(f.getlength(text))+4*ss
    h=size*2*ss
    mask=Image.new('L', (w, h), 0)
    md=ImageDraw.Draw(mask)
    if baseline:
        md.text((2*ss, size*ss), text, font=f, fill=255, anchor='ls')
    else:
        md.text((2*ss, 0), text, font=f, fill=255)
    r=max(1, round(size*0.03))
    mask=mask.filter(ImageFilter.MaxFilter(2*r+1))
    mask=mask.resize((w//ss, h//ss), Image.LANCZOS)
    layer=Image.new('RGB', mask.size, fill)
    if baseline:
        img.paste(layer, (int(pos[0])-2, int(pos[1])-size), mask)
    else:
        img.paste(layer, (int(pos[0])-2, int(pos[1])), mask)
W,H=1200,630
MARGIN=64
WHITE=(248,250,252)
BASE=(240,244,248)
SUBC=(196,205,219)
CAT_COLORS={'開発':(168,140,250),'雑記':(246,173,58)}
PALETTE=[(64,178,250),(52,211,153),(251,113,133),(96,165,250),(232,121,249)]
def accent_for(cat):
    if cat in CAT_COLORS: return CAT_COLORS[cat]
    return PALETTE[sum(cat.encode('utf-8')) % len(PALETTE)] if cat else PALETTE[0]

PARTICLES=set('はがをにへとのもや')
CONJ={'そして','しかし','だから','でも','また','なお','すると','ただ'}
AUX={'だった','でした','です','ます','ました','ない','なかった','でしょう','だろう','らしい','みたい','そう','たい'}
COMPOUND={'による','により','によって','について','にたいして','として','ごとに','にかけて','にわたって'}
NOSPLIT_END=('ごと','こと','もの','とき','ところ','ため','はず','まま','だけ','ほど','くらい','ぐらい','など','わけ','かた')

def tokenize(text):
    atoms=[]; i=0; n=len(text)
    while i<n:
        ch=text[i]
        if ch=='「':
            j=text.find('」', i)
            if j!=-1 and j-i<=14:
                seg=text[i:j+1]
                if j+1<n and text[j+1] in 'はがをにへとのもや': seg+=text[j+1]; j+=1
                atoms.append(seg); i=j+1; continue
        if ch=='(':
            j=text.find(')', i)
            if j!=-1 and j-i<=18:
                seg=text[i:j+1]
                if j+1<n and text[j+1] in 'はがをにへとのもや': seg+=text[j+1]; j+=1
                atoms.append(seg); i=j+1; continue
        if re.match(r'[A-Za-z0-9#@]', ch):
            j=i
            while j<n and re.match(r'[A-Za-z0-9#@]', text[j]): j+=1
            atoms.append(text[i:j]); i=j; continue
        if re.match(r'[ァ-ヶー]', ch):
            j=i
            while j<n and re.match(r'[ァ-ヶー]', text[j]): j+=1
            atoms.append(text[i:j]); i=j; continue
        j=i; buf=''
        while j<n:
            c=text[j]; buf+=c; j+=1
            if c in 'はがをにへとのもや、。・：:！？!?': break
            if len(buf)>=12: break
            if j<n and (text[j] in '「(' or re.match(r'[A-Za-z0-9#@ァ-ヶー]', text[j])): break
        atoms.append(buf); i=j
    merged=[]
    for a in atoms:
        if merged and a==' ': merged[-1]+=a
        else: merged.append(a)
    out=[]
    for a in merged:
        if a=='' : continue
        if len(a)>1 and a.endswith('：'):
            out.append(a[:-1]); out.append('：')
        else:
            out.append(a)
    return out

def split_brackets(atoms):
    out=[]
    for a in atoms:
        while a.startswith('【') and '】' in a:
            k=a.index('】')+1
            out.append((a[:k],'sub'))
            a=a[k:]
            if not a: break
        if a: out.append((a,None))
    return out

def merge_compounds(atoms):
    out=[]; i=0
    while i<len(atoms):
        a=atoms[i]
        if i+1<len(atoms):
            b=atoms[i+1]
            cand=a+b
            steal = (b=='に' and i+2<len(atoms) and atoms[i+2].startswith('よ'))
            if (cand in COMPOUND or (a=='に' and b.startswith('よ')) or (a.endswith('ごと') and b=='に' and not steal) or (a=='に' and b.startswith('つい')) or (a=='と' and b.startswith('して'))):
                out.append(cand); i+=2; continue
        out.append(a); i+=1
    return out

def classify(atoms, emph, hero):
    # returns list of (text, cls): cls in base/sub/accent/hero ; glue=True means a line must not start with it
    atoms = split_brackets(merge_compounds(atoms))
    out=[]
    def emit(text, cls, glue=False):
        if text: out.append((text, cls, glue))
    for a, forced in atoms:
        if forced=='sub':
            emit(a,'sub'); continue
        if a=='：':
            emit(a,'sub',glue=True); continue
        if a.endswith(' ') and a.strip() and all(ch in PARTICLES for ch in a.strip()):
            emit(a,'sub',glue=True); continue
        if a in COMPOUND:
            emit(a,'sub',glue=True); continue
        _pref = next((c for c in COMPOUND if a.startswith(c) and len(a)>len(c)), None)
        if _pref:
            emit(_pref,'sub',glue=True)
            a = a[len(_pref):]
            if a in emph:
                emit(a,'accent'); continue
            if len(a)>1 and a[-1] in PARTICLES and not a.endswith(NOSPLIT_END):
                emit(a[:-1],'base'); emit(a[-1],'sub',glue=True); continue
            emit(a,'base'); continue
        if a and all(ch in PARTICLES for ch in a):
            emit(a,'sub',glue=True); continue
        core = a[1:-1] if len(a)>=2 and ((a[0]=='\u300c' and a[-1]=='\u300d') or (a[0]=='\u300e' and a[-1]=='\u300f')) else a
        if a==hero or (core!=a and core==hero):
            emit(a,'hero'); continue
        if a in emph or (core!=a and core in emph):
            emit(a,'accent'); continue
        if a.startswith('('):
            k=a.find(')')
            emit(a[:k+1],'sub')
            rest=a[k+1:]
            if rest: emit(rest,'sub',glue=True)
            continue
        if a in CONJ or a in AUX:
            emit(a,'sub',glue=True); continue
        if len(a)>1 and a[-1] in PARTICLES and not a.endswith('から') and not a.endswith(NOSPLIT_END) and not a.endswith('ごとに'):
            emit(a[:-1],'base'); emit(a[-1],'sub',glue=True); continue
        emit(a,'base')
    out=[(t,c,(g or (t and t[0] in '」）)'))) for (t,c,g) in out]
    return out

def split_emph(atoms, emph, hero):
    targets=[e for e in emph+[hero] if e]
    out=[]
    for a in atoms:
        rest=a
        while rest:
            hit=None
            for e in targets:
                if e in rest: hit=e; break
            if not hit: out.append(rest); break
            pre,_,post = rest.partition(hit)
            if pre.endswith('「') and post.startswith('」'):
                pre=pre[:-1]; post=post[1:]; hit='「'+hit+'」'
            if pre: out.append(pre)
            out.append(hit); rest=post
    return out

def layout(items, widths, maxw, maxlines, balance_last=False, min_fill=0.0):
    n=len(items)
    INF=float('inf')
    from functools import lru_cache
    @lru_cache(maxsize=None)
    def solve(i, k):
        if i==n: return (0, [])
        if k==0: return (INF, None)
        best=(INF, None); w=0
        for j in range(i, n):
            w+=widths[j]
            if w>maxw and j>i: break
            line=items[i:j+1]
            if j<n-1:
                if items[j+1][2]:  # next is glue: cannot break here
                    continue
                if items[j][0].endswith(('・','･')):  # never break right after a nakaguro
                    continue
                slack=maxw-w
                cost=slack*slack/700.0
                if items[j][0]=='：': cost-=250
                if min_fill and w < maxw*min_fill: cost+=400
                rc, rest = solve(j+1, k-1)
                if rest is None: continue
                cand=(cost+rc, [line]+rest)
            else:
                c=(maxw-w)*0.25
                if balance_last:
                    c=(maxw-w)*1.15
                    if len(line)==1 and n>1: c+=500
                cand=(c, [line])
            if cand[0]<best[0]: best=cand
        return best
    return solve(0, maxlines)[1]

def background(acc):
    top=(19,29,48); bot=(8,12,22)
    base = Image.new('RGB',(1,H))
    for y in range(H):
        base.putpixel((0,y),(int(top[0]+(bot[0]-top[0])*y/H), int(top[1]+(bot[1]-top[1])*y/H), int(top[2]+(bot[2]-top[2])*y/H)))
    img = base.resize((W,H))
    glow = Image.new('RGB',(W,H),(0,0,0))
    gd = ImageDraw.Draw(glow)
    tint=tuple(int((a*0.35 + b*0.65) * 0.42) for a, b in zip(acc, (70, 95, 150)))
    gd.ellipse([W//2-560,-380,W//2+560,300], fill=tint)
    glow = glow.filter(ImageFilter.GaussianBlur(150))
    return ImageChops.add(img, glow)

def style_of(cls, size, acc):
    if cls=='hero': return cover_font("Bold", int(size*1.45)), WHITE, False
    if cls=='accent': return cover_font("Bold", int(size*1.15)), acc, False
    if cls=='sub': return cover_font("SemiBold", max(20,int(size*0.8))), SUBC, True
    return cover_font("SemiBold", size), BASE, True

def line_heights(lines, size, acc):
    hs=[]
    for ln in lines:
        mx=size
        for (text, cls, glue) in ln:
            fnt,_,_=style_of(cls, size, acc)
            mx=max(mx, fnt.size)
        hs.append(int(mx*1.38))
    return hs

def draw_lines(d, img, items, lines, widths, x0, y_top, size, acc, heights):
    y=y_top
    idx=0
    for li, ln in enumerate(lines):
        mx=max(style_of(cls, size, acc)[0].size for (text, cls, glue) in ln)
        baseline=y+mx
        x=x0
        for pos,(text, cls, glue) in enumerate(ln):
            fnt,col,semi=style_of(cls, size, acc)
            if not (text=='：' and pos==len(ln)-1):
                if semi:
                    draw_semi(img, (x, baseline), text, fnt.size, col, baseline=True)
                else:
                    d.text((x, baseline), text, font=fnt, fill=col, anchor='ls')
            x+=widths[idx]; idx+=1
        y+=heights[li]
    return y

def finish(d, img, cat, tags, acc, y, out, x0=None, sx=None):
    if tags:
        y += 30
        tf=cover_font("Regular", 27)
        x=MARGIN if x0 is None else x0
        for tg in tags[:5]:
            label='#'+tg
            bb=d.textbbox((0,0), label, font=tf); iw=bb[2]-bb[0]; ih=bb[3]-bb[1]; pw=iw+34
            if x+pw > W-MARGIN: break
            d.rounded_rectangle([x,y,x+pw,y+48], radius=24, outline=(120,135,160), width=2)
            d.text((x+(pw-iw)/2-bb[0], y+(48-ih)/2-bb[1]), label, font=tf, fill=(203,213,225))
            x+=pw+14
    d.text((MARGIN if sx is None else sx, H-72), 'aoiro-labo.com', font=cover_font("Regular", 30), fill=(148,170,200))
    d.rectangle([0,H-10,W,H], fill=acc)
    img.save(out, quality=90)

import urllib.request, io
def body_images(path):
    t=open(path,encoding='utf-8').read()
    body=t.split('---',2)[2] if t.count('---')>=2 else t
    urls=[]
    for m in re.finditer(r'!\[[^\]]*\]\((<[^>]+>|[^)\s]+)', body):
        u=m.group(1).strip('<>')
        urls.append(u)
    return urls

def load_image(src):
    try:
        if src.startswith('http'):
            req=urllib.request.Request(src, headers={'User-Agent':'Mozilla/5.0'})
            data=urllib.request.urlopen(req, timeout=20).read()
            return Image.open(io.BytesIO(data)).convert('RGB')
        p = src.lstrip('/')
        if p.startswith('images/'): p = 'static/' + p
        return Image.open(p).convert('RGB')
    except Exception as e:
        print('  img load failed:', src[:80], e)
        return None

def ns_pick(path):
    return pick_image(path, 'auto')

def pick_image(path, cimg):
    if cimg=='none': return None
    if cimg and cimg!='auto':
        return load_image(cimg)
    best=None
    for u in body_images(path):
        im=load_image(u)
        if im is None: continue
        w,h=im.size
        if w<1000: continue
        a=w/h
        if a<1.2 or a>2.4: continue
        score=-abs(a-1.78)
        if best is None or score>best[0]+0.02:
            best=(score, im, u)
    if best: print('  picked image:', best[2][:90], best[1].size)
    return best[1] if best else None

def paste_panel(img, panel_img, x, y, pw, ph):
    src=panel_img
    scale=max(pw/src.size[0], ph/src.size[1])
    nw,nh=int(src.size[0]*scale+0.5), int(src.size[1]*scale+0.5)
    src=src.resize((nw,nh), Image.LANCZOS)
    left=(nw-pw)//2; top=(nh-ph)//2
    src=src.crop((left,top,left+pw,top+ph))
    mask=Image.new('L',(pw,ph),0)
    md=ImageDraw.Draw(mask)
    md.rounded_rectangle([0,0,pw,ph], radius=18, fill=255)
    img.paste(src,(x,y),mask)
    d=ImageDraw.Draw(img)
    d.rounded_rectangle([x,y,x+pw,y+ph], radius=18, outline=(120,135,160), width=2)

def split_bracket_prefix(disp):
    if disp.startswith('【') and '】' in disp:
        k=disp.index('】')+1
        if k<=14:
            return disp[:k], disp[k:]
    return None, disp

def paste_banner(img, src):
    # right-side full-height bleed, fading into the background on its left edge
    ph = H
    pw = 470
    scale=max(pw/src.size[0], ph/src.size[1])
    nw,nh=int(src.size[0]*scale+0.5), int(src.size[1]*scale+0.5)
    src=src.resize((nw,nh), Image.LANCZOS)
    left=(nw-pw)//2; top=(nh-ph)//2
    src=src.crop((left,top,left+pw,top+ph))
    fade=260
    mask=Image.new('L',(pw,ph),255)
    md=ImageDraw.Draw(mask)
    for x in range(fade):
        v=int(255 * (x/fade)**1.4)
        md.line([(x,0),(x,ph)], fill=v)
    img.paste(src,(W-pw,0),mask)

def auto_pick(disp, cat):
    # when cover_keyword / cover_emphasis are unset, pick from the title itself:
    # quoted phrases first, then latin/katakana standouts, then long words
    items = classify(split_emph(tokenize(disp), [], ''), [], '')
    merged=[]
    for (t,c,g) in items:
        if merged and c=='base' and t.strip() and merged[-1][1]=='base' and re.fullmatch(r'[A-Za-z0-9#@ ]+', merged[-1][0]) and re.fullmatch(r'[A-Za-z0-9#@ ]+', t):
            pt,pc,pg,pp = merged[-1]
            merged[-1] = (pt + ('' if pt.endswith(' ') else ' ') + t, pc, pg, pp+[t.strip()])
        else:
            merged.append((t,c,g,[t.strip()]))
    def score(core, last):
        sc=0
        if core.startswith(('「','『')): sc+=100
        if '#' in core: sc+=25
        if re.fullmatch(r'[A-Za-z0-9#@ ]+', core): sc+=40
        elif re.fullmatch(r'[ァ-ヶー･]+', core): sc+=35
        if len(core)>=6: sc+=15
        elif len(core)>=4: sc+=8
        if last and len(core)>=3: sc+=10
        if last and len(core)>=2 and core[-1] in 'ろえ': sc+=55
        return sc
    n=len(merged)
    cands=[]
    for i,(t,c,g,parts) in enumerate(merged):
        if c!='base': continue
        core=t.strip()
        if not core or core==cat: continue
        last = (i==n-1) or (i==n-2 and merged[-1][1]=='sub')
        sc=score(core, last)
        if sc>=30: cands.append((sc, i, core, parts))
    cands.sort(key=lambda x:(-x[0], x[1]))
    return cands

def make(path, out, hero_override=None, emphasis_override=None):
    title, cat, tags, kw, emph, cimg, slug = fm_of(path)
    hero = hero_override if hero_override is not None else kw
    if emphasis_override is not None: emph = emphasis_override
    disp = title.replace('（','(').replace('）',')')
    bracket, disp = split_bracket_prefix(disp)
    disp = disp.replace('・', '･')
    bracket_h = 40+24 if bracket else 0
    acc = accent_for(cat)
    cands = auto_pick(disp, cat)
    if not hero:
        singles = [c for c in cands if len(c[3])==1]
        if singles and singles[0][0]>=45:
            hero = singles[0][2]
            print('  auto hero:', hero)
    if not emph and cands:
        emph = []
        taken = 0
        for (sc,i,c,parts) in sorted(cands, key=lambda x:x[1]):
            if taken>=2: break
            if c.strip('「」『』')==hero.strip('「」『』'): continue
            emph.extend(parts)
            taken += 1
        if emph: print('  auto accents:', emph)
    if cat and hero and cat == hero:
        cat = ''
    img = background(acc)
    d = ImageDraw.Draw(img)
    cat_h = 34+30 if cat else 0
    chips_h = 48 if tags else 0
    cat_h += bracket_h

    if cimg=='none':
        pic = None
    elif cimg=='bg':
        pic = ns_pick(path)
    elif cimg=='auto':
        pic = ns_pick(path)
    elif cimg:
        pic = load_image(cimg)
    else:
        pic = None
    use_bg = pic is not None
    panel = None if use_bg else (pic if cimg in ('auto',) or (cimg and cimg not in ('none','bg')) else None)
    if use_bg:
        if True:
            scale=max(W/pic.size[0], H/pic.size[1])
            nw,nh=int(pic.size[0]*scale+0.5), int(pic.size[1]*scale+0.5)
            bgimg=pic.resize((nw,nh), Image.LANCZOS).crop(((nw-W)//2,(nh-H)//2,(nw-W)//2+W,(nh-H)//2+H))
            from PIL import ImageStat
            g=bgimg.convert('L'); mean=ImageStat.Stat(g).mean[0]
            esmall=g.resize((320, int(320*g.size[1]/g.size[0]))).filter(ImageFilter.FIND_EDGES)
            if ImageStat.Stat(esmall).mean[0] >= 20:
                bgimg=bgimg.filter(ImageFilter.GaussianBlur(3))
            alpha=min(0.9, max(0.62, 1-52/max(mean,1)))
            dark=Image.new('RGB',(W,H),(10,15,26))
            img=Image.blend(bgimg, dark, alpha)
            grad=Image.new('L',(W,1))
            for gx in range(W):
                grad.putpixel((gx,0), int(60+110*(1-gx/W)))
            shade=Image.new('RGB',(W,H),(6,9,16))
            img=Image.composite(shade, img, grad.resize((W,H)))
            d=ImageDraw.Draw(img)
    if panel is not None:
        items = classify(split_emph(tokenize(disp), emph, hero), emph, hero)
        col_w = int((W - MARGIN*2) * 0.62)
        def solve_n(ml_target):
            for size_try in range(96, 39, -4):
                widths=[]
                for (text, cls, glue) in items:
                    fnt,_,_=style_of(cls, size_try, acc); widths.append(d.textlength(text, font=fnt))
                lt=layout(items, widths, col_w, ml_target, balance_last=True, min_fill=0.5)
                if not lt or len(lt)!=ml_target: continue
                hs=line_heights(lt, size_try, acc)
                if cat_h + sum(hs) + (30 if tags else 0) + chips_h > H - 150: continue
                return (size_try, lt, widths, hs)
            return None
        sols={}
        for ml_t in (2,3):
            s=solve_n(ml_t)
            if s: sols[ml_t]=s
        if 2 in sols and 3 in sols and sols[2][0]<76 and sols[3][0]>=sols[2][0]:
            chosen=sols[3]
        elif sols:
            chosen=sols[min(sols)]
        else:
            chosen=None
        if chosen is None or chosen[0] < 52:
            panel=None
            print('  image dropped (no room beside text):', out)
        else:
            size, lines, widths, heights = chosen
            block_h=sum(heights)
            total = cat_h + block_h + (30 if tags else 0) + chips_h
            y = (H - total)//2 - 14
            if cat:
                draw_semi(img, (MARGIN, y), cat, 34, acc); y += 34+30
            if bracket:
                draw_semi(img, (MARGIN, y), bracket, 40, SUBC); y += bracket_h
            draw_lines(d, img, items, lines, widths, MARGIN, y, size, acc, heights)
            y += block_h
            if tags:
                y += 30
                tf=cover_font("Regular", 27)
                x=MARGIN
                for tg in tags[:5]:
                    label='#'+tg
                    bb=d.textbbox((0,0), label, font=tf); iw=bb[2]-bb[0]; ih=bb[3]-bb[1]; pw=iw+34
                    if x+pw > MARGIN+col_w: break
                    d.rounded_rectangle([x,y,x+pw,y+48], radius=24, outline=(120,135,160), width=2)
                    d.text((x+(pw-iw)/2-bb[0], y+(48-ih)/2-bb[1]), label, font=tf, fill=(203,213,225))
                    x+=pw+14
            region_w = W - MARGIN - (MARGIN+col_w) - 24
            region_h = H - 190
            scale=min(region_w/panel.size[0], region_h/panel.size[1])
            nw,nh=int(panel.size[0]*scale), int(panel.size[1]*scale)
            thumb=panel.resize((nw,nh), Image.LANCZOS)
            px = W - MARGIN - nw
            py = H - 120 - nh
            shadow=Image.new('RGBA',(nw+16,nh+16),(0,0,0,0))
            sd=ImageDraw.Draw(shadow)
            sd.rounded_rectangle([8,10,nw+8,nh+12], radius=14, fill=(0,0,0,110))
            shadow=shadow.filter(ImageFilter.GaussianBlur(6))
            img.paste(shadow,(px-8,py-8),shadow)
            mask=Image.new('L',(nw,nh),0)
            md=ImageDraw.Draw(mask)
            md.rounded_rectangle([0,0,nw,nh], radius=14, fill=255)
            img.paste(thumb,(px,py),mask)
            d.rounded_rectangle([px,py,px+nw,py+nh], radius=14, outline=(120,135,160), width=2)
            d.text((MARGIN, H-72), 'aoiro-labo.com', font=cover_font("Regular", 30), fill=(148,170,200))
            d.rectangle([0,H-10,W,H], fill=acc)
            img.save(out, quality=90)
            print('made (natural)', out, '| hero:', hero, '| lines:', [[t for (t,c,g) in ln] for ln in lines])
            return
    zone = False
    if hero and disp.endswith(hero):
        # try zone composition: hero block on the right, white
        ksize=300
        while ksize>90:
            kw_font=cover_font("Bold", ksize)
            kw_w=d.textlength(hero, font=kw_font)
            if kw_w <= W*0.36: break
            ksize-=12
        body = disp[:-len(hero)]
        items = classify(split_emph(tokenize(body), emph, ''), emph, '')
        cap_w = int(kw_w)
        size=None; lines=None; widths=None; col_w=None; hero_w_cap=cap_w
        # prefer a 2-line body: shrink the hero (down to 0.24W) before shrinking the type
        for s_try in range(76, 57, -2):
            w_try=[]
            for (text, cls, glue) in items:
                fnt,_,_=style_of(cls, s_try, acc); w_try.append(d.textlength(text, font=fnt))
            hw = cap_w
            while hw >= int(W*0.24):
                cw = W - MARGIN*2 - hw - 48
                ln = layout(items, w_try, cw, 2)
                if ln:
                    size, lines, widths, col_w, hero_w_cap = s_try, ln, w_try, cw, hw
                    break
                hw -= 24
            if lines: break
        if lines is None:
            col_w = W - MARGIN*2 - cap_w - 48
            size=76
            while size>=52:
                widths=[]
                for (text, cls, glue) in items:
                    fnt,_,_=style_of(cls, size, acc); widths.append(d.textlength(text, font=fnt))
                for ml in (2,3):
                    lines=layout(items, widths, col_w, ml)
                    if lines: break
                if lines: break
                size-=4
        if lines:
            zone=True
            heights=line_heights(lines, size, acc)
            block_h=sum(heights)
            kw_w_max = hero_w_cap
            # size the hero so its ink height matches the left text block height
            _f100=cover_font("Bold", 100)
            _bb=d.textbbox((0,0), hero, font=_f100)
            _ratio=(_bb[3]-_bb[1])/100.0
            ksize=max(60, int(block_h*0.85/_ratio))
            while ksize>60:
                kw_font=cover_font("Bold", ksize)
                kw_w=d.textlength(hero, font=kw_font)
                if kw_w <= kw_w_max: break
                ksize-=8
            kw_font=cover_font("Bold", ksize)
            kw_w=d.textlength(hero, font=kw_font)
            kw_bb=d.textbbox((0,0), hero, font=kw_font)
            line_ws=[]; _idx=0
            for ln in lines:
                line_ws.append(sum(widths[_idx:_idx+len(ln)])); _idx+=len(ln)
            maxlw=max(line_ws)
            gx = max(MARGIN, (W - (maxlw + 14 + kw_w))//2)
            total = cat_h + block_h + (30 if tags else 0) + chips_h
            y = (H - total)//2 - 14
            if cat:
                draw_semi(img, (gx, y), cat, 34, acc); y += 34+30
            if bracket:
                draw_semi(img, (gx, y), bracket, 40, SUBC); y += bracket_h
            title_top = y
            draw_lines(d, img, items, lines, widths, gx, y, size, acc, heights)
            d.text((gx + maxlw + 14, title_top - kw_bb[1]), hero, font=kw_font, fill=WHITE)
            y += block_h
            finish(d, img, cat, tags, acc, y, out, x0=gx, sx=gx)
            print('made (zone)', out, '| hero:', hero)
            return
    # full-width flow (hero inline if it is a suffix, else plain)
    items = classify(split_emph(tokenize(disp), emph, hero), emph, hero)
    maxw = W - MARGIN*2
    def solve_for(ml_target):
        for size_try in range(100, 39, -4):
            widths=[]
            for (text, cls, glue) in items:
                fnt,_,_=style_of(cls, size_try, acc); widths.append(d.textlength(text, font=fnt))
            lt=layout(items, widths, maxw, ml_target, balance_last=True, min_fill=0.58)
            if not lt or len(lt)!=ml_target: continue
            line_ws=[]; idx=0
            for ln in lt:
                lw=sum(widths[idx:idx+len(ln)]); idx+=len(ln); line_ws.append(lw)
            if not all(lw>=maxw*0.45 for lw in line_ws[:-1]): continue
            hs=line_heights(lt, size_try, acc)
            if cat_h + sum(hs) + (30 if tags else 0) + chips_h > H-140: continue
            return (size_try, lt, widths, hs)
        return None
    sol = {}
    for ml_target in (1,2,3):
        s = solve_for(ml_target)
        if s: sol[ml_target]=s
    chosen=None
    if 2 in sol and 3 in sol and sol[2][0] < 76 and sol[3][0] >= sol[2][0]:
        chosen = sol[3]
    elif 2 in sol: chosen = sol[2]
    elif 3 in sol: chosen = sol[3]
    elif 1 in sol: chosen = sol[1]
    elif sol: chosen = sol[max(sol)]
    size, lines, widths, heights = chosen
    block_h=sum(heights)
    total = cat_h + block_h + (30 if tags else 0) + chips_h
    y = (H - total)//2 - 14
    if cat:
        draw_semi(img, (MARGIN, y), cat, 34, acc); y += 34+30
    if bracket:
        draw_semi(img, (MARGIN, y), bracket, 40, SUBC); y += bracket_h
    draw_lines(d, img, items, lines, widths, MARGIN, y, size, acc, heights)
    y += block_h
    finish(d, img, cat, tags, acc, y, out)
    print('made (flow)', out, '| hero:', hero, '| lines:', [[t for (t,c,g) in ln] for ln in lines])

if __name__ == '__main__':
    for p in sys.argv[1:]:
        _t,_c,_tg,_k,_e,_ci,sl = fm_of(p)
        make(p, rf'static\images\cover-{sl}.jpg')
