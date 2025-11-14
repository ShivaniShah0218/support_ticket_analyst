FROM python:3.10-slim

# Do not run as root in production images; this keeps the example simple.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install pip and build tools if necessary. Keep image small on slim base.
RUN pip install --upgrade pip

# Copy only requirements first for better caching
COPY backend/requirements.txt /app/requirements.txt

# Install runtime dependencies and gunicorn (production WSGI)
RUN pip install --no-cache-dir -r /app/requirements.txt gunicorn

# Copy backend application code
COPY backend /app

# Configure Flask app location. The Flask app instance is `app` in `backend/app/routes.py`.
ENV FLASK_APP=app.routes:app

# Expose the port the app listens on
EXPOSE 5000

# Use gunicorn as the production server. Adjust worker count as needed for your CPU.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.routes:app", "--workers", "4", "--timeout", "120"]
