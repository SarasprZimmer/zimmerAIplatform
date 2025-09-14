module.exports = {
  apps: [
    {
      name: 'zimmer-backend',
      script: 'zimmer-backend/main.py',
      interpreter: './venv/bin/python',
      cwd: '/home/zimmer/zimmerAIplatform',
      env: {
        NODE_ENV: 'production',
        PORT: 8000,
        HOST: '0.0.0.0',
        JWT_SECRET_KEY: 'your-super-secret-jwt-key-change-this-in-production',
        DATABASE_URL: 'postgresql+psycopg2://zimmer:zimmer@localhost:5432/zimmer',
        DEBUG: 'false',
        ENVIRONMENT: 'production',
        ALLOWED_ORIGINS: 'http://193.162.129.243:3000,http://193.162.129.243:4000,http://localhost:3000,http://localhost:4000',
        OPENAI_API_KEY: 'your-openai-api-key-here',
        ZIMMER_SERVICE_TOKEN: 'your-service-token-here'
      },
      log_file: './logs/backend-out.log',
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'zimmer-user-panel',
      script: 'npm',
      args: 'start',
      cwd: '/home/zimmer/zimmerAIplatform/zimmer_user_panel',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        HOSTNAME: '0.0.0.0',
        NEXT_PUBLIC_API_URL: 'http://193.162.129.243:8000',
        API_URL: 'http://193.162.129.243:8000'
      },
      log_file: './logs/user-panel-out.log',
      error_file: './logs/user-panel-error.log',
      out_file: './logs/user-panel-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'zimmer-admin-dashboard',
      script: 'npm',
      args: 'start -- -p 4000 -H 0.0.0.0',
      cwd: '/home/zimmer/zimmerAIplatform/zimmermanagement/zimmer-admin-dashboard',
      env: {
        NODE_ENV: 'production',
        PORT: 4000,
        HOSTNAME: '0.0.0.0',
        NEXT_PUBLIC_API_URL: 'http://193.162.129.243:8000',
        API_URL: 'http://193.162.129.243:8000'
      },
      log_file: './logs/admin-dashboard-out.log',
      error_file: './logs/admin-dashboard-error.log',
      out_file: './logs/admin-dashboard-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
