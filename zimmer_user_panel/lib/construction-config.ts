/**
 * Under Construction Configuration for User Panel
 * 
 * This file controls whether the user panel is in "under construction" mode.
 * When enabled, all routes will redirect to the under construction page.
 */

// Cache for construction config
let constructionConfig: { isUnderConstruction: boolean } | null = null

export const CONSTRUCTION_CONFIG = {
  // Construction details
  ESTIMATED_COMPLETION: '2-3 روز کاری',
  PROGRESS_PERCENTAGE: 75,
  CONTACT_EMAIL: 'support@zimmerai.com',
  
  // Messages
  MESSAGES: {
    TITLE: 'زیر ساخت',
    SUBTITLE: 'پلتفرم زیمر',
    DESCRIPTION: 'پلتفرم زیمر در حال ساخت و بهینه‌سازی است',
    STATUS: 'در حال ساخت',
    STATUS_DESCRIPTION: 'ما در حال بهبود و بهینه‌سازی پلتفرم هستیم. لطفاً صبر کنید تا کار تکمیل شود.',
    CONTACT_TITLE: 'تماس با ما',
    CONTACT_DESCRIPTION: 'در صورت نیاز به دسترسی فوری، با تیم فنی تماس بگیرید',
    PROGRESS_LABEL: 'پیشرفت ساخت',
    ESTIMATED_TIME: 'زمان تخمینی تکمیل'
  }
}

/**
 * Check if the user panel is under construction
 */
export const isUnderConstruction = (): boolean => {
  // Return cached value if available
  if (constructionConfig) {
    return constructionConfig.isUnderConstruction
  }
  
  // Default to false if not loaded yet
  return false
}

/**
 * Load construction config from API
 */
export const loadConstructionConfig = async (): Promise<void> => {
  try {
    const response = await fetch('/api/construction/config')
    if (response.ok) {
      constructionConfig = await response.json()
    }
  } catch (error) {
    console.error('Failed to load construction config:', error)
    // Fallback to false on error
    constructionConfig = { isUnderConstruction: false }
  }
}

/**
 * Get construction configuration
 */
export const getConstructionConfig = () => {
  return {
    ...CONSTRUCTION_CONFIG,
    UNDER_CONSTRUCTION: isUnderConstruction()
  }
}

// Load config on module initialization (client-side only)
if (typeof window !== 'undefined') {
  loadConstructionConfig()
}
