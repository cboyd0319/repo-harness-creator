#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

NO_ENV=0
for arg in "$@"; do
  case "$arg" in
    --no-env)
      NO_ENV=1
      ;;
    -h|--help)
      echo "Usage: ./init.sh [--no-env]"
      echo "  --no-env  clear common AI, cloud, and GitHub credentials for this run"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

if [ "$NO_ENV" = "1" ]; then
  unset ANTHROPIC_API_KEY ANTHROPIC_OAUTH_TOKEN OPENAI_API_KEY GEMINI_API_KEY
  unset GROQ_API_KEY CEREBRAS_API_KEY XAI_API_KEY OPENROUTER_API_KEY
  unset ZAI_API_KEY MISTRAL_API_KEY MINIMAX_API_KEY MINIMAX_CN_API_KEY
  unset AI_GATEWAY_API_KEY OPENCODE_API_KEY COPILOT_GITHUB_TOKEN
  unset GH_TOKEN GITHUB_TOKEN HF_TOKEN GOOGLE_APPLICATION_CREDENTIALS
  unset GOOGLE_CLOUD_PROJECT GCLOUD_PROJECT GOOGLE_CLOUD_LOCATION
  unset AWS_PROFILE AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
  unset AWS_REGION AWS_DEFAULT_REGION AWS_BEARER_TOKEN_BEDROCK
  unset AWS_CONTAINER_CREDENTIALS_RELATIVE_URI AWS_CONTAINER_CREDENTIALS_FULL_URI
  unset AWS_WEB_IDENTITY_TOKEN_FILE AZURE_OPENAI_API_KEY AZURE_OPENAI_BASE_URL
  unset AZURE_OPENAI_RESOURCE_NAME
  echo "== Running without common AI, cloud, or GitHub credentials =="
fi

export PYTHONPATH="src${PYTHONPATH:+:${PYTHONPATH}}"
PYTHON_BIN="${PYTHON:-}"
if [ -z "$PYTHON_BIN" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  else
    PYTHON_BIN="python"
  fi
fi

echo "== Doctor =="
"$PYTHON_BIN" -m harnessforge doctor

echo "== Compile =="
"$PYTHON_BIN" -m compileall src tests

echo "== Tests =="
"$PYTHON_BIN" -m unittest discover -s tests

echo "== Pin check =="
"$PYTHON_BIN" scripts/check_pins.py --root .

echo "== Self audit =="
"$PYTHON_BIN" -m harnessforge audit --target . --min-score 85
