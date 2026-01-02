# QR Code Auto-Generation

## Test Results ✅

### 1. Management Command
```bash
python manage.py generate_qrcodes
```
**Result:**
- Generated 7 new QR codes
- Total unclaimed: 10
- Sample UUIDs: 2d7b5fd367784fc4, c10547584534472c, etc.

### 2. Auto-Generation Signal
**Test:** Claim 1 QR code → Check if new one is generated

**Before Claim:**
- Unclaimed QR codes: 10

**Action:** Claimed QR `2d7b5fd367784fc4`

**After Claim:**
- Unclaimed QR codes: 10 ✅
- New QR generated: `9669af90111b4c06`

### 3. Railway Deployment
**Commands to run on Railway:**
```bash
# Generate initial pool of 10 QR codes
python manage.py generate_qrcodes

# Or generate custom amount
python manage.py generate_qrcodes --count 20
```

## How It Works

1. **Initial Setup:** Run `manage.py generate_qrcodes` to create 10 unclaimed QR codes
2. **Auto-Maintenance:** When QR code is claimed (house assigned), signal automatically generates new QR code
3. **Always 10:** System maintains minimum of 10 unclaimed QR codes at all times

## Files Changed
- `apps/qrcodes/management/commands/generate_qrcodes.py` - Management command
- `apps/qrcodes/signals.py` - Auto-generation signal
