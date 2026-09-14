#!/bin/bash
# DevPortal Deployment Script
# Supports multiple deployment targets

set -e

TARGET="${1:-github}"
BRANCH="${2:-main}"

echo "============================================"
echo "  DevPortal Deployment"
echo "============================================"
echo ""

case "$TARGET" in
    github)
        echo "Deploying to GitHub Pages..."
        echo "Branch: $BRANCH"
        
        # Check for uncommitted changes
        if ! git diff --quiet; then
            echo "Warning: You have uncommitted changes."
            read -p "Continue anyway? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
        
        # Push to trigger GitHub Pages
        git push origin "$BRANCH"
        echo ""
        echo "Deployment triggered. Check GitHub Actions for status."
        echo "Site will be available at: https://itsPremkumar.github.io/developer-portal"
        ;;
    
    netlify)
        echo "Deploying to Netlify..."
        
        if command -v netlify &> /dev/null; then
            netlify deploy --prod
        else
            echo "Installing Netlify CLI..."
            npm install -g netlify-cli
            netlify deploy --prod
        fi
        ;;
    
    vercel)
        echo "Deploying to Vercel..."
        
        if command -v vercel &> /dev/null; then
            vercel --prod
        else
            echo "Installing Vercel CLI..."
            npm install -g vercel
            vercel --prod
        fi
        ;;
    
    docker)
        echo "Building Docker image..."
        docker build -t devportal:latest .
        
        echo "Running container..."
        docker run -d -p 8080:80 --name devportal devportal:latest
        
        echo "DevPortal running at http://localhost:8080"
        ;;
    
    nginx)
        echo "Deploying to local Nginx..."
        
        read -p "Enter deployment path (default: /var/www/devportal): " DEPLOY_PATH
        DEPLOY_PATH="${DEPLOY_PATH:-/var/www/devportal}"
        
        sudo mkdir -p "$DEPLOY_PATH"
        sudo cp -r ./* "$DEPLOY_PATH/"
        sudo chown -R www-data:www-data "$DEPLOY_PATH"
        
        echo "Files copied to $DEPLOY_PATH"
        echo "Add Nginx config and reload:"
        echo "  sudo nginx -s reload"
        ;;
    
    *)
        echo "Unknown target: $TARGET"
        echo "Usage: $0 [github|netlify|vercel|docker|nginx] [branch]"
        exit 1
        ;;
esac

echo ""
echo "============================================"
echo "  Deployment Complete"
echo "============================================"
