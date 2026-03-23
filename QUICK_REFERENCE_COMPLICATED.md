# Love Is Complicated - Quick Reference

## 🎯 Challenge at a Glance

**Difficulty:** NIGHTMARE (1500 points)  
**Time:** 12-20 hours  
**Success Rate:** <1%

---

## ⏰ Timing Requirements

```
Hour:      14 (2 PM IST)
Minutes:   8-13 (6-minute window)
Seconds:   15-45 (31 seconds)
Parity:    EVEN seconds only
Divisible: timestamp % 21 == 0
Precision: Within 20 seconds of server
```

**Valid seconds per minute:** 16  
**Valid timestamps per day:** ~5

---

## 🔐 8 Required Headers

```
1. x-love-time          Unix timestamp
2. x-love-token         6-layer HMAC token
3. x-love-proof         SHA3-256 proof
4. x-love-signature     SHA3-512 signature
5. x-love-totp          6-digit TOTP code
6. x-love-commitment    BLAKE2B commitment
7. x-love-fingerprint   Browser fingerprint (32 chars)
8. x-love-nonce         Proof of work nonce
```

---

## 🧂 8 Salts (Rotating)

```python
SECRET_KEY      = b"C0mpl1c4t3d_L0v3_R3qu1r3s_P4t13nc3_Und3rst4nd1ng_4nd_C0mm1tm3nt_2024"
SALT_PRIMARY    = b"l0v3_1s_n3v3r_s1mpl3_1t_t4k3s_w0rk"
SALT_SECONDARY  = b"r3l4t10nsh1ps_4r3_bu1lt_0n_trust"
SALT_TERTIARY   = b"c0mm1tm3nt_1s_th3_f0und4t10n"
SALT_QUATERNARY = b"p4t13nc3_1s_th3_k3y_t0_l0v3"
SALT_QUINARY    = b"und3rst4nd1ng_br1dg3s_h34rts"
SALT_SENARY     = b"c0mmun1c4t10n_1s_3ss3nt14l"
SALT_SEPTENARY  = b"trust_must_b3_34rn3d_0v3r_t1m3"
SALT_OCTONARY   = b"l0v3_gr0ws_thr0ugh_sh4r3d_m0m3nts"
TOTP_SECRET     = b"L0V3_T0TP_S3CR3T_K3Y_F0R_P3RF3CT_T1M1NG"
```

**Rotation:** `rotation_index = (timestamp // 60) % 8`

---

## 🔨 Proof of Work

```python
# Find nonce where:
SHA256(timestamp + nonce).startswith('00000')

# Difficulty: 5 leading zeros
# Expected attempts: ~1,000,000
# Time: 5-30 seconds
```

---

## 🔑 TOTP Generation

```python
def generate_totp(timestamp, window=30):
    time_counter = timestamp // window
    message = str(time_counter).encode()
    totp_hash = hmac.new(TOTP_SECRET, message, hashlib.sha256).digest()
    offset = totp_hash[-1] & 0x0f
    code = int.from_bytes(totp_hash[offset:offset+4], 'big') & 0x7fffffff
    return str(code % 1000000).zfill(6)
```

**Changes every:** 30 seconds  
**Format:** 6 digits (e.g., "123456")

---

## 🔍 Browser Fingerprint

```python
fingerprint = SHA256(
    User-Agent + Accept-Language + Accept-Encoding
).hexdigest()[:32]
```

**Example:**
```
User-Agent: LoveConfessor/3.0
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
```

---

## 🏗️ Master Key Derivation

```python
components = [
    str(timestamp).encode(),
    rotated_salts[0],
    rotated_salts[1],
    user_agent.encode(),
    str(timestamp // 300).encode(),
    rotated_salts[2],
    ip_addr.encode(),
    str(timestamp // 120).encode(),
    rotated_salts[3],
    fingerprint.encode(),
    rotated_salts[4]
]

master = b''.join(components)

# Hash 8 times alternating
for i in range(8):
    if i % 2 == 0:
        master = hashlib.sha512(master).digest()
    else:
        master = hashlib.sha3_512(master).digest()
```

---

## 🎯 6-Layer Token Generation

```python
# Layer 1: HMAC-SHA256
layer1 = hmac.new(SECRET_KEY, 
    f"{timestamp}{rotated_salts[0].decode()}".encode(), 
    hashlib.sha256).digest()

# Layer 2: HMAC-SHA512
layer2 = hmac.new(rotated_salts[1], 
    layer1 + str(timestamp).encode() + totp.encode(), 
    hashlib.sha512).digest()

# Layer 3: HMAC-SHA3-256
layer3 = hmac.new(master_key, 
    layer2 + rotated_salts[2], 
    hashlib.sha3_256).digest()

# Layer 4: HMAC-BLAKE2B
layer4 = hmac.new(rotated_salts[3], 
    layer3 + str(timestamp // 60).encode(), 
    hashlib.blake2b).digest()

# Layer 5: HMAC-SHA3-512
layer5 = hmac.new(rotated_salts[4], 
    layer4 + fingerprint.encode(), 
    hashlib.sha3_512).digest()

# Layer 6: HMAC-BLAKE2S
layer6 = hmac.new(rotated_salts[5], 
    layer5 + str(timestamp // 30).encode(), 
    hashlib.blake2s).digest()

# Final token
token = hashlib.sha3_256(
    layer1 + layer2[:32] + layer3 + layer4[:32] + layer5[:32] + layer6
).hexdigest()
```

---

## 📝 Proof Generation

```python
proof = hashlib.sha3_256(
    f"{timestamp}{user_agent}{fingerprint}{rotated_salts[0].decode()}".encode()
).hexdigest()
```

---

## ✍️ Signature Generation

```python
signature = hmac.new(
    rotated_salts[6],
    f"{timestamp}{token}{proof}{totp}".encode(),
    hashlib.sha3_512
).hexdigest()
```

---

## 💍 Commitment Generation

```python
commitment = hmac.new(
    rotated_salts[7],
    f"{timestamp}{token}{proof}{signature}{nonce}".encode(),
    hashlib.blake2b
).hexdigest()
```

---

## 🔓 Deobfuscation (24 Layers)

```python
# 1. Split by @@ and rejoin
# 2. Base64 decode
# 3. Split by || and rejoin
# 4. Base32 decode
# 5. Split by :: and rejoin
# 6. Base85 decode
# 7. XOR decrypt with SHA3-512 key
# 8. Base64 decode 24 times
```

**XOR Key:**
```python
xor_key = hashlib.sha3_512(
    SECRET_KEY + SALT_PRIMARY + SALT_SECONDARY + str(timestamp).encode()
).digest()
```

---

## ⚡ Rate Limiting

**Exponential backoff:**
```
Attempt 1: 0 seconds
Attempt 2: 2 seconds
Attempt 3: 4 seconds
Attempt 4: 8 seconds
Attempt 5: 16 seconds
Attempt 6: 32 seconds
...
```

**Formula:** `wait_time = 2^(attempt_count - 1)`

---

## 🎭 Common Decoy Flags

```
early_minute:     TRACECTF{t00_34rly_l0v3_n33ds_p4t13nc3}
late_minute:      TRACECTF{t00_l4t3_th3_m0m3nt_h4s_p4ss3d}
odd_second:       TRACECTF{3v3n_s3c0nds_br1ng_h4rm0ny}
not_div_21:       TRACECTF{d1v1s1b1l1ty_1s_k3y_try_21}
invalid_totp:     TRACECTF{t0tp_3xp1r3d_t1m3_w41ts_f0r_n0_0n3}
pow_failed:       TRACECTF{pr00f_0f_w0rk_1nc0mpl3t3}
wrong_token:      TRACECTF{t0k3n_g3n3r4t10n_f41l3d}
```

---

## 🏆 Real Flag

```
TRACECTF{C0mpl1c4t3d_L0v3_R3qu1r3s_P4t13nc3_Trust_4nd_Unw4v3r1ng_C0mm1tm3nt_2024}
```

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements_complicated.txt

# Run server
python app_complicated.py

# Run solver (during 2:00-2:30 PM IST)
python solution_complicated.py http://localhost:5000
```

---

## 📊 Complexity Comparison

| Feature | Simple | Complicated | Increase |
|---------|--------|-------------|----------|
| Salts | 4 | 8 | 2x |
| Headers | 4 | 8 | 2x |
| HMAC Layers | 4 | 6 | 1.5x |
| Obfuscation | 12 | 24 | 2x |
| Decoys | 17 | 30+ | ~2x |
| Points | 1000 | 1500 | 1.5x |
| Time | 6-10h | 12-20h | 2x |

---

## 💡 Pro Tips

1. **Solve PoW first** - Takes 5-30 seconds
2. **Generate TOTP immediately** - Changes every 30s
3. **Get rotated salts** - Different every minute
4. **Check all timing constraints** - Very restrictive
5. **User-Agent length must be even**
6. **Fingerprint must match headers**
7. **All 8 headers required simultaneously**
8. **Rate limiting is exponential** - Don't spam
9. **Decoy flags everywhere** - Verify it's real
10. **24 layers to deobfuscate** - Be patient

---

## 🎯 Success Checklist

- [ ] Time: 2:00-2:30 PM IST
- [ ] Minute: 8-13
- [ ] Second: 15-45 and EVEN
- [ ] Timestamp % 21 == 0
- [ ] Within 20 seconds of server
- [ ] User-Agent length EVEN
- [ ] PoW solved (5 leading zeros)
- [ ] TOTP generated (current 30s window)
- [ ] Fingerprint matches headers
- [ ] All 8 salts correct
- [ ] Salt rotation applied
- [ ] Master key: 8 rounds
- [ ] Token: 6 layers
- [ ] Proof: SHA3-256
- [ ] Signature: SHA3-512
- [ ] Commitment: BLAKE2B
- [ ] All 8 headers sent
- [ ] Deobfuscate 24 layers

---

**Good luck! 💔**
