import os
def get_database_uri():
    return os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/resume_db')
