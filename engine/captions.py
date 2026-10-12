#!/usr/bin/env python
"""Word-level karaoke captions -> one ASS file. Usage: captions.py out.ass key1:wav1 key2:wav2 ...
Offsets are cumulative wav durations (each final segment == its audio length)."""
import sys, numpy as np, soundfile as sf
from faster_whisper import WhisperModel

def load_16k(wav):
    a,sr=sf.read(wav,dtype="float32")
    if a.ndim>1: a=a.mean(axis=1)
    if sr!=16000:
        n=int(round(len(a)*16000/sr))
        a=np.interp(np.linspace(0,len(a),n,endpoint=False),np.arange(len(a)),a).astype("float32")
    return a

def load_model():
    for dev,ct in (("cpu","int8"),):
        try:
            m=WhisperModel("small.en",device=dev,compute_type=ct)
            print("whisper on",dev); return m
        except Exception as e:
            print("whisper",dev,"failed:",str(e)[:80])
    raise SystemExit("no whisper backend")

def words_for(model, wav):
    segs,_=model.transcribe(load_16k(wav), word_timestamps=True, vad_filter=False)
    ws=[]
    for s in segs:
        for w in (s.words or []):
            ws.append((w.word.strip(), float(w.start), float(w.end)))
    return ws

def ass_time(t):
    h=int(t//3600); m=int((t%3600)//60); s=t%60
    return f"{h:d}:{m:02d}:{s:05.2f}"

HEAD = r"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap, Noto Sans, 52, &H00F3EDE6, &H00888888, &H00000000, &HB0000000, -1, 0, 0, 0, 100, 100, 0, 0, 3, 3, 0, 2, 180, 180, 90, 1
"""
# PrimaryColour = active/sung (near-white F3EDE6 in BGR), SecondaryColour = pending (grey)

def chunk(words, max_w=7, max_s=3.0):
    out=[]; cur=[]
    for w in words:
        if cur and (len(cur)>=max_w or (w[2]-cur[0][1])>max_s):
            out.append(cur); cur=[]
        cur.append(w)
    if cur: out.append(cur)
    return out

def main():
    out=sys.argv[1]; items=[a.split(":",1) for a in sys.argv[2:]]
    model=load_model()
    lines=[HEAD,"\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"]
    offset=0.0
    for key,wav in items:
        a,sr=sf.read(wav,dtype="float32")
        if a.ndim>1: a=a.mean(axis=1)
        dur=len(a)/sr
        onset=float(np.argmax(np.abs(a)>0.02*np.max(np.abs(a))))/sr   # real speech start
        ws=words_for(model,wav)
        # whisper often anchors the first word to 0; shift this scene so word1 == onset
        delta=0.0
        if ws:
            delta=min(0.6,max(0.0,onset-ws[0][1]))
        for ph in chunk(ws):
            st=max(0,offset+ph[0][1]+delta); en=max(0.1,offset+ph[-1][2]+delta)
            # karaoke: each word's \kf = its own duration in centiseconds
            txt=""
            for i,(w,a,b) in enumerate(ph):
                nxt = ph[i+1][1] if i+1<len(ph) else b
                cs=max(6,int(round((nxt-a)*100)))
                txt+=f"{{\\kf{cs}}}{w} "
            lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Cap,,0,0,0,,{txt.strip()}")
        offset+=dur+0.6   # each segment carries a 0.6s tail (see build); keep offsets aligned
    open(out,"w").write("\n".join(lines)+"\n")
    print("wrote",out,"offsets end",round(offset,2),"s")

if __name__=="__main__": main()
