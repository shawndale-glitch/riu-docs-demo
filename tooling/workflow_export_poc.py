"""PoC: FigJam extraction JSON -> workflow.yaml + README.md + lint report."""
import json, re, sys, yaml
from collections import defaultdict
src = json.load(open(sys.argv[1]))
TYPE = {"Eventos/Evento de inicio":"event.start","Eventos/Evento de fin":"event.end","Eventos/Evento intermedio":"event.intermediate",
        "Actividades/Actividad":"task","Actividades/Subproceso":"subprocess","Compuertas/Decisión (XOR)":"gateway.xor",
        "Compuertas/Paralelo (AND)":"gateway.and","Datos y sistemas/Sistema":"system","Datos y sistemas/Documento":"document",
        "Datos y sistemas/Almacén de datos":"datastore","Datos y sistemas/Anotación":"rule","STICKY":"note"}
clean = lambda s: re.sub(r"\s+"," ",s or "").strip()
lanes = {l["id"]: l["role"] for l in src["lanes"]}
hdr = next(n["props"] for n in src["nodes"] if n["comp"]=="Plantilla/Bloque de cabecera")
d = hdr["Última actualización"]; m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})$", d)
iso = f"{m[3]}-{m[2]}-{m[1]}" if m else d
errors, warns = [], []
nodes = {}
for n in src["nodes"]:
    if n["comp"] in ("Plantilla/Bloque de cabecera",): continue
    t = TYPE.get(n["comp"])
    if not t:
        if n["comp"] in ("SECTION",): continue
        errors.append(f"R2 off-library shape {n['id']} ({n['comp']}) «{clean(n.get('label'))}»")
        t = "UNTYPED"
    nodes[n["id"]] = {"id": n["id"], "type": t, "lane": n.get("lane"), "label": clean(n.get("label"))}
flows, assoc = [], []
out_, in_ = defaultdict(list), defaultdict(list)
for e in src["edges"]:
    f, t = e["from"], e["to"]
    if t in lanes or f in lanes: errors.append(f"R3 connector {e['id']} ends on a lane ({lanes.get(t) or lanes.get(f)})"); continue
    if f not in nodes or t not in nodes: errors.append(f"R3 connector {e['id']} attached to a section/unknown node"); continue
    rec = {"id": e["id"], "from": f, "to": t}
    if clean(e["label"]): rec["condition"] = clean(e["label"])
    if e["dash"] == "dashed": rec["type"] = "association"; assoc.append(rec); continue
    rec["type"] = "sequence"; flows.append(rec); out_[f].append(rec); in_[t].append(rec)
for nid, n in nodes.items():
    lbl = f"{n['type']} {nid} «{n['label']}»"
    if n["type"] in ("note","rule","system","document","datastore","UNTYPED"): 
        if n["type"]=="rule" and not any(a["to"]==nid or a["from"]==nid for a in assoc): warns.append(f"W rule {nid} not linked to any step")
        continue
    if n["type"]=="event.end" and out_[nid]: errors.append(f"R5 end event has outgoing flow: {lbl} → use a message flow (dashed) or an intermediate event")
    if n["type"]!="event.start" and not in_[nid]: errors.append(f"R5 unreachable (no incoming flow): {lbl}")
    if n["type"] not in ("event.end",) and not out_[nid]: errors.append(f"R5 dead end (no outgoing flow): {lbl}")
    if n["type"]=="gateway.xor":
        if len(out_[nid])<2: errors.append(f"R4 XOR with {len(out_[nid])} exit(s): {lbl}")
        for r in out_[nid]:
            if "condition" not in r: errors.append(f"R4 unlabeled exit {r['id']} from {lbl}")
    elif n["type"]!="event.start" and any("condition" in r for r in out_[nid]):
        warns.append(f"W conditional exit from a non-gateway: {lbl} → add an XOR")
    if n["lane"] is None: errors.append(f"R6 not inside a lane: {lbl}")
starts=[n for n in nodes.values() if n["type"]=="event.start"]
if len(starts)!=1: errors.append(f"R5 {len(starts)} start events (expected 1): " + ", ".join(s['label'] for s in starts))
if not m: errors.append(f"R7 date not ISO: {d}")
if "  " in hdr["Nombre del proceso"]: warns.append("W3 double space in process name")
doc = {"process":{"id":hdr["ID del proceso"],"name":clean(hdr["Nombre del proceso"]),"owner":hdr["Responsable"],"version":hdr["Versión"],
        "status":hdr["Estado"],"updated":iso,"state":hdr["Actual / futuro"],"source":{"file":"ZKLzn26919OP9YGE3QOk5Z","page":"18:354"}},
       "lanes":[{"id":k,"role":v} for k,v in lanes.items()],
       "nodes":list(nodes.values()),"flows":flows,"associations":assoc}
yaml.safe_dump(doc, open("workflow.yaml","w"), allow_unicode=True, sort_keys=False, width=120)
mid = lambda s: "n"+s.replace(":","_")
shape = {"event.start":'(("{}"))',"event.end":'((("{}")))',"gateway.xor":'{{"{}"}}',"task":'["{}"]',"system":'[("{}")]',"rule":'>"{}"]',"note":'>"{}"]',"UNTYPED":'["⚠ {}"]',"document":'[/"{}"/]'}
L=["```mermaid","flowchart LR"]
for k,v in lanes.items():
    L.append(f'  subgraph {mid(k)}["{v}"]')
    for n in nodes.values():
        if n["lane"]==v and n["type"]!="note": L.append("    "+mid(n["id"])+shape.get(n["type"],'["{}"]').format(n["label"].replace('"',"'") or "(empty)"))
    L.append("  end")
for n in nodes.values():
    if n["lane"] is None: L.append("  "+mid(n["id"])+shape.get(n["type"],'["{}"]').format(n["label"].replace('"',"'") or "(empty)"))
for f in flows: L.append(f"  {mid(f['from'])} -->" + (f"|{f['condition']}|" if 'condition' in f else "") + f" {mid(f['to'])}")
for a in assoc: L.append(f"  {mid(a['from'])} -.-> {mid(a['to'])}")
L.append("```")
p=doc["process"]
md=[f"# {p['id']} — {p['name']}","",
    "> Generated from FigJam. Do not edit by hand; edit the board and re-export.","",
    "| Field | Value |","|---|---|"]+[f"| {k} | {v} |" for k,v in p.items() if k!="source"]+["","## Flow",""]+L+["","## Steps","","| ID | Lane | Type | Label | Next |","|---|---|---|---|---|"]
for n in nodes.values():
    nxt="; ".join((f"[{r['condition']}] " if 'condition' in r else "")+nodes[r['to']]['label'] for r in out_[n['id']])
    md.append(f"| `{n['id']}` | {n['lane'] or '—'} | {n['type']} | {n['label'] or '(empty)'} | {nxt or '—'} |")
md+=["","## Lint","",f"**{len(errors)} errors, {len(warns)} warnings** — export {'BLOCKED' if errors else 'OK'}.",""]+[f"- ❌ {x}" for x in errors]+[f"- ⚠️ {x}" for x in warns]
open("README.md","w").write("\n".join(md)+"\n")
print(f"{len(nodes)} nodes, {len(flows)} sequence flows, {len(assoc)} associations, {len(errors)} errors, {len(warns)} warnings")
print("\n".join(errors+warns))
