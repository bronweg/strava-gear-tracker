# Deployment Guide

This guide covers deploying the Bike Equipment Tracker application to production.

## Local Development

### Running Locally

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
   ```

2. **Set up environment variables:**
   ```bash
   python create_env.py
   # Or manually edit .env file
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open http://localhost:5000 in your browser

## Production Deployment

### Option 1: Deploy with Gunicorn (Recommended for Linux/macOS)

1. **Install Gunicorn:**
   ```bash
   pip install gunicorn
   ```

2. **Update requirements.txt:**
   ```bash
   echo "gunicorn==21.2.0" >> requirements.txt
   ```

3. **Run with Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

### Option 2: Deploy with Waitress (Cross-platform)

1. **Install Waitress:**
   ```bash
   pip install waitress
   ```

2. **Create a production server file** (`wsgi.py`):
   ```python
   from waitress import serve
   from app import app
   
   if __name__ == '__main__':
       serve(app, host='0.0.0.0', port=8000)
   ```

3. **Run:**
   ```bash
   python wsgi.py
   ```

### Option 3: Deploy to Heroku

1. **Create Procfile:**
   ```
   web: gunicorn app:app
   ```

2. **Create runtime.txt:**
   ```
   python-3.9.6
   ```

3. **Deploy:**
   ```bash
   heroku create your-app-name
   heroku config:set FLASK_SECRET_KEY=your-secret-key
   heroku config:set STRAVA_CLIENT_ID=your-client-id
   heroku config:set STRAVA_CLIENT_SECRET=your-client-secret
   heroku config:set STRAVA_REDIRECT_URI=https://your-app-name.herokuapp.com/auth/callback
   git push heroku main
   ```

### Option 4: Deploy to Railway

1. **Create account at railway.app**
2. **Connect your GitHub repository**
3. **Add environment variables in Railway dashboard:**
   - `FLASK_SECRET_KEY`
   - `STRAVA_CLIENT_ID`
   - `STRAVA_CLIENT_SECRET`
   - `STRAVA_REDIRECT_URI`
4. **Deploy automatically on push**

### Option 5: Deploy with Docker

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 5000
   
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

2. **Build and run:**
   ```bash
   docker build -t bike-tracker .
   docker run -p 5000:5000 --env-file .env bike-tracker
   ```

## Production Considerations

### Security

1. **Use HTTPS in production** - Update `STRAVA_REDIRECT_URI` to use `https://`
2. **Set strong SECRET_KEY** - Use `secrets.token_hex(32)` to generate
3. **Use PostgreSQL** instead of SQLite for production
4. **Enable CSRF protection** (already included with Flask-WTF if you add it)
5. **Set secure session cookies:**
   ```python
   app.config['SESSION_COOKIE_SECURE'] = True
   app.config['SESSION_COOKIE_HTTPONLY'] = True
   app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
   ```

### Database

For production, use PostgreSQL instead of SQLite:

1. **Install psycopg2:**
   ```bash
   pip install psycopg2-binary
   ```

2. **Update DATABASE_URL in .env:**
   ```
   DATABASE_URL=postgresql://user:password@localhost/bike_tracker
   ```

### Performance

1. **Use a reverse proxy** (Nginx or Apache)
2. **Enable caching** for static files
3. **Use a CDN** for Bootstrap and other static assets
4. **Implement rate limiting** to prevent API abuse
5. **Add database connection pooling**

### Monitoring

1. **Add logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

2. **Monitor Strava API usage** to avoid rate limits
3. **Set up error tracking** (e.g., Sentry)
4. **Monitor database performance**

### Backup

1. **Regular database backups**
2. **Backup .env file securely**
3. **Version control** (but exclude .env and database files)

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_SECRET_KEY` | Flask session secret | `abc123...` |
| `STRAVA_CLIENT_ID` | Strava API Client ID | `12345` |
| `STRAVA_CLIENT_SECRET` | Strava API Client Secret | `abc123...` |
| `STRAVA_REDIRECT_URI` | OAuth callback URL | `http://localhost:5000/auth/callback` |
| `DATABASE_URL` | Database connection string | `sqlite:///bike_tracker.db` |

## Troubleshooting

### Database Issues

If you encounter database errors, try:
```bash
rm bike_tracker.db  # Delete old database
python app.py  # Recreate database
```

### Strava OAuth Issues

1. Check that redirect URI matches exactly in Strava API settings
2. Ensure callback domain is set correctly
3. Verify client ID and secret are correct

### Port Already in Use

Change the port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

