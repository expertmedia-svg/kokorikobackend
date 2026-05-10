module.exports = {
  apps: [
    {
      name: 'kokoriko-backend',
      script: 'uvicorn app.main:app',
      args: '--host 127.0.0.1 --port 4223 --workers 4',
      interpreter: '/usr/bin/python3',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      instances: 1,
      exec_mode: 'fork',
    }
  ]
};
