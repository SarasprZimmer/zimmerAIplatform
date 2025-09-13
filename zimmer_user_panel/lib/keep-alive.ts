// Keep-alive utility for idle UX
// Refreshes token every 10 minutes if user is active

let keepAliveInterval: NodeJS.Timeout | null = null
let lastActivity = Date.now()
let isActive = false
let isRefreshing = false

const KEEP_ALIVE_INTERVAL = 15 * 60 * 1000 // 15 minutes (same as access token TTL)
const IDLE_TIMEOUT = 5 * 60 * 1000 // 5 minutes

// Track user activity
function updateActivity() {
  lastActivity = Date.now()
  isActive = true
}

// Check if user is idle
function isUserIdle(): boolean {
  return Date.now() - lastActivity > IDLE_TIMEOUT
}

// Keep-alive function
async function keepAlive() {
  if (isRefreshing) {
    console.log('Keep-alive: Token refresh already in progress, skipping...')
    return
  }

  if (!isUserIdle()) {
    try {
      isRefreshing = true
      console.log('Keep-alive: Attempting token refresh...')
      
      // Use the API client for proper token handling
      const { default: ApiClient } = await import('./api')
      const api = new ApiClient()
      
      try {
        const result = await api.refreshToken()
        console.log('Keep-alive: Token refreshed successfully')
      } catch (error) {
        console.warn('Keep-alive: Token refresh failed:', error)
        // Don't force logout on keep-alive failure, just log it
      }
      
    } catch (error) {
      console.error('Keep-alive: Failed to refresh token:', error)
      // If there's a network error, log it but don't force logout
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.warn('Keep-alive: Network error, backend may be unavailable')
      }
    } finally {
      isRefreshing = false
    }
  } else {
    console.log('Keep-alive: User is idle, skipping token refresh')
  }
}

// Start keep-alive monitoring
export function startKeepAlive() {
  console.log('Keep-alive: Starting keep-alive monitoring...')
  
  // Add event listeners for user activity
  const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']
  
  events.forEach(event => {
    document.addEventListener(event, updateActivity, true)
  })

  // Start keep-alive interval
  keepAliveInterval = setInterval(keepAlive, KEEP_ALIVE_INTERVAL)
  
  console.log('Keep-alive: Keep-alive monitoring started')
}

// Stop keep-alive monitoring
export function stopKeepAlive() {
  if (keepAliveInterval) {
    clearInterval(keepAliveInterval)
    keepAliveInterval = null
  }
  
  // Remove event listeners
  const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']
  
  events.forEach(event => {
    document.removeEventListener(event, updateActivity, true)
  })
  
  console.log('Keep-alive: Keep-alive monitoring stopped')
}

// Check if keep-alive is running
export function isKeepAliveRunning(): boolean {
  return keepAliveInterval !== null
}


