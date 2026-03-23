#!/usr/bin/env python3
"""
Love Is Complicated - Solution Script
Author: MD
Difficulty: NIGHTMARE

This solves the 2x more complicated version with:
- 8 salts with dynamic rotation
- 8 headers required
- 6-layer HMAC
- Proof of work
- TOTP generation
- Browser fingerprinting
- 24 layers of deobfuscation
"""

import requests
import time
import hmac
import hashlib
import base64
from datetime import datetime
import pytz

# ============================================================================
# CONSTANTS - Must discover all 8 salts
# ============================================================================
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

IST = pytz.timezone('Asia/Kolkata')

# ============================================================================
# DYNAMIC SALT ROTATION
# ============================================================================
def get_rotated_salts(timestamp):
    """Rotate salts based on timestamp"""
    rotation_index = (timestamp // 60) % 8
    salts = [
        SALT_PRIMARY, SALT_SECONDARY, SALT_TERTIARY, SALT_QUATERNARY,
        SALT_QUINARY, SALT_SENARY, SALT_SEPTENARY, SALT_OCTONARY
    ]
    return salts[rotation_index:] + salts[:rotation_index]

# ============================================================================
# PROOF OF WORK
# ============================================================================
def solve_proof_of_work(timestamp, difficulty=5):
    """Find nonce that produces hash with required leading zeros"""
    print(f"🔨 Solving proof of work (difficulty: {difficulty})...")
    nonce = 0
    start_time = time.time()
    
    while True:
        data = f"{timestamp}{nonce}".encode()
        hash_result = hashlib.sha256(data).hexdigest()
        
        if hash_result.startswith('0' * difficulty):
            elapsed = time.time() - start_time
            print(f"✅ Found nonce: {nonce} (took {elapsed:.2f}s)")
            print(f"   Hash: {hash_result}")
            return str(nonce)
        
        nonce += 1
        
        if nonce % 100000 == 0:
            print(f"   Tried {nonce:,} nonces...")

# ============================================================================
# TOTP GENERATION
# ============================================================================
def generate_totp(timestamp, window=30):
    """Generate time-based one-time password"""
    time_counter = timestamp // window
    message = str(time_counter).encode()
    totp_hash = hmac.new(TOTP_SECRET, message, hashlib.sha256).digest()
    offset = totp_hash[-1] & 0x0f
    code = int.from_bytes(totp_hash[offset:offset+4], 'big') & 0x7fffffff
    return str(code % 1000000).zfill(6)

# ============================================================================
# BROWSER FINGERPRINTING
# ============================================================================
def generate_love_fingerprint(user_agent, accept_lang, accept_encoding):
    """Generate browser fingerprint"""
    data = f"{user_agent}{accept_lang}{accept_encoding}".encode()
    return hashlib.sha256(data).hexdigest()[:32]

# ============================================================================
# 6-LAYER HMAC TOKEN GENERATION
# ============================================================================
def derive_master_key(timestamp, user_agent, ip_addr, fingerprint):
    """Enhanced master key derivation with 8 salts"""
    rotated_salts = get_rotated_salts(timestamp)
    
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
    
    # Hash 8 times with alternating algorithms
    for i in range(8):
        if i % 2 == 0:
            master = hashlib.sha512(master).digest()
        else:
            master = hashlib.sha3_512(master).digest()
    
    return master

def generate_love_token(timestamp, user_agent, ip_addr, fingerprint, totp):
    """6-layer HMAC token generation"""
    master_key = derive_master_key(timestamp, user_agent, ip_addr, fingerprint)
    rotated_salts = get_rotated_salts(timestamp)
    
    # Layer 1: HMAC-SHA256
    layer1 = hmac.new(
        SECRET_KEY,
        f"{timestamp}{rotated_salts[0].decode()}".encode(),
        hashlib.sha256
    ).digest()
    
    # Layer 2: HMAC-SHA512
    layer2 = hmac.new(
        rotated_salts[1],
        layer1 + str(timestamp).encode() + totp.encode(),
        hashlib.sha512
    ).digest()
    
    # Layer 3: HMAC-SHA3-256
    layer3 = hmac.new(
        master_key,
        layer2 + rotated_salts[2],
        hashlib.sha3_256
    ).digest()
    
    # Layer 4: HMAC-BLAKE2B
    layer4 = hmac.new(
        rotated_salts[3],
        layer3 + str(timestamp // 60).encode(),
        hashlib.blake2b
    ).digest()
    
    # Layer 5: HMAC-SHA3-512
    layer5 = hmac.new(
        rotated_salts[4],
        layer4 + fingerprint.encode(),
        hashlib.sha3_512
    ).digest()
    
    # Layer 6: HMAC-BLAKE2S
    layer6 = hmac.new(
        rotated_salts[5],
        layer5 + str(timestamp // 30).encode(),
        hashlib.blake2s
    ).digest()
    
    # Final token
    final_token = hashlib.sha3_256(
        layer1 + layer2[:32] + layer3 + layer4[:32] + layer5[:32] + layer6
    ).hexdigest()
    
    return final_token

def generate_love_proof(timestamp, user_agent, fingerprint):
    """Enhanced proof with fingerprint"""
    rotated_salts = get_rotated_salts(timestamp)
    data = f"{timestamp}{user_agent}{fingerprint}{rotated_salts[0].decode()}".encode()
    return hashlib.sha3_256(data).hexdigest()

def generate_love_signature(timestamp, token, proof, totp):
    """Enhanced signature with TOTP"""
    rotated_salts = get_rotated_salts(timestamp)
    data = f"{timestamp}{token}{proof}{totp}".encode()
    return hmac.new(rotated_salts[6], data, hashlib.sha3_512).hexdigest()

def generate_love_commitment(timestamp, token, proof, signature, nonce):
    """Additional commitment header"""
    rotated_salts = get_rotated_salts(timestamp)
    data = f"{timestamp}{token}{proof}{signature}{nonce}".encode()
    return hmac.new(rotated_salts[7], data, hashlib.blake2b).hexdigest()

# ============================================================================
# DEOBFUSCATION (24 layers)
# ============================================================================

def xor_decrypt(data, key):
    """XOR decryption"""
    result = bytearray()
    key_len = len(key)
    for i, byte in enumerate(data):
        result.append(byte ^ key[i % key_len])
    return bytes(result)

def deobfuscate_flag(obfuscated, timestamp):
    """Reverse 24 layers of obfuscation"""
    print("🔓 Deobfuscating flag...")
    
    try:
        # Step 1: Split by @@ and rejoin
        segments = obfuscated.split('@@')
        rejoined = ''.join(segments)
        print("  ✓ Step 1: Rejoined @@ segments")
        
        # Step 2: Base64 decode
        decoded = base64.b64decode(rejoined)
        print("  ✓ Step 2: Base64 decoded")
        
        # Step 3: Split by || and rejoin
        parts = decoded.split(b'||')
        rejoined_parts = b''.join(parts)
        print("  ✓ Step 3: Rejoined || parts")
        
        # Step 4: Base32 decode
        decoded_b32 = base64.b32decode(rejoined_parts)
        print("  ✓ Step 4: Base32 decoded")
        
        # Step 5: Split by :: and rejoin
        chunks = decoded_b32.split(b'::')
        rejoined_chunks = b''.join(chunks)
        print("  ✓ Step 5: Rejoined :: chunks")
        
        # Step 6: Base85 decode
        decoded_b85 = base64.b85decode(rejoined_chunks)
        print("  ✓ Step 6: Base85 decoded")
        
        # Step 7: XOR decrypt
        xor_key = hashlib.sha3_512(
            SECRET_KEY + SALT_PRIMARY + SALT_SECONDARY + str(timestamp).encode()
        ).digest()
        decrypted = xor_decrypt(decoded_b85, xor_key)
        print("  ✓ Step 7: XOR decrypted")
        
        # Step 8: Base64 decode 24 times
        current = decrypted
        for i in range(24):
            current = base64.b64decode(current)
            if (i + 1) % 6 == 0:
                print(f"  ✓ Step 8: Base64 decoded {i + 1}/24 times")
        
        print("  ✓ Step 8: All 24 base64 layers decoded")
        
        return current.decode()
        
    except Exception as e:
        print(f"❌ Deobfuscation failed: {e}")
        return None

# ============================================================================
# TIMING
# ============================================================================
def is_valid_time_window():
    """Check if in valid time window"""
    current = datetime.now(IST)
    return current.hour == 14 and 0 <= current.minute < 30

def wait_for_perfect_moment():
    """Wait for the perfect moment with all constraints"""
    print("⏰ Waiting for the PERFECT moment...")
    print("   Requirements:")
    print("   - Hour: 14 (2 PM IST)")
    print("   - Minutes: 8-13 only")
    print("   - Seconds: 15-45 and EVEN")
    print("   - Timestamp divisible by 21")
    print()
    
    attempts = 0
    while True:
        current = datetime.now(IST)
        minute = current.minute
        second = current.second
        timestamp = int(time.time())
        
        attempts += 1
        if attempts % 10 == 0:
            print(f"   Checking... (attempt {attempts})")
        
        if (8 <= minute <= 13 and 
            15 <= second <= 45 and 
            second % 2 == 0 and 
            timestamp % 21 == 0):
            
            print(f"✅ Perfect moment found!")
            print(f"   - Time: {current.strftime('%H:%M:%S')} IST")
            print(f"   - Minute: {minute}")
            print(f"   - Second: {second}")
            print(f"   - Timestamp: {timestamp}")
            print(f"   - Divisible by 21: ✓")
            return timestamp
        
        time.sleep(0.3)

# ============================================================================
# MAIN SOLVER
# ============================================================================
def solve_challenge(url):
    """Main solver function"""
    print("=" * 70)
    print("Love Is Complicated - NIGHTMARE Difficulty Solver")
    print("Author: MD")
    print("=" * 70)
    print()
    
    # Check time window
    if not is_valid_time_window():
        current = datetime.now(IST)
        print(f"❌ Current time: {current.strftime('%H:%M:%S')} IST")
        print("❌ Must be between 2:00-2:30 PM IST")
        return
    
    current = datetime.now(IST)
    print(f"✅ Time window valid: {current.strftime('%H:%M:%S')} IST")
    print()
    
    # Wait for perfect moment
    timestamp = wait_for_perfect_moment()
    
    # User-Agent (length must be even)
    user_agent = "LoveConfessor/3.0"  # Length 18 (even)
    accept_lang = "en-US,en;q=0.9"
    accept_encoding = "gzip, deflate, br"
    ip_addr = "0.0.0.0"
    
    print()
    print(f"🌐 User-Agent: {user_agent} (length: {len(user_agent)} - EVEN ✓)")
    print()
    
    # Generate fingerprint
    fingerprint = generate_love_fingerprint(user_agent, accept_lang, accept_encoding)
    print(f"🔍 Browser fingerprint: {fingerprint[:32]}...")
    print()
    
    # Solve proof of work
    nonce = solve_proof_of_work(timestamp, difficulty=5)
    print()
    
    # Generate TOTP
    totp = generate_totp(timestamp)
    print(f"🔐 TOTP: {totp}")
    print()
    
    # Generate all cryptographic headers
    print("🔐 Generating 8 cryptographic headers...")
    token = generate_love_token(timestamp, user_agent, ip_addr, fingerprint, totp)
    proof = generate_love_proof(timestamp, user_agent, fingerprint)
    signature = generate_love_signature(timestamp, token, proof, totp)
    commitment = generate_love_commitment(timestamp, token, proof, signature, nonce)
    
    print(f"  ✓ x-love-time: {timestamp}")
    print(f"  ✓ x-love-token: {token[:40]}...")
    print(f"  ✓ x-love-proof: {proof[:40]}...")
    print(f"  ✓ x-love-signature: {signature[:40]}...")
    print(f"  ✓ x-love-totp: {totp}")
    print(f"  ✓ x-love-commitment: {commitment[:40]}...")
    print(f"  ✓ x-love-fingerprint: {fingerprint}")
    print(f"  ✓ x-love-nonce: {nonce}")
    print()
    
    # Prepare headers
    headers = {
        'x-love-time': str(timestamp),
        'x-love-token': token,
        'x-love-proof': proof,
        'x-love-signature': signature,
        'x-love-totp': totp,
        'x-love-commitment': commitment,
        'x-love-fingerprint': fingerprint,
        'x-love-nonce': nonce,
        'User-Agent': user_agent,
        'Accept-Language': accept_lang,
        'Accept-Encoding': accept_encoding,
        'Content-Type': 'application/json'
    }
    
    # Send request
    print("💌 Sending confession to the server...")
    try:
        response = requests.post(f"{url}/api/confess", headers=headers, json={})
        print(f"📡 Status: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Request accepted!")
            print(f"💡 Message: {data.get('message')}")
            print()
            
            obfuscated_flag = data.get('data')
            flag = deobfuscate_flag(obfuscated_flag, timestamp)
            
            if flag:
                print("=" * 70)
                print("🎉 FLAG FOUND!")
                print("=" * 70)
                print(f"🚩 {flag}")
                print("=" * 70)
                print()
                
                # Check if it's a decoy
                decoy_keywords = ["n1c3_try", "d3c0y", "cl0s3_but", "4lm0st", 
                                 "wr0ng", "n0t_th3", "try_4g41n"]
                if any(word in flag for word in decoy_keywords):
                    print("⚠️  DECOY FLAG DETECTED!")
                    print("💡 Check all constraints:")
                    print("   - Minutes 8-13? Seconds 15-45 even?")
                    print("   - Timestamp % 21 == 0?")
                    print("   - UA length even?")
                    print("   - All 8 headers correct?")
                else:
                    print("✅ REAL FLAG! Challenge complete! 🎉🎉🎉")
                    print("🏆 NIGHTMARE difficulty conquered!")
            
        elif response.status_code == 429:
            data = response.json()
            print(f"⏳ Rate limited! Wait {data.get('wait_seconds')} seconds")
            if 'decoy_flag' in data:
                print(f"🎭 Decoy flag: {data['decoy_flag']}")
        else:
            data = response.json()
            print(f"❌ Error: {data.get('error')}")
            if 'decoy_flag' in data:
                print(f"🎭 Decoy flag: {data['decoy_flag']}")
            if 'hint' in data:
                print(f"💡 Hint: {data['hint']}")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1].rstrip('/')
    else:
        url = input("Challenge URL: ").rstrip('/')
    
    solve_challenge(url)
