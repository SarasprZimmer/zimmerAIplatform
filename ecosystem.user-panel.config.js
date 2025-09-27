module.exports = {
  apps: [{
    name: 'zimmer-user-panel',
    script: 'npm',
    args: 'start',
    cwd: '/home/zimmer/zimmerAIplatform/zimmer_user_panel',
    env: {
      NODE_ENV: 'production',
      PORT: 3000,
      NEXT_PUBLIC_API_URL: 'https://api.zimmerai.com'
    }
  }]
};
