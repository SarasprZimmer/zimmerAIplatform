module.exports = {
  apps: [{
    name: 'zimmer-admin-dashboard',
    script: 'npm',
    args: 'start -- -p 4000 -H 0.0.0.0',
    cwd: '/home/zimmer/zimmerAIplatform/zimmermanagement/zimmer-admin-dashboard',
    env: {
      NODE_ENV: 'production',
      PORT: 4000,
      NEXT_PUBLIC_API_URL: 'https://api.zimmerai.com'
    }
  }]
};
