# Love Is Complicated - NIGHTMARE CTF Challenge

**Author:** MD  
**Category:** Web / Cryptography / Reverse Engineering  
**Difficulty:** NIGHTMARE  
**Points:** 1500  
**Estimated Solve Time:** 12-20 hours  
**Expected Solve Rate:** <1%

---

## 🔥 What Makes This 2x More Complicated

This challenge is **TWICE as complex** as "Love Is Simple" with the following enhancements:

### Comparison Table

| Feature | Love Is Simple | Love Is Complicated | Multiplier |
|---------|----------------|---------------------|------------|
| **Salts** | 4 | 8 (with rotation) | 2x |
| **Required Headers** | 4 | 8 | 2x |
| **HMAC Layers** | 4 | 6 | 1.5x |
| **Hash Algorithms** | 5 | 8 | 1.6x |
| **Obfuscation Layers** | 12 | 24 | 2x |
| **Decoy Flags** | 17 | 30+ | ~2x |
| **Valid Time Window** | 6 minutes | 6 minutes | Same |
| **Valid Seconds** | 20/minute | 16/minute | 0.8x |
| **Additional Features** | - | PoW, TOTP, Fingerprint | NEW |
| **Points** | 1000 | 1500 | 1.5x |
| **Solve Time** | 6-10 hours | 12-20 hours | 2x |

---

## 🎯 New Features (Not in Original)

### 1. Dynamic Salt Rotation
Salts rotate every minute based on timestamp:
```python
rotation_index = (timestamp // 60) % 8
```
This means the same timestamp in different minutes produces different tokens!

### 2. Proof of Work (PoW)
Must find a nonce where:
```python
SHA256(timestamp + nonce).startswith('00000')  # 5 leading zeros
```
Expected attempts: ~1,000,000 (takes 5-30 seconds)

### 3. Time-Based One-Time Password (TOTP)
Generate 6-digit TOTP code that changes every 30 seconds:
```python
totp = generate_totp(timestamp, window=30)
```

### 4. Browser Fingerprinting
Must generate fingerprint from browser headers:
```python
fingerprint = SHA256(User-Agent + Accept-Language + Accept-Encoding)[:32]
```

### 5. Rate Limiting with Exponential Backoff
Each failed attempt increases wait time:
- 1st attempt: 0 seconds
- 2nd attempt: 2 seconds
- 3rd attempt: 4 seconds
- 4th attempt: 8 seconds
- 5th attempt: 16 seconds
- etc.

### 6. 8 Required Headers (vs 4)
```
x-love-time          - Timestamp
x-love-token         - 6-layer HMAC token
x-love-proof         - SHA3-256 proof
x-love-signature     - SHA3-512 signature
x-love-totp          - 6-digit TOTP code
x-love-commitment    - BLAKE2B commitment
x-love-fingerprint   - Browser fingerprint
x-love-nonce         - Proof of work nonce
```

### 7. 6-Layer HMAC (vs 4)
```
Layer 1: HMAC-SHA256
Layer 2: HMAC-SHA512
Layer 3: HMAC-SHA3-256
Layer 4: HMAC-BLAKE2B
Layer 5: HMAC-SHA3-512  ← NEW
Layer 6: HMAC-BLAKE2S   ← NEW
```

### 8. 24 Layers of Obfuscation (vs 12)
```
24x Base64 → XOR → Base85 → Base32 → Base64 → Chunking
```

---

## 📊 Complexity Analysis

### Time Constraints (More Restrictive)

| Constraint | Love Is Simple | Love Is Complicated |
|------------|----------------|---------------------|
| Hour | 14 (2 PM IST) | 14 (2 PM IST) |
| Minutes | 7-12 (6 min) | 8-13 (6 min) |
| Seconds | 10-49 (40 sec) | 15-45 (31 sec) |
| Even seconds | Yes | Yes |
| Divisible by 21 | Yes | Yes |
| Valid seconds/min | 20 | 16 |
| Valid timestamps/day | ~6 | ~5 |

### Cryptographic Complexity

**Love Is Simple:**
- 4 salts (static)
- 4-layer HMAC
- Master key: 5 rounds SHA-512

**Love Is Complicated:**
- 8 salts (rotating every minute)
- 6-layer HMAC
- Master key: 8 rounds (alternating SHA-512 and SHA3-512)
- Additional: PoW + TOTP + Fingerprint

### Success Probability

**Love Is Simple:** ~0.0003%

**Love Is Complicated:** ~0.00015% (2x harder)

Breakdown:
- Time window: 360s / 86400s = 0.42%
- Valid minutes: 6/30 = 20%
- Valid seconds: 16/60 = 27%
- Even seconds: 50%
- Divisible by 21: 4.76%
- **Combined: 0.00015%**

---

## 🔐 8 Salts to Discover

```python
SECRET_KEY = b"C0mpl1c4t3d_L0v3_R3qu1r3s_P4t13nc3_Und3rst4nd1ng_4nd_C0mm1tm3nt_2020"
SALT_PRIMARY = b"l0v3_1s_n3v3r_s1mpl3_1t_t4k3s_w0rk"
SALT_SECONDARY = b"r3l4t10nsh1ps_4r3_bu1lt_0n_trust"
SALT_TERTIARY = b"c0mm1tm3nt_1s_th3_f0und4t10n"
SALT_QUATERNARY = b"p4t13nc3_1s_th3_k3y_t0_l0v3"
SALT_QUINARY = b"und3rst4nd1ng_br1dg3s_h34rts"
SALT_SENARY = b"c0mmun1c4t10n_1s_3ss3nt14l"
SALT_SEPTENARY = b"trust_must_b3_34rn3d_0v3r_t1m3"
SALT_OCTONARY = b"l0v3_gr0ws_thr0ugh_sh4r3d_m0m3nts"
TOTP_SECRET = b"L0V3_T0TP_S3CR3T_K3Y_F0R_P3RF3CT_T1M1NG"
```

---

## 🎭 30+ Decoy Flags

Decoy flags are returned for:
1. Wrong hour
2. Early minute (< 8)
3. Late minute (> 13)
4. Wrong second range
5. Odd second
6. Not divisible by 21
7. Not divisible by 7
8. Not divisible by 3
9. User-Agent odd length
10. Wrong fingerprint
11. Invalid TOTP
12. Proof of work failed
13. Wrong IP/location
14. Rate limited
15. Missing header 1
16. Missing header 2
17. Missing header 3
18. Missing header 4
19. Missing header 5
20. Missing header 6
21. Missing header 7
22. Missing header 8
23. Wrong token
24. Wrong proof
25. Wrong signature
26. Wrong commitment
27. HTML source
28. Console log
29. robots.txt
30. Click event
... and more!

---

## 🚀 Solution Steps

### Step 1: Wait for Time Window
- Must be 2:00-2:30 PM IST
- Minute must be 8-13
- Second must be 15-45 and EVEN
- Timestamp must be divisible by 21

### Step 2: Solve Proof of Work
Find nonce where `SHA256(timestamp + nonce)` starts with `00000`

### Step 3: Generate TOTP
```python
totp = generate_totp(timestamp, window=30)
```

### Step 4: Generate Fingerprint
```python
fingerprint = SHA256(UA + Accept-Lang + Accept-Encoding)[:32]
```

### Step 5: Get Rotated Salts
```python
rotated_salts = get_rotated_salts(timestamp)
```

### Step 6: Generate Master Key
8 rounds of alternating SHA-512 and SHA3-512

### Step 7: Generate 6-Layer Token
HMAC with SHA256 → SHA512 → SHA3-256 → BLAKE2B → SHA3-512 → BLAKE2S

### Step 8: Generate Proof
```python
proof = SHA3-256(timestamp + UA + fingerprint + salt)
```

### Step 9: Generate Signature
```python
signature = HMAC-SHA3-512(timestamp + token + proof + totp)
```

### Step 10: Generate Commitment
```python
commitment = HMAC-BLAKE2B(timestamp + token + proof + signature + nonce)
```

### Step 11: Send Request
POST to `/api/confess` with all 8 headers

### Step 12: Deobfuscate Flag
Reverse 24 layers of encoding

---

## 🏆 Flag

```
TRACECTF{C0mpl1c4t3d_L0v3_R3qu1r3s_P4t13nc3_Trust_4nd_Unw4v3r1ng_C0mm1tm3nt_2020}
```

---

## 📈 Difficulty Metrics

| Metric | Value |
|--------|-------|
| Difficulty | NIGHTMARE |
| Points | 1500 |
| Salts to discover | 8 + 1 TOTP secret |
| Headers required | 8 |
| Cryptographic layers | 6 |
| Obfuscation layers | 24 |
| Decoy flags | 30+ |
| Valid timestamps/day | ~5 |
| Success probability | 0.00015% |
| Expected attempts | 666,666+ |
| PoW difficulty | 5 leading zeros |
| PoW expected attempts | ~1,000,000 |
| Estimated solve time | 12-20 hours |
| Expected solve rate | <1% |

---

## 🛡️ Defense Layers

1. **Time Window** - Blocks 98.6% of attempts
2. **8 Headers** - Blocks 99.9% of remaining
3. **Proof of Work** - Requires computation
4. **TOTP** - Changes every 30 seconds
5. **Fingerprint** - Must match browser
6. **Token Validation** - 6-layer HMAC
7. **Proof Validation** - SHA3-256
8. **Signature Validation** - SHA3-512
9. **Commitment Validation** - BLAKE2B
10. **Rate Limiting** - Exponential backoff
11. **Timing Precision** - Within 20 seconds
12. **Minute Range** - 8-13 only
13. **Second Range** - 15-45 only
14. **Even Second** - Must be even
15. **Divisible by 21** - Timestamp constraint
16. **Salt Rotation** - Changes every minute
17. **24-Layer Obfuscation** - Prevents extraction

**Total Protection:** ~99.99985% of attempts blocked

---

## 💡 Key Insights

### What Makes This NIGHTMARE Difficulty

1. **8 Salts** - 2x more to discover, with rotation
2. **Dynamic Rotation** - Salts change every minute
3. **Proof of Work** - Requires ~1M hash attempts
4. **TOTP** - Time-sensitive, changes every 30s
5. **Fingerprinting** - Browser-dependent
6. **6 Layers** - More HMAC complexity
7. **8 Headers** - All must be perfect
8. **24 Obfuscation Layers** - 2x more decoding
9. **Rate Limiting** - Exponential backoff
10. **Tighter Timing** - Fewer valid seconds
11. **30+ Decoys** - More misleading flags
12. **Multiple Algorithms** - SHA256, SHA512, SHA3-256, SHA3-512, BLAKE2B, BLAKE2S

### Discovery Difficulty

**Easy:** Time window, need headers  
**Medium:** 8 headers required, timing precision  
**Hard:** Primary salts, basic algorithms  
**Very Hard:** All 8 salts, rotation mechanism  
**EXTREME:** PoW, TOTP, fingerprinting  
**NIGHTMARE:** 6-layer HMAC, salt rotation, 24-layer obfuscation

---

## 🎓 Learning Outcomes

Players will learn:
- Advanced HMAC constructions
- Proof of work systems
- TOTP implementation
- Browser fingerprinting
- Rate limiting strategies
- Complex obfuscation techniques
- Time-based security
- Multi-layer cryptography
- Salt rotation mechanisms
- Exponential backoff

---

## 🔧 Tools Required

- Python 3.x
- requests library
- pytz library
- hashlib module
- hmac module
- base64 module
- High patience level
- Strong coffee ☕

---

**This is the most complicated web/crypto challenge ever created!**

**Good luck. You'll need it. 💔**

---

**Author:** MD  
**Challenge:** Love Is Complicated  
**Version:** 1.0 (NIGHTMARE)  
**Status:** Ready to Destroy Souls 😈
