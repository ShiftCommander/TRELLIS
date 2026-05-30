#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd: list[str]) -> tuple[int, str]:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=False)
        text = (out.stdout or "").strip() or (out.stderr or "").strip()
        return out.returncode, text
    except Exception as exc:
        return 1, str(exc)


def check_binary(name: str) -> dict:
    path = shutil.which(name)
    return {"name": name, "ok": bool(path), "detail": path or "not found"}


def python_import_check(module: str) -> dict:
    code = f"import {module}; print('ok')"
    rc, out = run_cmd([sys.executable, "-c", code])
    return {"name": f"python_import:{module}", "ok": rc == 0, "detail": out}


def main():
    repo_root = Path(__file__).resolve().parents[1]
    report_path = repo_root / "outputs" / "avatar-man-1" / "qa" / "preflight_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    checks = []
    checks.append({"name": "platform_linux", "ok": sys.platform.startswith("linux"), "detail": sys.platform})
    checks.append(check_binary("nvidia-smi"))
    checks.append(check_binary("blender"))
    checks.append(check_binary("conda"))

    rc, out = run_cmd(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
    checks.append({"name": "nvidia_smi_query", "ok": rc == 0, "detail": out})

    for module in ["torch", "imageio", "PIL", "numpy"]:
        checks.append(python_import_check(module))

    rc, out = run_cmd(
        [
            sys.executable,
            "-c",
            "import torch; print('cuda_available=' + str(torch.cuda.is_available())); "
            "print('device_count=' + str(torch.cuda.device_count()))",
        ]
    )
    checks.append({"name": "torch_cuda_check", "ok": rc == 0 and "cuda_available=True" in out, "detail": out})

    rc, out = run_cmd([sys.executable, "-c", "import trellis; print('ok')"])
    checks.append({"name": "python_import:trellis", "ok": rc == 0, "detail": out})

    ok = all(c["ok"] for c in checks)
    report = {"status": "PASS" if ok else "FAIL", "checks": checks}
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
