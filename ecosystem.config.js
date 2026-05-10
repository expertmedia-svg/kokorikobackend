module.exports = {
  apps: [
    {
      name: 'kokoriko-backend',
      cwd: '/home/debian/projects/kokoriko-backend',
      script: './start.sh',
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
