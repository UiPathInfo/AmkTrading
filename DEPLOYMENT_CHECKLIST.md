# AMK Trading Platform - Deployment & Launch Checklist

## 🚀 Pre-Deployment Setup

### 1. Environment Preparation

- [ ] Create `.env` file in backend directory
- [ ] Set Python version: 3.8+ (recommend 3.10+)
- [ ] Set Node version: 16+ (recommend 18+)
- [ ] Install system dependencies (Ubuntu/Linux):
  ```bash
  sudo apt-get update
  sudo apt-get install python3-dev python3-venv build-essential
  ```

### 2. Backend Setup

```bash
# Create virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create stock_list.ods file with tickers in 'Ticker' column
# (Required for screener to work)

# Test backend
python main.py
# Should start on http://localhost:8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install

# Create .env file with API endpoint
echo "VITE_API_BASE=http://localhost:8000" > .env.local

# Test frontend
npm run dev
# Should start on http://localhost:5173
```

### 4. Verification Tests

- [ ] Backend health check: `curl http://localhost:8000/api/health`
  - Expected: `{"status":"ok","version":"2.0.0"}`

- [ ] API config: `curl http://localhost:8000/api/config`
  - Expected: Configuration object returned

- [ ] Frontend loads: Open http://localhost:5173 in browser
  - Expected: UI loads without errors

- [ ] Run screener: Open frontend → Screener tab → Run Screener
  - Expected: Stock analysis results displayed

---

## 📦 Production Deployment

### Option 1: Docker Deployment

#### Backend Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY backend/stock_list.ods .

CMD ["python", "main.py"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:18-alpine AS build

WORKDIR /app/frontend

COPY frontend/package*.json .
RUN npm install

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/frontend/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./backend/trading_journal.json:/app/backend/trading_journal.json

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE=http://backend:8000

volumes:
  trading_journal:
```

### Option 2: Cloud Deployment (Render/Heroku)

#### Backend Deployment (Render)

1. Create `Procfile`:
   ```
   web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT
   ```

2. Update requirements.txt with:
   ```
   gunicorn>=20.0.0
   ```

3. Deploy to Render:
   - Connect GitHub repository
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - Set environment variables if needed

#### Frontend Deployment (Vercel)

1. Create `vercel.json`:
   ```json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "frontend/dist",
     "framework": "vite"
   }
   ```

2. Deploy to Vercel:
   - Connect GitHub repository
   - Framework: Vite
   - Build command: `npm run build`
   - Output directory: `frontend/dist`
   - Set env var: `VITE_API_BASE=<backend_url>`

### Option 3: Self-Hosted Server

```bash
# SSH into server
ssh user@your-server-ip

# Install dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv nginx supervisor postgresql

# Clone repository
git clone https://github.com/yourusername/AmkTrading.git
cd AmkTrading

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup supervisor for backend
sudo nano /etc/supervisor/conf.d/amktrading.conf
# Add:
# [program:amktrading]
# command=/home/user/AmkTrading/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
# directory=/home/user/AmkTrading/backend
# user=www-data
# autostart=true
# autorestart=true

# Setup nginx for frontend
cd ../frontend
npm install
npm run build

sudo nano /etc/nginx/sites-available/amktrading
# Configure reverse proxy and static files

sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start amktrading
```

---

## 🔧 Production Configuration

### Backend (.env file)
```
# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=false

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/amktrading
JOURNAL_PATH=/data/trading_journal.json

# Cache Configuration
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# ML Configuration
ML_MODEL_PATH=/models/conviction_model.pkl
TRAINING_DATA_DAYS=252

# API Configuration
API_TITLE=AMK Trading API
API_VERSION=2.0.0
CORS_ORIGINS=["https://yourdomain.com"]
```

### Frontend (.env.production)
```
VITE_API_BASE=https://api.yourdomain.com
VITE_APP_NAME=AMK Trading
VITE_ENVIRONMENT=production
```

---

## 📊 Performance Optimization

### Backend Optimization

- [ ] Enable response compression
- [ ] Add response caching headers
- [ ] Implement database connection pooling
- [ ] Add rate limiting (50 req/min per IP)
- [ ] Optimize indicator calculations with caching
- [ ] Use async/await throughout
- [ ] Add database indices on trade table

```python
# Add to main.py
from fastapi.middleware.gzip import GZIPMiddleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

### Frontend Optimization

- [ ] Enable gzip compression
- [ ] Implement lazy loading
- [ ] Minify CSS/JavaScript
- [ ] Optimize images
- [ ] Use service workers for PWA
- [ ] Enable browser caching

```bash
# Vite automatically optimizes on build
npm run build

# Check bundle size
npm run preview
```

---

## 🔒 Security Hardening

### Backend Security

- [ ] Set strong database password (32+ chars)
- [ ] Enable HTTPS only (SSL certificate)
- [ ] Configure CORS properly (specific origins)
- [ ] Implement rate limiting
- [ ] Add request validation
- [ ] Sanitize all inputs
- [ ] Use environment variables for secrets
- [ ] Enable security headers

```python
# Add to main.py
from fastapi.middleware import trustedhost

app.add_middleware(
    trustedhost.TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "www.yourdomain.com"]
)
```

### Frontend Security

- [ ] Enable HTTPS
- [ ] Configure Content Security Policy
- [ ] Validate all API responses
- [ ] Sanitize user inputs
- [ ] No sensitive data in localStorage
- [ ] Use secure cookies (HttpOnly, Secure)

### Database Security

- [ ] Enable encryption at rest
- [ ] Configure SSL for connections
- [ ] Set up database backups (daily)
- [ ] Use read-only replicas for analytics
- [ ] Monitor for unauthorized access
- [ ] Regular security updates

---

## 📈 Monitoring & Logging

### Application Monitoring

```bash
# Install monitoring stack
docker run -d -p 9090:9090 prom/prometheus
docker run -d -p 3000:3000 grafana/grafana

# Configure Prometheus scraping
# Configure Grafana dashboards
```

### Logging Setup

```python
# Backend logging configuration
import logging
from logging.handlers import RotatingFileHandler

# Log API requests
# Log errors with full traceback
# Log performance metrics
```

### Alerting

- [ ] Setup alerts for high error rates (>5% of requests)
- [ ] Alert on API response time (>1000ms)
- [ ] Alert on database connection failures
- [ ] Alert on disk space (>90% full)
- [ ] Alert on memory usage (>85%)

---

## 🧪 Testing Before Live

### Backend Testing

```bash
# Unit tests for indicators
python -m pytest backend/test_indicators.py

# Integration tests for API
python -m pytest backend/test_api.py

# Load testing
locust -f backend/locustfile.py
```

### Frontend Testing

```bash
# UI component tests
npm test

# E2E testing
npm run test:e2e

# Visual regression
npm run test:visual
```

### Screener Functionality

- [ ] Test with 5 stocks - verify results
- [ ] Test with 50 stocks - check performance
- [ ] Test with invalid ticker - error handling
- [ ] Test with no market data - graceful failure
- [ ] Test concurrent requests - no race conditions

### Journal Functionality

- [ ] Create trade entry - verify saved
- [ ] Update trade exit - verify P&L calculated
- [ ] Delete trade - verify removed
- [ ] Export journal - verify JSON format
- [ ] Calculate metrics - verify accuracy

### Analytics Functionality

- [ ] Win rate calculation - verify accuracy
- [ ] Profit factor - verify formula
- [ ] Max drawdown - verify calculation
- [ ] Symbol breakdown - verify grouping
- [ ] Setup breakdown - verify classification

---

## 📋 Post-Deployment Checklist

### Day 1 (Launch Day)

- [ ] Verify all endpoints responding
- [ ] Check frontend loads without errors
- [ ] Run screener - verify results displayed
- [ ] Create test trade - verify logging
- [ ] Check performance metrics - responsive
- [ ] Monitor error logs - no critical errors
- [ ] Test on mobile device - responsive
- [ ] Verify database backups running
- [ ] Check SSL certificate valid
- [ ] Monitor API response times

### Week 1

- [ ] Monitor for crashes or errors
- [ ] Check database size and growth
- [ ] Verify backup completion
- [ ] Performance metrics within targets
- [ ] User feedback collection
- [ ] Bug fixes and patches
- [ ] Optimize slow endpoints
- [ ] Security audit

### Month 1

- [ ] Full system stability
- [ ] Performance optimization complete
- [ ] User adoption metrics
- [ ] Feature request analysis
- [ ] Financial metrics tracking
- [ ] Plan Phase 2 enhancements
- [ ] Community feedback integration

---

## 🆘 Troubleshooting Guide

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.8+

# Verify dependencies installed
pip list | grep fastapi

# Check port not in use
lsof -i :8000

# Check for syntax errors
python -m py_compile main.py

# Review error logs
tail -f error.log
```

### API Returns 500 Errors

- [ ] Check database connection
- [ ] Verify environment variables set
- [ ] Check file permissions
- [ ] Review application logs
- [ ] Test with curl directly
- [ ] Check stock_list.ods exists

### Frontend Won't Connect to Backend

```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check CORS configuration
# Check API_BASE URL correct
# Check network connectivity
# Check browser console for errors
```

### Slow Performance

- [ ] Check CPU/Memory usage
- [ ] Review slow queries with logging
- [ ] Optimize database indices
- [ ] Enable response caching
- [ ] Check network latency
- [ ] Profile with profiling tools

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

**Daily**:
- Monitor error logs
- Check API response times
- Verify database health

**Weekly**:
- Review performance metrics
- Check disk space
- Verify backups completed
- Review security logs

**Monthly**:
- Update dependencies
- Security patches
- Performance optimization
- Feature releases

**Quarterly**:
- Full security audit
- Database maintenance
- Disaster recovery test
- Strategic review

---

## 📚 Documentation References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## ✅ Final Pre-Launch Checklist

- [ ] Backend code reviewed and tested
- [ ] Frontend responsive on all devices
- [ ] All 19 API endpoints functional
- [ ] Trading journal system operational
- [ ] Performance metrics calculated correctly
- [ ] Documentation complete and accurate
- [ ] Security hardening complete
- [ ] Backups and disaster recovery tested
- [ ] Monitoring and logging configured
- [ ] Team trained on platform
- [ ] Support procedures documented
- [ ] Launch communication plan ready

---

**Status**: Ready for Deployment  
**Version**: 2.0.0  
**Last Updated**: 31 December 2025  

🚀 **The AMK Trading Platform is ready to go live!**
