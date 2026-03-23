# 💔 Love Is Complicated

**A NIGHTMARE Difficulty CTF Challenge**

---

## 📋 Overview

**Author:** MD  
**Category:** Web / Cryptography / Reverse Engineering  
**Difficulty:** NIGHTMARE  
**Points:** 1500  
**Estimated Solve Time:** 12-20 hours  
**Expected Solve Rate:** <1%

This challenge is **2x more complicated** than "Love Is Simple" with enhanced cryptographic requirements, proof of work, TOTP authentication, and browser fingerprinting.

---

## 📁 Files in This Folder

- **app_complicated.py** - Flask application (challenge server)
- **solution_complicated.py** - Complete solver script
- **CHALLENGE_COMPLICATED.md** - Full challenge documentation
- **QUICK_REFERENCE_COMPLICATED.md** - Quick reference guide
- **requirements_complicated.txt** - Python dependencies
- **README.md** - This file

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_complicated.txt
```

### 2. Run the Challenge Server

```bash
python app_complicated.py
```

The server will start on `http://localhost:5000`

### 3. Run the Solver

**Important:** Must be run during 2:00-2:30 PM IST

```bash
python solution_complicated.py http://localhost:5000
```

---

## 🔥 What Makes This 2x More Complicated

### Doubled Features
- ✅ **8 salts** (vs 4) with dynamic rotation
- ✅ **8 headers** (vs 4) required
- ✅ **24 obfuscation layers** (vs 12)
- ✅ **30+ decoy flags** (vs 17)
- ✅ **6-layer HMAC** (vs 4)

### New Features
- 🆕 **Proof of Work** - Find nonce with 5 leading zeros
- 🆕 **TOTP** - Time-based one-time password
- 🆕 **Browser Fingerprinting** - SHA256 of headers
- 🆕 **Rate Limiting** - Exponential backoff
- 🆕 **Dynamic Salt Rotation** - Changes every minute

---

## ⏰ Timing Requirements

```
Hour:      14 (2 PM IST)
Minutes:   8-13 (6-minute window)
Seconds:   15-45 (even seconds only)
Divisible: timestamp % 21 == 0
Precision: Within 20 seconds
```

**Valid timestamps per day:** ~5

---

## 🔐 8 Required Headers

```
1. x-love-time          - Unix timestamp
2. x-love-token         - 6-layer HMAC token
3. x-love-proof         - SHA3-256 proof
4. x-love-signature     - SHA3-512 signature
5. x-love-totp          - 6-digit TOTP code
6. x-love-commitment    - BLAKE2B commitment
7. x-love-fingerprint   - Browser fingerprint
8. x-love-nonce         - Proof of work nonce
```

---

## 🏆 Flag Format

```
TRACECTF{C0mpl1c4t3d_L0v3_R3qu1r3s_P4t13nc3_Trust_4nd_Unw4v3r1ng_C0mm1tm3nt_2020}
```

---

## 📊 Complexity Comparison

| Feature | Love Is Simple | Love Is Complicated |
|---------|----------------|---------------------|
| Salts | 4 | 8 (rotating) |
| Headers | 4 | 8 |
| HMAC Layers | 4 | 6 |
| Obfuscation | 12 layers | 24 layers |
| Decoy Flags | 17 | 30+ |
| Points | 1000 | 1500 |
| Solve Time | 6-10 hours | 12-20 hours |
| Success Rate | 1-2% | <1% |

---

## 📚 Documentation

- **CHALLENGE_COMPLICATED.md** - Complete challenge writeup with all details
- **QUICK_REFERENCE_COMPLICATED.md** - Quick reference for solving

---

## 🛠️ Technologies Used

- Python 3.x
- Flask (web framework)
- Cryptography (hashlib, hmac)
- pytz (timezone handling)
- requests (HTTP client)

---

## 💡 Tips for Solving

1. Read the full documentation first
2. Understand the timing constraints
3. Solve proof of work efficiently
4. Generate TOTP at the right moment
5. Get salt rotation correct
6. All 8 headers must be perfect
7. Be patient with 24-layer deobfuscation
8. Watch out for 30+ decoy flags

---

## ⚠️ Warning

This is a **NIGHTMARE difficulty** challenge. Expected solve time is 12-20 hours. Only attempt if you:
- Have strong cryptography knowledge
- Understand HMAC and hash functions
- Can implement proof of work
- Have patience for complex debugging
- Are comfortable with Python

---

## 🎯 Challenge Goals

This challenge teaches:
- Advanced HMAC constructions
- Proof of work systems
- TOTP implementation
- Browser fingerprinting
- Rate limiting strategies
- Complex obfuscation techniques
- Time-based security mechanisms
- Multi-layer cryptography

---

## 📞 Support

For questions or issues:
- Check CHALLENGE_COMPLICATED.md for full details
- Review QUICK_REFERENCE_COMPLICATED.md for quick help
- Verify all timing constraints are met
- Ensure all 8 salts are correct

---

**Good luck! You'll need it. 💔**

---

**Author:** MD  
**Version:** 1.0  
**Status:** Ready to Destroy Souls 😈
