# Deployment Protocol — Bayesian A/B Test Dashboard → Google Cloud Run

This document is the step-by-step protocol for deploying `streamlit_dashboard.py` to
Google Cloud Run. It assumes you are running from the `Phase_5_Depolyment guide/`
directory.

> ⚠️ **Blocker before deploying:** the dashboard currently crashes on launch due to an
> invalid slider default (`value=26.5` outside `min=50/max=90`). See the Code Review
> section in the chat / `CODE_REVIEW.md`. Fix that first, then run a local smoke test
> (Step 2) before pushing to the cloud.

---

## 0. Prerequisites (one-time)

| Requirement | Check / Install |
|-------------|-----------------|
| Google Cloud SDK (`gcloud`) | `gcloud version` — else https://cloud.google.com/sdk/docs/install |
| Docker (for local build only) | `docker version` — optional; Cloud Build does not need it |
| A GCP project with billing enabled | https://console.cloud.google.com/billing |
| Authenticated CLI | `gcloud auth login` |

Set the active project (replace with your own ID):

```bash
export PROJECT_ID="sacred-woods-499215-h8"   # currently deployed project
export REGION="us-central1"
export SERVICE_NAME="bayesian-dashboard"
gcloud config set project "$PROJECT_ID"
```

> **Live service:** https://bayesian-dashboard-56ihiiew2a-uc.a.run.app
> (deployed to `sacred-woods-499215-h8`, region `us-central1`, public access)

---

## 1. Enable required APIs (one-time per project)

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

> `containerregistry.googleapis.com` (gcr.io) still works but is deprecated. The
> commands below use Artifact Registry, the current standard.

Create an Artifact Registry repo (one-time):

```bash
gcloud artifacts repositories create dashboards \
  --repository-format=docker \
  --location="$REGION" \
  --description="Streamlit dashboards"
```

---

## 2. Local smoke test (MANDATORY before every deploy)

Never deploy code that has not started locally. Cold-start failures on Cloud Run are
slow and expensive to debug.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_dashboard.py
# open http://localhost:8501 — click through all 4 tabs, especially with
# "Number of Treatment Arms" = 2 (a known edge case, see code review)
```

Optionally test the actual container locally (catches Docker-only issues):

```bash
docker build -t dashboard-local .
docker run -e PORT=8080 -p 8080:8080 dashboard-local
# open http://localhost:8080
```

---

## 3. Build the image with Cloud Build

```bash
export IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/dashboards/${SERVICE_NAME}:$(date +%Y%m%d-%H%M%S)"
gcloud builds submit --tag "$IMAGE_TAG" .
```

Using a timestamped tag (instead of `:latest`) gives you an immutable, rollback-able
history. Note the tag — you'll need it for deploy and rollback.

---

## 4. Deploy to Cloud Run

```bash
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_TAG" \
  --region "$REGION" \
  --platform managed \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --concurrency 20 \
  --timeout 300 \
  --port 8080 \
  --allow-unauthenticated
```

| Flag | Why |
|------|-----|
| `--min-instances 0` | Scale to zero = no cost when idle (accepts ~10 s cold start). |
| `--max-instances 5` | Caps run-away cost; a portfolio demo never needs more. |
| `--concurrency 20` | Streamlit holds a session per user; keep this modest. |
| `--allow-unauthenticated` | Public demo. **Remove for any non-public use** (see §7). |

---

## 5. Verify the deployment

```bash
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" --format 'value(status.url)')
echo "$SERVICE_URL"
curl -fsS "${SERVICE_URL}/_stcore/health" && echo " — healthy"
```

Then open `$SERVICE_URL` in a browser and click through all four tabs. First request
takes ~10–15 s (cold start); this is expected with `min-instances 0`.

---

## 6. Rollback (if a deploy goes bad)

Cloud Run keeps every revision. To shift 100% of traffic back to the previous good one:

```bash
gcloud run revisions list --service "$SERVICE_NAME" --region "$REGION"
gcloud run services update-traffic "$SERVICE_NAME" \
  --region "$REGION" \
  --to-revisions <PREVIOUS_REVISION_NAME>=100
```

---

## 7. Security notes

- **`--allow-unauthenticated` makes the app fully public.** That is fine for a portfolio
  demo. For anything private, drop the flag and grant access explicitly:
  ```bash
  gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --region "$REGION" \
    --member="user:you@example.com" \
    --role="roles/run.invoker"
  ```
- **IAM least privilege.** The existing `deploy_to_cloud_run.sh` grants
  `roles/storage.admin` to the Compute and Cloud Build service accounts. That is broader
  than needed. Prefer `roles/artifactregistry.writer` for the build account and remove
  `storage.admin` once builds succeed.
- **No secrets in the image.** This app has none today; if you add any (API keys, DB
  creds), inject them with `--set-secrets` from Secret Manager, never via `ENV` in the
  Dockerfile.

---

## 8. Teardown (stop billing)

```bash
gcloud run services delete "$SERVICE_NAME" --region "$REGION"
# optional: remove old images
gcloud artifacts docker images list "${REGION}-docker.pkg.dev/${PROJECT_ID}/dashboards"
```

---

## Quick reference — full deploy in 3 commands

```bash
gcloud config set project "$PROJECT_ID"
gcloud builds submit --tag "$IMAGE_TAG" .
gcloud run deploy "$SERVICE_NAME" --image "$IMAGE_TAG" --region "$REGION" \
  --memory 1Gi --max-instances 5 --port 8080 --allow-unauthenticated
```
