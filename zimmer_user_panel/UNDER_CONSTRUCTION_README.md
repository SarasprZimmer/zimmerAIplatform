# 🚧 Under Construction Mode - User Panel

This document explains how to use the "Under Construction" feature for the user panel (panel.zimmerai.com).

## Overview

The under construction mode allows you to temporarily disable access to the user panel while you're working on it. When enabled, all routes will redirect to a maintenance page.

## Files Created/Modified

### New Files:
- `pages/under-construction.tsx` - The maintenance page displayed to users
- `lib/construction-config.ts` - Configuration file for construction mode
- `UNDER_CONSTRUCTION_README.md` - This documentation

### Modified Files:
- `pages/login.tsx` - Added redirect to under construction page
- `pages/dashboard.tsx` - Added redirect to under construction page

## How to Use

### Enable Under Construction Mode

1. Open `lib/construction-config.ts`
2. Set `UNDER_CONSTRUCTION: true`
3. Save the file
4. The user panel will now redirect all users to the maintenance page

### Disable Under Construction Mode

1. Open `lib/construction-config.ts`
2. Set `UNDER_CONSTRUCTION: false`
3. Save the file
4. The user panel will return to normal operation

## Configuration Options

In `lib/construction-config.ts`, you can customize:

- `UNDER_CONSTRUCTION` - Enable/disable construction mode
- `ESTIMATED_COMPLETION` - Estimated completion time
- `PROGRESS_PERCENTAGE` - Progress bar percentage
- `CONTACT_EMAIL` - Contact email for urgent access
- `MESSAGES` - All text content (Persian)

## Customization

### Update Progress
```typescript
PROGRESS_PERCENTAGE: 85, // Update to current progress
```

### Change Completion Time
```typescript
ESTIMATED_COMPLETION: '1 روز کاری', // Update estimated time
```

### Modify Messages
```typescript
MESSAGES: {
  TITLE: 'زیر ساخت',
  SUBTITLE: 'پلتفرم زیمر',
  // ... other messages
}
```

## Testing

1. **Enable construction mode** by setting `UNDER_CONSTRUCTION: true`
2. **Visit panel.zimmerai.com/login** - should redirect to `/under-construction`
3. **Visit panel.zimmerai.com/dashboard** - should redirect to `/under-construction`
4. **Disable construction mode** by setting `UNDER_CONSTRUCTION: false`
5. **Visit the user panel** - should work normally

## Deployment

When deploying with construction mode enabled:

1. The maintenance page will be shown to all users
2. No authentication is required to view the maintenance page
3. All other routes will redirect to the maintenance page
4. The backend API remains accessible (if needed for testing)

## Security Notes

- The maintenance page is publicly accessible
- No sensitive information should be displayed on the maintenance page
- The construction mode only affects the frontend routes
- Backend API endpoints remain accessible

## Troubleshooting

### Construction Mode Not Working
- Check that `UNDER_CONSTRUCTION: true` in `construction-config.ts`
- Verify the file is saved and the application is restarted
- Check browser console for any JavaScript errors

### Maintenance Page Not Displaying
- Verify `pages/under-construction.tsx` exists
- Check that the file is properly formatted
- Ensure all imports are correct

### Cannot Disable Construction Mode
- Check that `UNDER_CONSTRUCTION: false` in `construction-config.ts`
- Clear browser cache and cookies
- Restart the application

## Quick Commands

### Enable Construction Mode
```bash
# Edit the config file
sed -i 's/UNDER_CONSTRUCTION: false/UNDER_CONSTRUCTION: true/' lib/construction-config.ts
```

### Disable Construction Mode
```bash
# Edit the config file
sed -i 's/UNDER_CONSTRUCTION: true/UNDER_CONSTRUCTION: false/' lib/construction-config.ts
```

## Image Requirements

You need to add the 4 images to the user panel's public/images folder:
```
zimmer_user_panel/public/images/
├── dots.png          ← Place here
├── logo.png          ← Place here  
├── image1.png        ← Place here
├── image2.png        ← Place here
```

## Support

If you need help with the under construction feature:

1. Check this README first
2. Verify the configuration file
3. Test with a fresh browser session
4. Contact the development team

---

**Note**: Remember to disable construction mode when you're ready to go live! 🚀
