# Railway Deployment Guide

## Quick Setup

Since you cannot deploy directly from GitHub, you'll need to deploy manually via Railway CLI.

### Prerequisites
- Railway account (free tier available)
- Railway CLI installed

### Step 1: Install Railway CLI

```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Or using npm
npm install -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

### Step 3: Create a New Project

```bash
cd library-management-system
railway init
```

### Step 4: Add PostgreSQL Database

```bash
railway add --database postgresql
```

### Step 5: Set Environment Variables

Railway will automatically set `DATABASE_URL` for PostgreSQL. You need to add these:

```bash
railway variables set DEBUG=False
railway variables set DJANGO_SETTINGS_MODULE=config.settings.production
railway variables set ALLOWED_HOSTS=.railway.app
railway variables set SECRET_KEY=your-generated-secret-key
```

**Generate a secret key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 6: Deploy

```bash
railway up
```

### Step 7: Run Migrations (Optional - already in build command)

If migrations didn't run automatically:
```bash
railway run python manage.py migrate
railway run python manage.py setup_groups
```

### Step 8: Get Your URL

```bash
railway domain
```

Or create a custom domain in the Railway dashboard.

## Configuration Files Created

- **`railway.json`**: Railway service configuration
- **`nixpacks.toml`**: Build configuration with Python 3.11 and PostgreSQL
- **`Procfile`**: Process definitions for web server and release phase

## Environment Variables Needed

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | Auto-set by Railway | PostgreSQL connection string |
| `DEBUG` | `False` | Production mode |
| `SECRET_KEY` | Generate new key | Django secret key |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` | Settings module |
| `ALLOWED_HOSTS` | `.railway.app` | Allowed hosts (update with your domain) |

## Alternative: Deploy via Dashboard

If you later want to connect GitHub:

1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Add PostgreSQL database
4. Click "Deploy from GitHub repo"
5. Connect your GitHub account
6. Select your repository
7. Set environment variables in the dashboard

## Troubleshooting

### Build Fails
- Check logs: `railway logs`
- Ensure all dependencies are in `requirements.txt`

### Database Connection Issues
- Verify `DATABASE_URL` is set: `railway variables`
- Check PostgreSQL service is running

### Static Files Not Loading
- Verify `collectstatic` ran during build
- Check `STATIC_ROOT` in settings

## Useful Commands

```bash
# View logs
railway logs

# Open Railway dashboard
railway open

# Connect to database
railway connect postgresql

# View all environment variables
railway variables

# Run Django management commands
railway run python manage.py <command>
```

## Cost

Railway offers:
- **Free Tier**: $5 worth of usage per month
- **Hobby Plan**: $5/month for personal projects
- No credit card required for trial

This is much more generous than Render's free tier limitations.
