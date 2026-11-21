#!/usr/bin/env python3
"""Submit/check serverless jobs. Needs env RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID (read from
/workspace/v2/.runpod.env as KEY=VALUE lines if not in env).
  client.py run <job_id>     (job must already be pushed: python3 harness/gpu.py push <job_id>)
  client.py status <req_id>  ;  client.py health"""
import json, os, pathlib, sys, urllib.request
f = pathlib.Path(__file__).resolve().parents[2] / ".runpod.env"
if f.exists():
    for l in f.read_text().splitlines():
        if "=" in l and not l.startswith("#"): k, v = l.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
K, E = os.environ.get("RUNPOD_API_KEY"), os.environ.get("RUNPOD_ENDPOINT_ID")
if not (K and E): sys.exit("missing RUNPOD_API_KEY / RUNPOD_ENDPOINT_ID (.runpod.env)")
def call(path, body=None):
    r = urllib.request.Request(f"https://api.runpod.ai/v2/{E}/{path}", data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {K}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=60))
c = sys.argv[1]
if c == "run": print(call("run", {"input": {"job_id": sys.argv[2]}}))
elif c == "status": print(call("status/" + sys.argv[2]))
elif c == "health": print(call("health"))
