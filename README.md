# Serverless GPU setup (M0039)
Operator steps are in the Telegram message; summary: build image from this dir, create Serverless endpoint
with the same network volume attached, put API key + endpoint id in /workspace/v2/.runpod.env.
Flow: prepare work/gpu_jobs/<id>/ -> `python3 harness/gpu.py push <id>` -> `python3 work/serverless/client.py run <id>`
-> poll `client.py status` -> `gpu.py pull <id>` -> `ledger.py import-run`. Active workers=0 so billing only while running.
