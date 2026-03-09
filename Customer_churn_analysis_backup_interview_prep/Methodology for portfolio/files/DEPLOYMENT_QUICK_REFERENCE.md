# 🚀 Quick Deployment Reference - Streamlit Dashboard

## ⚡ 3-Minute Deploy (Cloud Run)

```bash
# 1. Login
gcloud auth login

# 2. Set project
gcloud config set project YOUR_PROJECT_ID

# 3. Deploy (one command!)
gcloud run deploy bayesian-dashboard \
    --source . \
    --region us-central1 \
    --allow-unauthenticated
```

**Done!** Get your URL and visit your dashboard.

---

## 📋 Required Files

```
deployment/
├── streamlit_dashboard.py    ← Your app
├── config.py                 ← Config file
├── requirements.txt          ← Dependencies
├── Dockerfile               ← Container (optional)
└── .dockerignore            ← Exclude files
```

---

## 📦 Two Deployment Methods

### **Method 1: Cloud Run (Recommended)** ⭐

**Pros:**
- ✅ Easiest to deploy
- ✅ Auto-scaling
- ✅ Pay only for usage
- ✅ Scale to zero

**Deploy:**
```bash
gcloud run deploy bayesian-dashboard --source .
```

**Cost:** $0.50 - $5/month (typical usage)

---

### **Method 2: App Engine (Alternative)**

**Pros:**
- ✅ Integrated with GCP
- ✅ Good for long-running apps
- ✅ Simple configuration

**Deploy:**
```bash
gcloud app deploy
```

**Cost:** $5 - $20/month (always running)

---

## 🔧 Essential Commands

### **Deploy**
```bash
# Cloud Run (from source)
gcloud run deploy SERVICE_NAME --source .

# Cloud Run (from container)
gcloud run deploy SERVICE_NAME --image gcr.io/PROJECT/IMAGE

# App Engine
gcloud app deploy
```

### **View URL**
```bash
# Cloud Run
gcloud run services describe SERVICE_NAME --format 'value(status.url)'

# App Engine  
gcloud app browse
```

### **View Logs**
```bash
# Cloud Run
gcloud run services logs read SERVICE_NAME --follow

# App Engine
gcloud app logs tail -s default
```

### **Update**
```bash
# Just run deploy again
gcloud run deploy SERVICE_NAME --source .
```

### **Delete**
```bash
# Cloud Run
gcloud run services delete SERVICE_NAME

# App Engine
gcloud app services delete default
```

---

## 🐛 Troubleshooting

### **Build fails**
```bash
# Check build logs
gcloud builds list
gcloud builds log BUILD_ID
```

**Fix:** Check requirements.txt, Dockerfile syntax

---

### **502 Error**
```bash
# View app logs
gcloud run services logs read SERVICE_NAME --limit 50
```

**Fix:** App crashed - check Python errors in logs

---

### **Slow startup**
```bash
# Keep instance warm
gcloud run services update SERVICE_NAME --min-instances 1
```

---

### **Out of memory**
```bash
# Increase memory
gcloud run services update SERVICE_NAME --memory 2Gi
```

---

## 💰 Cost Estimates

**Cloud Run:**
| Traffic | Requests/Day | Cost/Month |
|---------|--------------|------------|
| Low | 1,000 | $0.50 - $2 |
| Medium | 10,000 | $5 - $10 |
| High | 100,000 | $50 - $100 |

**Free tier:** 2 million requests/month

---

## 🔐 Security Options

### **Public Access**
```bash
--allow-unauthenticated
```

### **Require Login**
```bash
--no-allow-unauthenticated

# Add specific user
gcloud run services add-iam-policy-binding SERVICE_NAME \
    --member='user:alice@example.com' \
    --role='roles/run.invoker'
```

---

## 📊 Monitoring

### **View in Console**
```
https://console.cloud.google.com/run
```

### **Check metrics**
- Request count
- Response time
- Error rate
- Memory usage

---

## 🎯 Deployment Checklist

**Before deploying:**
- [ ] Test locally: `streamlit run streamlit_dashboard.py`
- [ ] Check requirements.txt has all dependencies
- [ ] GCP project created
- [ ] Billing enabled
- [ ] gcloud CLI installed

**Deploy:**
- [ ] Run: `gcloud run deploy bayesian-dashboard --source .`
- [ ] Wait 2-3 minutes
- [ ] Get URL
- [ ] Test in browser

**After deploying:**
- [ ] Dashboard loads
- [ ] All features work
- [ ] Check logs for errors
- [ ] Note URL for sharing

---

## 📝 Common Configuration

### **Standard Config (Recommended)**
```bash
gcloud run deploy bayesian-dashboard \
    --source . \
    --region us-central1 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --allow-unauthenticated
```

### **Always Running (Faster Response)**
```bash
gcloud run deploy bayesian-dashboard \
    --source . \
    --region us-central1 \
    --memory 1Gi \
    --min-instances 1 \
    --max-instances 10
```

### **Cost-Optimized (Scale to Zero)**
```bash
gcloud run deploy bayesian-dashboard \
    --source . \
    --region us-central1 \
    --memory 512Mi \
    --min-instances 0 \
    --max-instances 5
```

---

## 🌍 Available Regions

**Americas:**
- `us-central1` (Iowa) - Cheapest
- `us-east1` (South Carolina)
- `us-west1` (Oregon)

**Europe:**
- `europe-west1` (Belgium)
- `europe-west2` (London)

**Asia:**
- `asia-east1` (Taiwan)
- `asia-northeast1` (Tokyo)

---

## 🔄 Update Workflow

**After code changes:**

```bash
# 1. Test locally
streamlit run streamlit_dashboard.py

# 2. Redeploy
gcloud run deploy bayesian-dashboard --source .

# 3. Verify
# Visit URL and test
```

**That's it!** Cloud Run rebuilds and redeploys automatically.

---

## 📞 Getting Help

**Documentation:**
- Cloud Run: https://cloud.google.com/run/docs
- Streamlit: https://docs.streamlit.io

**Community:**
- Stack Overflow: [google-cloud-run] tag
- Streamlit Forum: https://discuss.streamlit.io

**Support:**
- GCP Console: Submit support ticket
- Free tier: Community support only

---

## ✅ Success Checklist

**Your deployment is successful when:**
- [ ] URL is accessible
- [ ] Dashboard loads in <5 seconds
- [ ] All calculations work
- [ ] Visualizations display correctly
- [ ] No errors in logs
- [ ] Mobile-friendly (responsive)

---

## 🎯 Pro Tips

1. **Always test locally first**
   ```bash
   streamlit run streamlit_dashboard.py
   ```

2. **Use descriptive service names**
   - Good: `bayesian-dashboard`
   - Bad: `app1`, `test`

3. **Monitor costs**
   - Check billing dashboard weekly
   - Set up budget alerts

4. **Keep it simple**
   - Start with defaults
   - Optimize only if needed

5. **Version your deployments**
   - Use git tags
   - Document changes

---

## 🚀 Quick Start Summary

**Deploy in 3 commands:**

```bash
# 1. Login
gcloud auth login

# 2. Set project  
gcloud config set project YOUR_PROJECT_ID

# 3. Deploy
gcloud run deploy bayesian-dashboard --source . --allow-unauthenticated
```

**Get URL:**
```bash
gcloud run services describe bayesian-dashboard --format 'value(status.url)'
```

**Done!** Your dashboard is live. 🎉

---

**Remember: Cloud Run is serverless - you only pay when someone uses your dashboard!**
