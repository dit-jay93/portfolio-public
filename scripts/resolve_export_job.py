#!/usr/bin/env python3
"""
Resolve -> Linux scheduler job manifest 생성 스크립트 (UI 팝업 버전)
- 타임라인 클립 경로를 수집해 source.input_files에 기록
- 코덱 프리셋 / 파일명 모드 / 템플릿 / 수동 파일명 UI 선택
"""

import json
import os
import re
import uuid
from datetime import datetime, timezone

# ===== 경로 설정 =====
JOBS_DIR = "/Volumes/share_rw/nasuser/06_MEDIA/incoming_jobs"  # mac에서 보이는 경로
LINUX_OUT = "<NAS_ROOT>/06_MEDIA/outcoming"        # Linux 워커가 쓰는 경로
MAC_SHARE_ROOT = "/Volumes/share_rw/nasuser"
LINUX_SHARE_ROOT = "<NAS_ROOT>"

CODEC_PRESETS = ["prores_proxy", "h264_proxy", "h265_proxy", "h264_nvenc", "h265_nvenc", "dnxhr_lb"]
FILENAME_MODES = ["source", "template", "manual"]
RENDER_MODES = ["clip_each", "timeline_single"]

CODEC_MAP = {
    "prores_proxy": {
        "container": "mov",
        "codec": "prores_ks",
        "profile": "proxy",
        "ffmpeg_args": "-c:v prores_ks -profile:v 0 -pix_fmt yuv422p10le -c:a pcm_s16le",
        "audio": {"codec": "pcm_s16le", "sample_rate": 48000, "channels": 2},
    },
    "h264_proxy": {
        "container": "mp4",
        "codec": "libx264",
        "profile": "high",
        "ffmpeg_args": "-c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 128k",
        "audio": {"codec": "aac", "sample_rate": 48000, "channels": 2},
    },
    "h265_proxy": {
        "container": "mp4",
        "codec": "libx265",
        "profile": "main",
        "ffmpeg_args": "-c:v libx265 -preset medium -crf 28 -c:a aac -b:a 128k",
        "audio": {"codec": "aac", "sample_rate": 48000, "channels": 2},
    },
    "h264_nvenc": {
        "container": "mp4",
        "codec": "h264_nvenc",
        "profile": "high",
        "ffmpeg_args": "-hwaccel cuda -c:v h264_nvenc -preset p5 -cq 23 -b:v 0 -c:a aac -b:a 128k",
        "audio": {"codec": "aac", "sample_rate": 48000, "channels": 2},
    },
    "h265_nvenc": {
        "container": "mp4",
        "codec": "hevc_nvenc",
        "profile": "main",
        "ffmpeg_args": "-hwaccel cuda -c:v hevc_nvenc -preset p5 -cq 26 -b:v 0 -c:a aac -b:a 128k",
        "audio": {"codec": "aac", "sample_rate": 48000, "channels": 2},
    },
    "dnxhr_lb": {
        "container": "mov",
        "codec": "dnxhd",
        "profile": "dnxhr_lb",
        "ffmpeg_args": "-c:v dnxhd -profile:v dnxhr_lb -c:a pcm_s16le",
        "audio": {"codec": "pcm_s16le", "sample_rate": 48000, "channels": 2},
    },
}


DEFAULTS = {
    "codec_preset": "prores_proxy",
    "render_mode": "clip_each",
    "filename_mode": "source",
    "filename_template": "%{src_name}",
    "manual_filename": "",
    "width": "1920",
    "height": "1080",
    "fps": "23.976",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", text)


def mac_to_linux_path(path: str) -> str:
    if path.startswith(MAC_SHARE_ROOT):
        return path.replace(MAC_SHARE_ROOT, LINUX_SHARE_ROOT, 1)
    return path


def collect_timeline_input_linux_paths(timeline):
    paths = []
    seen = set()

    track_count = int(timeline.GetTrackCount("video") or 0)
    for track_idx in range(1, track_count + 1):
        items = timeline.GetItemListInTrack("video", track_idx) or []
        for item in items:
            mpi = item.GetMediaPoolItem()
            if not mpi:
                continue

            try:
                clip_path = (mpi.GetClipProperty("File Path") or "").strip()
            except Exception:
                clip_path = ""

            if not clip_path:
                continue

            linux_path = mac_to_linux_path(clip_path)
            if linux_path.startswith("/Volumes/"):
                continue

            if linux_path not in seen:
                seen.add(linux_path)
                paths.append(linux_path)

    if not paths:
        raise RuntimeError("타임라인에서 유효한 원본 파일 경로를 찾지 못했습니다.")

    return paths


def build_output_filename(src_path: str, project_name: str, timeline_name: str, container: str, mode: str, template: str, manual: str) -> str:
    src_base = os.path.basename(src_path)
    src_name, _src_ext = os.path.splitext(src_base)

    if mode == "source":
        base = src_name
    elif mode == "manual" and manual.strip():
        base = manual.strip()
    else:
        tokens = {
            "%{src_name}": src_name,
            "%{project}": project_name,
            "%{timeline}": timeline_name,
            "%{date}": datetime.now().strftime("%Y%m%d"),
            "%{time}": datetime.now().strftime("%H%M%S"),
        }
        base = template
        for k, v in tokens.items():
            base = base.replace(k, v)

    base = safe_name(base)
    ext = f".{container}"
    if not base.lower().endswith(ext):
        base += ext
    return base


def to_int(v: str, name: str) -> int:
    try:
        return int(v)
    except Exception:
        raise RuntimeError(f"{name} 값이 올바르지 않습니다: {v}")


def to_float(v: str, name: str) -> float:
    try:
        return float(v)
    except Exception:
        raise RuntimeError(f"{name} 값이 올바르지 않습니다: {v}")


def show_config_dialog(fusion, project_name: str, timeline_name: str):
    ui = fusion.UIManager
    disp = bmd.UIDispatcher(ui)  # type: ignore[name-defined]

    win = disp.AddWindow(
        {
            "ID": "ResolveJobDialog",
            "WindowTitle": "Export Job to Linux Queue",
            "Geometry": [100, 100, 640, 300],
        },
        ui.VGroup(
            {"Spacing": 8, "Margin": 12},
            [
                ui.Label({"Text": f"Project: {project_name} / Timeline: {timeline_name}"}),
                ui.HGroup({"Spacing": 8}, [
                    ui.Label({"Text": "Codec Preset", "MinimumSize": [110, 0]}),
                    ui.ComboBox({"ID": "codec"}),
                ]),
                ui.HGroup({"Spacing": 8}, [
                    ui.Label({"Text": "Render Mode", "MinimumSize": [110, 0]}),
                    ui.ComboBox({"ID": "render_mode"}),
                ]),
                ui.HGroup({"Spacing": 8}, [
                    ui.Label({"Text": "Filename Mode", "MinimumSize": [110, 0]}),
                    ui.ComboBox({"ID": "fname_mode"}),
                ]),
                ui.HGroup({"Spacing": 8}, [
                    ui.Label({"Text": "Template", "MinimumSize": [110, 0]}),
                    ui.LineEdit({"ID": "fname_template", "Text": DEFAULTS["filename_template"]}),
                ]),
                ui.HGroup({"Spacing": 8}, [
                    ui.Label({"Text": "Manual Name", "MinimumSize": [110, 0]}),
                    ui.LineEdit({"ID": "manual_name", "Text": DEFAULTS["manual_filename"]}),
                ]),
                ui.HGroup({"Spacing": 8}, [
                    ui.Label({"Text": "Resolution", "MinimumSize": [110, 0]}),
                    ui.LineEdit({"ID": "width", "Text": DEFAULTS["width"], "PlaceholderText": "width"}),
                    ui.Label({"Text": "x"}),
                    ui.LineEdit({"ID": "height", "Text": DEFAULTS["height"], "PlaceholderText": "height"}),
                    ui.Label({"Text": "FPS"}),
                    ui.LineEdit({"ID": "fps", "Text": DEFAULTS["fps"], "PlaceholderText": "fps"}),
                ]),
                ui.Label({"Text": "Tokens: %{src_name} %{project} %{timeline} %{date} %{time}"}),
                ui.HGroup({"Weight": 0, "Spacing": 8}, [
                    ui.Button({"ID": "ok_btn", "Text": "Create Job"}),
                    ui.Button({"ID": "cancel_btn", "Text": "Cancel"}),
                ]),
            ],
        ),
    )

    items = win.GetItems()
    for p in CODEC_PRESETS:
        items["codec"].AddItem(p)
    items["codec"].CurrentText = DEFAULTS["codec_preset"]

    for r in RENDER_MODES:
        items["render_mode"].AddItem(r)
    items["render_mode"].CurrentText = DEFAULTS["render_mode"]

    for m in FILENAME_MODES:
        items["fname_mode"].AddItem(m)
    items["fname_mode"].CurrentText = DEFAULTS["filename_mode"]

    state = {"ok": False}

    def on_ok(ev):
        state["ok"] = True
        disp.ExitLoop()

    def on_cancel(ev):
        state["ok"] = False
        disp.ExitLoop()

    win.On.ok_btn.Clicked = on_ok
    win.On.cancel_btn.Clicked = on_cancel
    win.On.ResolveJobDialog.Close = on_cancel

    win.Show()
    disp.RunLoop()
    win.Hide()

    if not state["ok"]:
        return None

    return {
        "codec_preset": items["codec"].CurrentText,
        "render_mode": items["render_mode"].CurrentText,
        "filename_mode": items["fname_mode"].CurrentText,
        "filename_template": items["fname_template"].Text,
        "manual_filename": items["manual_name"].Text,
        "width": items["width"].Text,
        "height": items["height"].Text,
        "fps": items["fps"].Text,
    }


def build_job(project_name: str, timeline_name: str, input_files, output_filename: str, cfg):
    codec_preset = cfg["codec_preset"]
    if codec_preset not in CODEC_MAP:
        raise RuntimeError(f"지원하지 않는 codec preset: {codec_preset}")

    c = CODEC_MAP[codec_preset]
    job_id = f"resolve-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"

    return {
        "job_id": job_id,
        "created_at": now_iso(),
        "source": {
            "project": project_name,
            "timeline": timeline_name,
            "input_files": input_files,
        },
        "target": {
            "output_path": LINUX_OUT,
            "filename": output_filename,
            "container": c["container"],
        },
        "render": {
            "codec": c["codec"],
            "profile": c["profile"],
            "resolution": {
                "width": to_int(cfg["width"], "width"),
                "height": to_int(cfg["height"], "height"),
            },
            "fps": to_float(cfg["fps"], "fps"),
            "audio": c["audio"],
            "ffmpeg_args": c["ffmpeg_args"],
        },
        "routing": {"queue": "default", "priority": 50, "node_group": "docker-worker"},
        "metadata": {
            "reel": "UNKNOWN",
            "timecode_start": "00:00:00:00",
            "color_space": "Rec.709",
            "camera": "UNKNOWN",
            "notes": "Generated from Resolve timeline (UI)",
        },
    }


def save_job(job):
    os.makedirs(JOBS_DIR, exist_ok=True)
    path = os.path.join(JOBS_DIR, f"{job['job_id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)
    return path


def main():
    resolve = bmd.scriptapp("Resolve")  # type: ignore[name-defined]
    fusion = bmd.scriptapp("Fusion")    # type: ignore[name-defined]
    pm = resolve.GetProjectManager()

    project = pm.GetCurrentProject()
    if not project:
        raise RuntimeError("현재 Resolve 프로젝트를 찾을 수 없습니다.")

    timeline = project.GetCurrentTimeline()
    if not timeline:
        raise RuntimeError("현재 타임라인을 찾을 수 없습니다.")

    project_name = project.GetName()
    timeline_name = timeline.GetName()

    cfg = show_config_dialog(fusion, project_name, timeline_name)
    if not cfg:
        print("[CANCELLED] user cancelled")
        return

    input_files = collect_timeline_input_linux_paths(timeline)

    codec_preset = cfg["codec_preset"]
    if codec_preset not in CODEC_MAP:
        raise RuntimeError(f"지원하지 않는 codec preset: {codec_preset}")

    created = []
    render_mode = cfg.get("render_mode", "clip_each")

    if render_mode == "timeline_single":
        output_filename = build_output_filename(
            src_path=input_files[0],
            project_name=project_name,
            timeline_name=timeline_name,
            container=CODEC_MAP[codec_preset]["container"],
            mode=cfg["filename_mode"],
            template=cfg["filename_template"],
            manual=cfg["manual_filename"],
        )
        # 주의: 현재 Linux scheduler/worker는 input_files[0] 기반 처리.
        # timeline_single은 단일 잡으로만 묶어 전달.
        job = build_job(project_name, timeline_name, input_files, output_filename, cfg)
        job["metadata"]["render_scope"] = "timeline_single"
        path = save_job(job)
        created.append((path, job["target"]["filename"], f"clips={len(input_files)}"))
    else:
        for src in input_files:
            output_filename = build_output_filename(
                src_path=src,
                project_name=project_name,
                timeline_name=timeline_name,
                container=CODEC_MAP[codec_preset]["container"],
                mode=cfg["filename_mode"],
                template=cfg["filename_template"],
                manual=cfg["manual_filename"],
            )

            # 스케줄러가 source.input_files[0]를 사용하므로 클립별 단일 입력으로 job 생성
            job = build_job(project_name, timeline_name, [src], output_filename, cfg)
            job["metadata"]["render_scope"] = "clip_each"
            path = save_job(job)
            created.append((path, job["target"]["filename"], os.path.basename(src)))

    print(f"[OK] Job manifests created: {len(created)}")
    for p, out, src in created:
        print(f"[OK] {p} | input={src} | output={out}")
    print(f"[INFO] codec_preset={codec_preset} render_mode={render_mode}")


if __name__ == "__main__":
    main()
