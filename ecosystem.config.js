module.exports = {
  apps: [
    {
      name: 'zimmer-backend',
      script: 'zimmer-backend/main.py',
      interpreter: './venv/bin/python',
      cwd: '/opt/zimmer/zimmer-platform-final',
      env: {
        NODE_ENV: 'production',
        PORT: 8000
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_file: './logs/backend-combined.log',
      time: true
    },
    {
      name: 'zimmer-user-panel',
      script: 'npm',
      args: 'start',
      cwd: '/opt/zimmer/zimmer-platform-final/zimmer_user_panel',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/user-panel-error.log',
      out_file: './logs/user-panel-out.log',
      log_file: './logs/user-panel-combined.log',
      time: true,
      kill_timeout: 5000
    },
    {
      name: 'zimmer-admin-dashboard',
      script: 'npm',
      args: 'start',
      cwd: '/opt/zimmer/zimmer-platform-final/zimmermanagement/zimmer-admin-dashboard',
      env: {
        NODE_ENV: 'production',
        PORT: 4000,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/admin-dashboard-error.log',
      out_file: './logs/admin-dashboard-out.log',
      log_file: './logs/admin-dashboard-combined.log',
      time: true,
      kill_timeout: 5000
    }
  ]
};
