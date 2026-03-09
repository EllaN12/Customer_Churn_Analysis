#!/bin/bash

# Deploy Streamlit Dashboard to Google Cloud Run
# This script automates the deployment process

set -e  # Exit on error

# ============================================================================
# CONFIGURATION
# ============================================================================

# Project configuration
PROJECT_ID="symmetric-ion-489004-b3"            
REGION="us-central1"                          # or your preferred region
SERVICE_NAME="bayesian-dashboard"
IMAGE_NAME="streamlit-bayesian-dashboard"

# Resource configuration
MEMORY="1Gi"                                  # Memory allocation
CPU="1"                                       # CPU allocation
MAX_INSTANCES="10"                            # Auto-scaling limit
MIN_INSTANCES="0"                             # Can scale to zero

# ============================================================================
# COLORS FOR OUTPUT
# ============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# ============================================================================
# GRANT REQUIRED ROLES AND PERMISSIONS TO SERVICE ACCOUNT
# ============================================================================

PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')

# Grant all needed permissions to Compute Engine service account
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

# Grant to Cloud Build service account too
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

echo "✅ All permissions granted! Retry deployment now"


# ============================================================================
# PRE-DEPLOYMENT CHECKS
# ============================================================================

print_step "Starting deployment process..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
print_success "gcloud CLI found"

# Check if required files exist
if [ ! -f "streamlit_dashboard.py" ]; then
    print_error "streamlit_dashboard.py not found in current directory"
    exit 1
fi
print_success "streamlit_dashboard.py found"

if [ ! -f "Dockerfile" ]; then
    print_error "Dockerfile not found"
    exit 1
fi
print_success "Dockerfile found"

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
    exit 1
fi
print_success "requirements.txt found"

# Check if config.py exists
if [ ! -f "config.py" ]; then
    print_warning "config.py not found - creating minimal version"
    cat > config.py << 'EOF'
# Minimal config.py for deployment
import os

results_dir = os.path.join(os.getcwd(), 'Results')
visualizations_dir = os.path.join(results_dir, 'visualizations')
reports_dir = os.path.join(results_dir, 'reports')
logs_dir = os.path.join(results_dir, 'logs')

def get_visualization_path(filename):
    os.makedirs(visualizations_dir, exist_ok=True)
    return os.path.join(visualizations_dir, filename)

def get_report_path(filename):
    os.makedirs(reports_dir, exist_ok=True)
    return os.path.join(reports_dir, filename)

def get_log_path(filename):
    os.makedirs(logs_dir, exist_ok=True)
    return os.path.join(logs_dir, filename)
EOF
    print_success "Created minimal config.py"
fi

# ============================================================================
# SET GCP PROJECT
# ============================================================================

print_step "Setting GCP project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

if [ $? -ne 0 ]; then
    print_error "Failed to set project. Please check PROJECT_ID."
    exit 1
fi
print_success "Project set successfully"

# ============================================================================
# ENABLE REQUIRED APIs
# ============================================================================

print_step "Enabling required Google Cloud APIs..."

gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

print_success "APIs enabled"



# ============================================================================
# BUILD CONTAINER IMAGE
# ============================================================================

print_step "Building container image with Cloud Build..."

IMAGE_TAG="gcr.io/${PROJECT_ID}/${IMAGE_NAME}:latest"

gcloud builds submit --tag $IMAGE_TAG .

if [ $? -ne 0 ]; then
    print_error "Container build failed"
    exit 1
fi
print_success "Container image built: $IMAGE_TAG"

# ============================================================================
# DEPLOY TO CLOUD RUN
# ============================================================================

print_step "Deploying to Cloud Run..."

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --platform managed \
    --region $REGION \
    --memory $MEMORY \
    --cpu $CPU \
    --min-instances $MIN_INSTANCES \
    --max-instances $MAX_INSTANCES \
    --allow-unauthenticated \
    --port 8080

if [ $? -ne 0 ]; then
    print_error "Deployment failed"
    exit 1
fi

# ============================================================================
# GET SERVICE URL
# ============================================================================

print_success "Deployment complete!"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format 'value(status.url)')

echo ""
echo "========================================="
echo "  Deployment Summary"
echo "========================================="
echo "Service Name: $SERVICE_NAME"
echo "Region:       $REGION"
echo "Image:        $IMAGE_TAG"
echo "URL:          $SERVICE_URL"
echo "========================================="
echo ""
print_success "Your Streamlit dashboard is live at:"
echo -e "${GREEN}$SERVICE_URL${NC}"
echo ""
print_warning "Note: First request may take 10-15 seconds (cold start)"
echo ""

# ============================================================================
# OPTIONAL: OPEN IN BROWSER
# ============================================================================

read -p "Open dashboard in browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open $SERVICE_URL
    elif command -v open &> /dev/null; then
        open $SERVICE_URL
    else
        print_warning "Cannot auto-open browser. Please visit: $SERVICE_URL"
    fi
fi

print_success "Deployment script completed successfully!"
