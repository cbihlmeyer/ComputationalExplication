
# Optional mount Google Drive;
# Content saves to Google Drive instead of temp Colab system
from google.colab import drive
drive.mount('/content/drive')


# --- Transcribe Loop from tiktokurl ---

!apt-get -y -qq install ffmpeg >/dev/null
!pip -q install yt-dlp faster-whisper tqdm pandas

import os, glob, subprocess, shlex
import pandas as pd
from tqdm import tqdm
from faster_whisper import WhisperModel


INPUT_XLSX  = "/content/id_url_for_trans.xlsx"   # tiktok urls
OUTPUT_XLSX = "/content/drive/MyDrive/tiktoktranscripts.xlsx"
AUDIOD  = "audio"

os.makedirs(AUDIOD, exist_ok=True)

df = pd.read_excel(INPUT_XLSX, dtype=str)
if "verbatimtranscript" not in df.columns: df["verbatimtranscript"] = ""
if "transcriptionstatus" not in df.columns: df["transcriptionstatus"] = ""

# --- Model: prefer GPU + FP16; fallback to CPU int8 ---
use_gpu = os.path.exists("/proc/driver/nvidia/version")
device = "cuda" if use_gpu else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
model_name = "medium.en"  # use "medium" for multilingual
model = WhisperModel(model_name, device=device, compute_type=compute_type)

def run(cmd):
    return subprocess.run(cmd if isinstance(cmd, list) else shlex.split(cmd),
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

def download_audio(page_url, out_prefix):
    # Download best audio without re-encoding
    tmpl = f"{out_prefix}.%(ext)s"
    cmd= [
        "yt-dlp",
        "-f", "bestaudio[ext=m4a]/bestaudio/best",
        "--no-part",
        "--concurrent-fragments", "8",
        "-N", "4",
        "-o", tmpl,
        page_url
    ]
    run(cmd)
    for f in glob.glob(f"{out_prefix}.*"):
        if os.path.isfile(f) and os.path.getsize(f) > 0:
            return f
    return ""

def transcribe(path):
    segments, info = model.transcribe(
        path,
        beam_size=1,
        vad_filter=True,
        language="en",
        condition_on_previous_text=False,
        temperature=0.0
    )
    return " ".join(s.text.strip() for s in segments if getattr(s, "text", "").strip())

for i, row in tqdm(df.iterrows(), total=len(df)):
    url = (row.get("tiktokurl") or "").strip()
    if not url:
        df.at[i, "transcriptionstatus"] = "missingurl"
        continue
    outp = os.path.join(AUDIOD, f"audio_{i:06d}")
    audio = download_audio(url, outp)
    if not audio:
        df.at[i, "transcriptionstatus"] = "download_failed"
        continue
    try:
        txt = (transcribe(audio) or "").strip()
        if txt:
            df.at[i, "verbatimtranscript"] = txt
            df.at[i, "transcriptionstatus"] = "success"
        else:
            df.at[i, "transcriptionstatus"] = "emptyaudio"
    except Exception as e:
        df.at[i, "transcriptionstatus"] = f"failed:{type(e).__name__}"
    finally:
        # cleanup audio file(s)
        for f in glob.glob(f"{outp}.*"):
            try: os.remove(f)
            except OSError: pass

df.to_excel(OUTPUT_XLSX, index=False)
print(f"✅ Transcription saved to {OUTPUT_XLSX}")
# Save to Google Drive
OUTPUT_XLSX = "/content/drive/MyDrive/tiktoktranscripts.xlsx"
