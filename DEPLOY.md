# Deploy the GPU worker (simple version)

You do NOT need Docker on your machine. RunPod can build the image straight from GitHub.

## Facts
- `/workspace` is already a RunPod **network volume**. Your data is already on it.
- The serverless endpoint must attach **that same volume**. It then appears at `/runpod-volume`
  inside the worker, and `handler.py` reads jobs from `/runpod-volume/gpu_jobs_v2`.
- This folder contains everything needed: `Dockerfile`, `handler.py`, `client.py`.

## Steps (about 10 minutes)

1. **Put this folder in a GitHub repo** (only this folder, not the whole workspace).
   - Repo root must contain `Dockerfile`, `handler.py`, `client.py`.
   - Do NOT commit API keys.

2. **In RunPod console → Serverless → New Endpoint**
   - Source: **GitHub repo** (connect your GitHub account, pick the repo, branch `main`).
   - GPU: pick one you need (for example 24 GB).
   - Active workers: **0** (you pay only while a job runs).
   - Max workers: 1.
   - Execution timeout: longer than your longest job.
   - **Network volume: select the same volume** that `/workspace` uses.
   - Deploy. RunPod builds the image on its side.

3. **Copy the endpoint ID and create an API key** (Settings → API Keys).
   Save them in `/workspace/v2/.runpod.env`:
   ```
   RUNPOD_API_KEY=your_key
   RUNPOD_ENDPOINT_ID=your_endpoint_id
   ```

4. **Test it**
   ```
   python3 /workspace/v2/work/serverless/client.py health
   ```
   Then run a real job:
   ```
   python3 /workspace/v2/harness/gpu.py push <job_id>
   python3 /workspace/v2/work/serverless/client.py run <job_id>
   python3 /workspace/v2/work/serverless/client.py status <request_id>
   python3 /workspace/v2/harness/gpu.py pull <job_id>
   ```

## Simpler alternative (no serverless)
If serverless feels like too much, use a normal **GPU pod**: choose the stock `runpod/pytorch` template,
attach the same network volume, open a terminal and run the job's `run.sh`. This is the flow the
project already describes in `harness/gpu.py`. It bills hourly, so stop the pod when done.

## Troubleshooting
- `health` fails: check the endpoint ID and API key in `.runpod.env`.
- Job goes to `failed/`: read `/workspace/gpu_jobs_v2/failed/<job_id>/stdout.log`.
- Build fails on GitHub: check the Dockerfile base image tag exists on Docker Hub.
