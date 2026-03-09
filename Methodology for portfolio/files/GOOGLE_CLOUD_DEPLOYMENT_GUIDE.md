# 🚀 Deploy Streamlit Dashboard to Google Cloud - Complete Guide

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (5 Minutes)](#quick-start)
3. [Detailed Step-by-Step](#detailed-step-by-step)
4. [Configuration Options](#configuration-options)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)
7. [Cost Optimization](#cost-optimization)

---

## 📦 Prerequisites

### **1. Google Cloud Account**
- Sign up at: https://cloud.google.com/
- $300 free credits for new users
- Credit card required (won't be charged with free tier)

### **2. Install Google Cloud SDK**

**macOS:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

### **3. Verify Installation**
```bash
gcloud --version
```

### **4. Required Files**
```
deployment/
├── streamlit_dashboard.py    # Your Streamlit app
├── config.py                 # Configuration file
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container definition
├── .dockerignore            # Files to exclude
└── deploy_to_cloud_run.sh   # Deployment script
```

---

## ⚡ Quick Start (5 Minutes)

### **Option 1: Automated Deployment (Easiest)**

```bash
# 1. Initialize gcloud
gcloud init

# 2. Set your project ID in the script
# Edit deploy_to_cloud_run.sh and change:
# PROJECT_ID="your-gcp-project-id"

# 3. Make script executable
chmod +x deploy_to_cloud_run.sh

# 4. Run deployment
./deploy_to_cloud_run.sh
```

**Done!** Your dashboard will be live in ~5 minutes.

---

### **Option 2: Manual Deployment (Step-by-Step)**

```bash
# 1. Set variables
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="bayesian-dashboard"

# 2. Set project
gcloud config set project $PROJECT_ID

# 3. Enable APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# 4. Build and deploy
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated
```

---

## 📝 Detailed Step-by-Step

### **Step 1: Create Google Cloud Project**

1. Go to: https://console.cloud.google.com/
2. Click "New Project"
3. Name: "bayesian-dashboard" (or your choice)
4. Note your **Project ID** (e.g., `bayesian-dashboard-123456`)

---

### **Step 2: Set Up Local Environment**

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Verify
gcloud config get-value project
```

---

### **Step 3: Prepare Files**

**Create `requirements.txt`:**
```txt
streamlit==1.28.0
numpy==1.24.3
pandas==2.0.3
plotly==5.17.0
scipy==1.11.3
```

**Create `Dockerfile`:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY streamlit_dashboard.py .
COPY config.py .
RUN mkdir -p Results/visualizations Results/reports Results/logs
EXPOSE 8080
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

**Create `.dockerignore`:**
```
__pycache__/
*.pyc
.git/
*.md
Results/
*_test.py
*.ipynb
```

---

### **Step 4: Build Container**

```bash
# Build container image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/streamlit-dashboard

# This takes 2-3 minutes
```

---

### **Step 5: Deploy to Cloud Run**

```bash
gcloud run deploy bayesian-dashboard \
    --image gcr.io/YOUR_PROJECT_ID/streamlit-dashboard \
    --platform managed \
    --region us-central1 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --allow-unauthenticated \
    --port 8080
```

**Options explained:**
- `--memory 1Gi`: 1GB RAM (sufficient for Streamlit)
- `--cpu 1`: 1 CPU core
- `--max-instances 10`: Auto-scale up to 10 instances
- `--allow-unauthenticated`: Public access (no login required)

---

### **Step 6: Get Your URL**

```bash
gcloud run services describe bayesian-dashboard \
    --platform managed \
    --region us-central1 \
    --format 'value(status.url)'
```

**Output example:**
```
https://bayesian-dashboard-xxxxx-uc.a.run.app
```

---

## ⚙️ Configuration Options

### **Memory & CPU Options**

**Small (Light usage):**
```bash
--memory 512Mi --cpu 1
```

**Medium (Recommended):**
```bash
--memory 1Gi --cpu 1
```

**Large (Heavy traffic):**
```bash
--memory 2Gi --cpu 2
```

---

### **Auto-Scaling Options**

**Always running (fastest response):**
```bash
--min-instances 1 --max-instances 10
```

**Cost-optimized (scales to zero):**
```bash
--min-instances 0 --max-instances 10
```

---

### **Authentication Options**

**Public (no login):**
```bash
--allow-unauthenticated
```

**Private (requires Google login):**
```bash
--no-allow-unauthenticated
```

---

### **Environment Variables**

**Add custom environment variables:**
```bash
gcloud run deploy bayesian-dashboard \
    --set-env-vars="APP_ENV=production,DEBUG=false"
```

---

## 📊 Monitoring & Maintenance

### **View Logs**

```bash
# Stream logs in real-time
gcloud run services logs read bayesian-dashboard \
    --region us-central1 \
    --limit 50 \
    --follow
```

**Or view in console:**
https://console.cloud.google.com/run

---

### **Check Service Status**

```bash
gcloud run services describe bayesian-dashboard \
    --region us-central1
```

---

### **Update Deployment**

**After code changes:**

```bash
# Rebuild and redeploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/streamlit-dashboard

gcloud run deploy bayesian-dashboard \
    --image gcr.io/YOUR_PROJECT_ID/streamlit-dashboard \
    --region us-central1
```

**Or use the automated script:**
```bash
./deploy_to_cloud_run.sh
```

---

### **Rollback to Previous Version**

```bash
# List revisions
gcloud run revisions list --service bayesian-dashboard

# Rollback to specific revision
gcloud run services update-traffic bayesian-dashboard \
    --to-revisions REVISION-NAME=100
```

---

## 🐛 Troubleshooting

### **Issue: Build Fails**

**Check:**
```bash
# View build logs
gcloud builds list --limit 5

# Get detailed logs
gcloud builds log BUILD_ID
```

**Common fixes:**
- Verify `requirements.txt` versions are correct
- Check Dockerfile syntax
- Ensure all files exist (streamlit_dashboard.py, config.py)

---

### **Issue: Deployment Fails**

**Check:**
```bash
# View service logs
gcloud run services logs read bayesian-dashboard --limit 100
```

**Common fixes:**
- Verify port 8080 is exposed
- Check Streamlit starts correctly locally
- Ensure environment variables are set

---

### **Issue: 502 Bad Gateway**

**Cause:** App crashed on startup

**Fix:**
```bash
# Check logs for errors
gcloud run services logs read bayesian-dashboard --limit 50

# Common issues:
# - Missing dependencies in requirements.txt
# - Import errors
# - Port mismatch
```

---

### **Issue: Slow Cold Starts**

**Cause:** Container starts from scratch

**Fix:**
```bash
# Keep at least 1 instance running
gcloud run services update bayesian-dashboard \
    --min-instances 1
```

---

### **Issue: Out of Memory**

**Fix:**
```bash
# Increase memory allocation
gcloud run services update bayesian-dashboard \
    --memory 2Gi
```

---

## 💰 Cost Optimization

### **Pricing Overview**

**Cloud Run pricing (as of 2024):**
- **CPU:** $0.00002400 per vCPU-second
- **Memory:** $0.00000250 per GiB-second
- **Requests:** $0.40 per million requests
- **Free tier:** 2 million requests/month

**Example costs:**

**Low traffic (1000 requests/day):**
- ~30,000 requests/month
- Estimated: **$0.50 - $2/month** (within free tier)

**Medium traffic (10,000 requests/day):**
- ~300,000 requests/month
- Estimated: **$5 - $10/month**

**High traffic (100,000 requests/day):**
- ~3M requests/month
- Estimated: **$50 - $100/month**

---

### **Cost Optimization Tips**

**1. Scale to Zero:**
```bash
--min-instances 0
```
**Saves:** ~$5-10/month if idle

**2. Right-size Resources:**
```bash
# Start small
--memory 512Mi --cpu 1

# Monitor and adjust if needed
```

**3. Set Request Limits:**
```bash
--concurrency 80
```

**4. Use Regional Deployment:**
```bash
# Use cheaper regions
--region us-central1  # Generally cheaper
```

**5. Monitor Usage:**
```bash
# View usage in console
https://console.cloud.google.com/run
```

---

## 📋 Deployment Checklist

**Before deploying:**

- [ ] All files present (dashboard, config, requirements, Dockerfile)
- [ ] Tested locally: `streamlit run streamlit_dashboard.py`
- [ ] GCP project created and billing enabled
- [ ] gcloud CLI installed and authenticated
- [ ] Project ID set in deployment script

**After deploying:**

- [ ] Service URL accessible
- [ ] Dashboard loads without errors
- [ ] All features work (calculations, visualizations)
- [ ] Logs show no errors
- [ ] Response time acceptable (<2 seconds)

---

## 🔐 Security Best Practices

### **1. Add Authentication (Optional)**

```bash
# Require Google authentication
gcloud run services update bayesian-dashboard \
    --no-allow-unauthenticated
```

**Then add users:**
```bash
gcloud run services add-iam-policy-binding bayesian-dashboard \
    --member='user:alice@example.com' \
    --role='roles/run.invoker'
```

---

### **2. Custom Domain (Optional)**

```bash
# Map custom domain
gcloud run domain-mappings create \
    --service bayesian-dashboard \
    --domain dashboard.yourdomain.com
```

**Then add DNS records as shown in console**

---

### **3. HTTPS (Automatic)**

Cloud Run automatically provisions SSL certificates for HTTPS.

---

## 🎯 Quick Commands Reference

```bash
# Deploy
gcloud run deploy bayesian-dashboard --source .

# View logs
gcloud run services logs read bayesian-dashboard --follow

# Get URL
gcloud run services describe bayesian-dashboard --format 'value(status.url)'

# Update
gcloud run deploy bayesian-dashboard --image gcr.io/PROJECT/image

# Delete
gcloud run services delete bayesian-dashboard

# List services
gcloud run services list
```

---

## 📊 Alternative: Deploy to App Engine (Optional)

**If you prefer App Engine:**

**Create `app.yaml`:**
```yaml
runtime: python39
entrypoint: streamlit run streamlit_dashboard.py --server.port $PORT

automatic_scaling:
  min_instances: 0
  max_instances: 10
  target_cpu_utilization: 0.65

resources:
  cpu: 1
  memory_gb: 1
  disk_size_gb: 10
```

**Deploy:**
```bash
gcloud app deploy
```

---

## 🎉 Success!

**Your Streamlit dashboard is now live!**

**Next steps:**
1. Share URL with stakeholders
2. Monitor usage and costs
3. Iterate based on feedback
4. Scale as needed

**For support:**
- Google Cloud docs: https://cloud.google.com/run/docs
- Streamlit docs: https://docs.streamlit.io

---

## 📝 Summary

**What you deployed:**
- Streamlit dashboard on Google Cloud Run
- Auto-scaling serverless container
- HTTPS enabled by default
- Public or private access options

**Benefits:**
- ✅ Serverless (no server management)
- ✅ Auto-scaling (handles traffic spikes)
- ✅ Pay only for usage
- ✅ Built-in HTTPS
- ✅ Easy updates

**Typical costs:** $0.50 - $10/month for normal usage

---

**You're all set! Your Bayesian dashboard is production-ready on Google Cloud.** 🚀
