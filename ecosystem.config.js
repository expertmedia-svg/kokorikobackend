module.exports = {
  apps: [
    {
      name: 'kokoriko-backend',
      cwd: '/home/debian/projects/kokoriko-backend',
      script: 'venv/bin/uvicorn',
      args: 'app.main:app --host 127.0.0.1 --port 4223 --workers 4',
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      exec_mode: 'fork',
    }
  ]
};
