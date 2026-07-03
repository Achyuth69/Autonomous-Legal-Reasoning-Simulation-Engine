# Deployment Guide

This guide covers deploying the Autonomous Legal Reasoning Engine to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Security Considerations](#security-considerations)
6. [Monitoring & Maintenance](#monitoring--maintenance)

## Prerequisites

### Required Services
- PostgreSQL 15+
- Redis 7+
- OpenAI API key
- Domain name (for production)
- SSL certificate (for production)

### Optional Services
- Docker & Docker Compose
- Kubernetes cluster
- Cloud provider account (AWS/GCP/Azure)
- CDN (CloudFlare, AWS CloudFront)
- Email service (for notifications)

## Environment Configuration

### Backend Environment Variables

Create `backend/.env` for production:

```bash
# Application
APP_NAME="Autonomous Legal Reasoning Engine"
APP_VERSION="1.0.0"
DEBUG=False
ENVIRONMENT=production

# API
API_V1_PREFIX=/api/v1
SECRET_KEY=<generate-strong-secret-key>
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/legal_reasoning
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=20

# Redis
REDIS_URL=redis://redis-host:6379/0

# OpenAI
OPENAI_API_KEY=<your-production-api-key>
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=4000

# File Upload
MAX_UPLOAD_SIZE=20971520  # 20MB
UPLOAD_DIR=/app/data/uploads

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
CORS_ORIGINS=["https://yourdomain.com"]
CORS_ALLOW_CREDENTIALS=True

# Security
ALLOWED_HOSTS=["yourdomain.com"]
```

### Frontend Environment Variables

Create `frontend/.env.production`:

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## Docker Deployment

### 1. Build Images

```bash
# Build backend
cd backend
docker build -t legal-reasoning-backend:latest .

# Build frontend
cd frontend
docker build -t legal-reasoning-frontend:latest .
```

### 2. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: legal_reasoning
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - backend

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - backend

  backend:
    image: legal-reasoning-backend:latest
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/legal_reasoning
      REDIS_URL: redis://redis:6379/0
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: "False"
      ENVIRONMENT: production
    volumes:
      - backend_data:/app/data
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - backend
      - frontend

  frontend:
    image: legal-reasoning-frontend:latest
    environment:
      NEXT_PUBLIC_API_URL: https://api.yourdomain.com
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - frontend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    networks:
      - frontend

volumes:
  postgres_data:
  redis_data:
  backend_data:

networks:
  backend:
  frontend:
```

### 3. Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # Frontend
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

    # Backend API
    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### 4. Deploy

```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Initialize database
docker-compose -f docker-compose.prod.yml exec backend python -m app.db.init_db
```

## Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Create ECR Repositories**
```bash
aws ecr create-repository --repository-name legal-reasoning-backend
aws ecr create-repository --repository-name legal-reasoning-frontend
```

2. **Push Images**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag legal-reasoning-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/legal-reasoning-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/legal-reasoning-backend:latest

docker tag legal-reasoning-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/legal-reasoning-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/legal-reasoning-frontend:latest
```

3. **Set Up Infrastructure**
- Create RDS PostgreSQL instance
- Create ElastiCache Redis cluster
- Create ECS cluster
- Create Application Load Balancer
- Configure security groups
- Set up CloudWatch logs

4. **Deploy to ECS**
- Create task definitions
- Create services
- Configure auto-scaling

#### Using EC2

```bash
# Connect to EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone <your-repo-url>
cd Autonomous-Legal-Reasoning-Simulation-Engine
docker-compose -f docker-compose.prod.yml up -d
```

### GCP Deployment

#### Using Cloud Run

1. **Build and push to GCR**
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/legal-reasoning-backend backend/
gcloud builds submit --tag gcr.io/PROJECT-ID/legal-reasoning-frontend frontend/
```

2. **Deploy**
```bash
# Backend
gcloud run deploy legal-reasoning-backend \
  --image gcr.io/PROJECT-ID/legal-reasoning-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Frontend
gcloud run deploy legal-reasoning-frontend \
  --image gcr.io/PROJECT-ID/legal-reasoning-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Vercel (Frontend Only)

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## Security Considerations

### 1. API Keys & Secrets
- Use environment variables
- Never commit secrets to git
- Use secret management services (AWS Secrets Manager, GCP Secret Manager)
- Rotate API keys regularly

### 2. SSL/TLS
- Use Let's Encrypt for free SSL certificates
- Enable HTTPS only
- Configure HSTS headers

### 3. Database Security
- Use strong passwords
- Enable SSL connections
- Restrict network access
- Regular backups
- Encrypt at rest

### 4. Application Security
- Enable CSRF protection
- Set secure CORS policies
- Rate limiting
- Input validation
- SQL injection prevention (ORM)
- XSS prevention

### 5. Network Security
- Use VPC/private networks
- Configure security groups
- Enable WAF (Web Application Firewall)
- DDoS protection

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/api/v1/health

# Check logs
docker-compose logs -f backend
```

### Logging

Configure centralized logging:
- CloudWatch (AWS)
- Stackdriver (GCP)
- ELK Stack
- Datadog

### Metrics

Monitor:
- API response times
- Error rates
- Database connections
- Memory usage
- CPU usage
- OpenAI API usage

### Backups

```bash
# Database backup
docker-compose exec postgres pg_dump -U postgres legal_reasoning > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres legal_reasoning < backup.sql
```

### Updates

```bash
# Pull latest code
git pull origin master

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling

#### Horizontal Scaling
- Add more backend instances behind load balancer
- Use session storage in Redis
- Separate read/write database replicas

#### Vertical Scaling
- Increase container resources
- Optimize database queries
- Add database indices

## Troubleshooting

### Backend Issues

```bash
# Check logs
docker-compose logs backend

# Access container
docker-compose exec backend bash

# Test API
curl http://localhost:8000/api/v1/health
```

### Database Issues

```bash
# Check connections
docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Reset database
docker-compose exec backend python -m app.db.init_db
```

### Frontend Issues

```bash
# Check logs
docker-compose logs frontend

# Rebuild
docker-compose build frontend
docker-compose up -d frontend
```

## Cost Optimization

1. **OpenAI API**: Monitor usage, implement caching
2. **Database**: Use appropriate instance size, enable auto-scaling
3. **Compute**: Use spot instances, auto-scaling
4. **Storage**: Lifecycle policies, compression
5. **CDN**: Cache static assets

## Support

For deployment issues:
1. Check logs
2. Verify environment variables
3. Test network connectivity
4. Review security group rules
5. Open GitHub issue with details
