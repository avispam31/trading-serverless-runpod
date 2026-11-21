"""RunPod SERVERLESS worker. Input: {"input": {"job_id": "<id>"}}.
Takes /jobs/pending/<id> (same layout as harness/gpu.py push), runs run.sh with OUT_DIR, writes
manifest.json (sha256 manifest, same format as harness/pod_runner.sh) and moves job to done/ or failed/.
Network volume is mounted at /runpod-volume in serverless; we symlink /workspace to it."""
import hashlib, json, os, pathlib, shutil, subprocess, time
import runpod
VOL = pathlib.Path("/runpod-volume")
if VOL.exists() and not pathlib.Path("/workspace").exists():
    os.symlink(VOL, "/workspace")
J = pathlib.Path(os.environ.get("JOBS_DIR", "/runpod-volume/gpu_jobs_v2"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def handler(ev):
    job = ev["input"]["job_id"]
    for s in ("pending", "running", "done", "failed"): (J / s).mkdir(parents=True, exist_ok=True)
    src = J / "pending" / job
    if not src.exists(): return {"error": f"no pending job {job}"}
    run = J / "running" / job; shutil.rmtree(run, ignore_errors=True); shutil.move(str(src), str(run))
    W = pathlib.Path("/tmp/podjobs") / job; shutil.rmtree(W, ignore_errors=True); (W / "out").mkdir(parents=True)
    shutil.copytree(run, W / "in")
    gpu = subprocess.run("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader", shell=True, capture_output=True, text=True).stdout.strip().split("\n")[0]
    t0 = time.time(); start = time.strftime("%FT%TZ", time.gmtime())
    with open(W / "out" / "stdout.log", "w") as f:
        rc = subprocess.run(["bash", "run.sh"], cwd=W / "in", stdout=f, stderr=subprocess.STDOUT,
                            env={**os.environ, "OUT_DIR": str(W / "out")}).returncode
    out = W / "out"
    outs = {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob("*")) if p.is_file() and p.name != "manifest.json"}
    json.dump({"job_id": job, "name": job, "cmd": ["bash", "run.sh"], "started": start, "wall_seconds": round(time.time() - t0, 1),
               "exit_code": rc, "gpu": gpu, "outputs": outs}, open(out / "manifest.json", "w"), indent=1)
    dest = "failed" if rc != 0 or not (out / "metrics.json").exists() else "done"
    d = J / dest / job; shutil.rmtree(d, ignore_errors=True); shutil.copytree(out, d); shutil.rmtree(run, ignore_errors=True)
    return {"job_id": job, "state": dest, "exit_code": rc, "wall_seconds": round(time.time() - t0, 1), "gpu": gpu}
runpod.serverless.start({"handler": handler})
