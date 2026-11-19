import json, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
k=Kokoro("/home/claude/models/kokoro.onnx","/home/claude/models/voices.bin")
lines=[
"Uluru is not a rock sitting on the desert. It's the tip of something far bigger.",
"Five hundred and fifty million years ago, giant mountains rose right here, in the middle of Australia.",
"Rain tore those granite peaks apart, and the sand washed down into huge fans at their base, kilometres thick.",
"Then a shallow sea flooded in, burying the sand under mud. The weight slowly pressed it into hard rock.",
"Hundreds of millions of years later, the land was squeezed again. The layers tipped until they stood almost straight up.",
"Over time, the softer rock around it wore away. Uluru's tough sandstone stayed. The three hundred and forty eight metres you see is only the exposed top.",
"And that famous red? It's rust. Iron in the rock reacting with the air. Underneath, it's grey.",
"For the Anangu, its Traditional Owners, Uluru is a sacred place, with stories far older than this science.",
"Follow How On Earth, for a new wonder every day.",
]
meta=[]
for i,t in enumerate(lines):
    a,sr=k.create(t,voice="am_michael",speed=1.0,lang="en-us")
    sf.write(f"l{i}.wav",a,sr); meta.append({"text":t,"dur":len(a)/sr})
json.dump(meta,open("meta.json","w"),indent=1)
print(sum(m["dur"] for m in meta)); print([round(m["dur"],2) for m in meta])
