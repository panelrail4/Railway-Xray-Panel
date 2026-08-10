import json, subprocess
from ..config import settings

def query_all():
    p=subprocess.run(
        [settings.XRAY_PATH,"api","statsquery","--server=127.0.0.1:10085"],
        capture_output=True,text=True,timeout=10
    )
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout or "stats query failed").strip())
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("Xray returned non-JSON statistics output")

def parse_stats(payload):
    result={"users":{}, "inbounds":{}, "outbounds":{}}
    for item in payload.get("stat", []):
        name=item.get("name","")
        try: value=int(item.get("value",0))
        except: value=0
        parts=name.split(">>>")
        if len(parts)!=4 or parts[2]!="traffic": continue
        bucket,key,direction=parts[0],parts[1],parts[3]
        result.setdefault(bucket+"s",{}).setdefault(key,{"uplink":0,"downlink":0})
        result[bucket+"s"][key][direction]=value
    for bucket in ("users","inbounds","outbounds"):
        for key,v in result[bucket].items():
            v["total"]=v["uplink"]+v["downlink"]
    return result
