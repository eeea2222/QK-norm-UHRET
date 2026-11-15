#!/usr/bin/env bash
# Resumable download of the pinned WT4 base weights (RikiyaT/Qwen3.5-0.8B-weight-space-programming @ d1671a17...).
# Expected sha256 (efe-T/WeightSeek-WT4 wt4.json base_weight_sha256): fd1e42acdd118ac1b300d37500fd2885e75f5a09de3a33010d802bf7f737b553
set -euo pipefail
cd "$(dirname "$0")"
URL="https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming/resolve/d1671a178705bcab7644806d23c535517f35723b/model.safetensors-00001-of-00001.safetensors"
for i in $(seq 1 50); do
  if curl -sL -C - --retry 5 --retry-delay 5 --speed-limit 1000 --speed-time 60 -o model.safetensors-00001-of-00001.safetensors "$URL"; then break; fi
  echo "retry $i"; sleep 5
done
sha256sum model.safetensors-00001-of-00001.safetensors
