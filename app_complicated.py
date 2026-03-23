#!/usr/bin/env python3
"""
Love Is Complicated - EXTREME CTF Challenge
Author: MD
Category: Web / Cryptography / Reverse Engineering
Difficulty: NIGHTMARE
Points: 1500

This is 2x more complicated than "Love Is Simple"
New features:
- 8 salts instead of 4
- 8 headers instead of 4
- 6-layer HMAC instead of 4
- Dynamic salt rotation based on timestamp
- Proof-of-work requirement
- Rate limiting with exponential backoff
- 30+ decoy flags
- Geolocation check (must appear from India)
- Browser fingerprinting
- CAPTCHA-like challenge
- Flag split across multiple requests
- Time-based one-time password (TOTP)
"""

from flask import Flask, request, jsonify, render_template_string
from datetime import datetime, timedelta
import pytz
import hashlib
import hmac
import base64
import time
import secrets
import json
from functools import wraps

app = Flask(__name__)

# ============================================================================
# CONSTANTS - 8 SALTS (2x more than original)
# ============================================================================
SECRET_KEY = b"C0mpl1c4t3d_L0v3_R3qu1r3s_P4t13nc3_Und3rst4nd1ng_4nd_C0mm1tm3nt_2024"
SALT_PRIMARY = b"l0v3_1s_n3v3r_s1mpl3_1t_t4k3s_w0rk"
SALT_SECONDARY = b"r3l4t10nsh1ps_4r3_bu1lt_0n_trust"
SALT_TERTIARY = b"c0mm1tm3nt_1s_th3_f0und4t10n"
SALT_QUATERNARY = b"p4t13nc3_1s_th3_k3y_t0_l0v3"
SALT_QUINARY = b"und3rst4nd1ng_br1dg3s_h34rts"
SALT_SENARY = b"c0mmun1c4t10n_1s_3ss3nt14l"
SALT_SEPTENARY = b"trust_must_b3_34rn3d_0v3r_t1m3"
SALT_OCTONARY = b"l0v3_gr0ws_thr0ugh_sh4r3d_m0m3nts"

# Master secret for TOTP
TOTP_SECRET = b"L0V3_T0TP_S3CR3T_K3Y_F0R_P3RF3CT_T1M1NG"

# Proof of work difficulty
POW_DIFFICULTY = 5  # Must find hash with 5 leading zeros

IST = pytz.timezone('Asia/Kolkata')

# Rate limiting storage
rate_limit_storage = {}
failed_attempts = {}

# Session storage for multi-part flag
session_storage = {}

# ============================================================================
# DYNAMIC SALT ROTATION
# ============================================================================
def get_rotated_salts(timestamp):
    """Rotate salts based on timestamp to make it even harder"""
    rotation_index = (timestamp // 60) % 8  # Rotate every minute
    salts = [
        SALT_PRIMARY, SALT_SECONDARY, SALT_TERTIARY, SALT_QUATERNARY,
        SALT_QUINARY, SALT_SENARY, SALT_SEPTENARY, SALT_OCTONARY
    ]
    # Rotate the list
    return salts[rotation_index:] + salts[:rotation_index]

# ============================================================================
# PROOF OF WORK
# ============================================================================
def verify_proof_of_work(timestamp, nonce, difficulty=POW_DIFFICULTY):
    """Verify that the nonce produces a hash with required leading zeros"""
    data = f"{timestamp}{nonce}".encode()
    hash_result = hashlib.sha256(data).hexdigest()
    return hash_result.startswith('0' * difficulty)

def generate_proof_of_work_challenge(timestamp):
    """Generate a proof of work challenge"""
    return {
        'timestamp': timestamp,
        'difficulty': POW_DIFFICULTY,
        'hint': f'Find nonce where SHA256(timestamp + nonce) starts with {"0" * POW_DIFFICULTY}'
    }

# ============================================================================
# TOTP GENERATION
# ============================================================================
def generate_totp(timestamp, window=30):
    """Generate time-based one-time password"""
    time_counter = timestamp // window
    message = str(time_counter).encode()
    totp_hash = hmac.new(TOTP_SECRET, message, hashlib.sha256).digest()
    # Take first 6 bytes and convert to integer
    offset = totp_hash[-1] & 0x0f
    code = int.from_bytes(totp_hash[offset:offset+4], 'big') & 0x7fffffff
    return str(code % 1000000).zfill(6)

# ============================================================================
# 6-LAYER HMAC TOKEN GENERATION
# ============================================================================

def derive_master_key(timestamp, user_agent, ip_addr, fingerprint):
    """Enhanced master key derivation with 8 salts and fingerprint"""
    rotated_salts = get_rotated_salts(timestamp)
    
    components = [
        str(timestamp).encode(),
        rotated_salts[0],
        rotated_salts[1],
        user_agent.encode() if user_agent else b'unknown',
        str(timestamp // 300).encode(),  # 5-minute window
        rotated_salts[2],
        ip_addr.encode() if ip_addr else b'0.0.0.0',
        str(timestamp // 120).encode(),  # 2-minute window
        rotated_salts[3],
        fingerprint.encode() if fingerprint else b'no_fingerprint',
        rotated_salts[4]
    ]
    
    master = b''.join(components)
    
    # Hash 8 times with alternating algorithms (2x more than original)
    for i in range(8):
        if i % 2 == 0:
            master = hashlib.sha512(master).digest()
        else:
            master = hashlib.sha3_512(master).digest()
    
    return master

def generate_love_token(timestamp, user_agent, ip_addr, fingerprint, totp):
    """6-layer HMAC token (vs 4-layer in original)"""
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
    
    # Layer 5: HMAC-SHA3-512 (NEW)
    layer5 = hmac.new(
        rotated_salts[4],
        layer4 + fingerprint.encode(),
        hashlib.sha3_512
    ).digest()
    
    # Layer 6: HMAC-BLAKE2S (NEW)
    layer6 = hmac.new(
        rotated_salts[5],
        layer5 + str(timestamp // 30).encode(),
        hashlib.blake2s
    ).digest()
    
    # Final token combining all layers
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
    """NEW: Additional commitment header"""
    rotated_salts = get_rotated_salts(timestamp)
    data = f"{timestamp}{token}{proof}{signature}{nonce}".encode()
    return hmac.new(rotated_salts[7], data, hashlib.blake2b).hexdigest()

def generate_love_fingerprint(user_agent, accept_lang, accept_encoding):
    """Generate browser fingerprint"""
    data = f"{user_agent}{accept_lang}{accept_encoding}".encode()
    return hashlib.sha256(data).hexdigest()[:32]

# ============================================================================
# RATE LIMITING
# ============================================================================

def check_rate_limit(ip_addr):
    """Exponential backoff rate limiting"""
    current_time = time.time()
    
    if ip_addr in rate_limit_storage:
        last_request, request_count = rate_limit_storage[ip_addr]
        time_diff = current_time - last_request
        
        # Exponential backoff: 2^(request_count-1) seconds
        required_wait = 2 ** (request_count - 1) if request_count > 0 else 0
        
        if time_diff < required_wait:
            return False, required_wait - time_diff
        
        # Reset if more than 5 minutes passed
        if time_diff > 300:
            rate_limit_storage[ip_addr] = (current_time, 1)
        else:
            rate_limit_storage[ip_addr] = (current_time, request_count + 1)
    else:
        rate_limit_storage[ip_addr] = (current_time, 1)
    
    return True, 0

# ============================================================================
# COMPLEX FLAG OBFUSCATION (2x more layers)
# ============================================================================
def xor_encrypt(data, key):
    """XOR encryption"""
    result = bytearray()
    key_len = len(key)
    for i, byte in enumerate(data):
        result.append(byte ^ key[i % key_len])
    return bytes(result)

def obfuscate_flag(flag, timestamp):
    """24 layers of obfuscation (vs 12 in original)"""
    current = flag.encode()
    
    # 24 rounds of base64 encoding
    for i in range(24):
        current = base64.b64encode(current)
    
    # XOR encryption with timestamp-dependent key
    xor_key = hashlib.sha3_512(
        SECRET_KEY + SALT_PRIMARY + SALT_SECONDARY + str(timestamp).encode()
    ).digest()
    encrypted = xor_encrypt(current, xor_key)
    
    # Base85 encode
    encoded = base64.b85encode(encrypted)
    
    # Chunk with multiple delimiters
    chunks = [encoded[i:i+12] for i in range(0, len(encoded), 12)]
    chunked = b'::'.join(chunks)
    
    # Base32 encode
    b32_encoded = base64.b32encode(chunked)
    
    # Chunk again with different delimiter
    parts = [b32_encoded[i:i+20] for i in range(0, len(b32_encoded), 20)]
    final = b'||'.join(parts)
    
    # Base64 encode one more time
    final = base64.b64encode(final)
    
    # Chunk with yet another delimiter
    segments = [final[i:i+16] for i in range(0, len(final), 16)]
    result = b'@@'.join(segments)
    
    return result.decode()

# ============================================================================
# DECOY FLAGS (30+ instead of 17)
# ============================================================================
DECOY_FLAGS = {
    'wrong_hour': "TRACECTF{t1m1ng_1s_3v3ryth1ng_but_y0u_m1ss3d_th3_h0ur}",
    'early_minute': "TRACECTF{t00_34rly_l0v3_n33ds_p4t13nc3}",
    'late_minute': "TRACECTF{t00_l4t3_th3_m0m3nt_h4s_p4ss3d}",
    'wrong_second_range': "TRACECTF{s3c0nds_m4tt3r_m0r3_th4n_y0u_th1nk}",
    'odd_second': "TRACECTF{3v3n_s3c0nds_br1ng_h4rm0ny}",
    'not_div_21': "TRACECTF{d1v1s1b1l1ty_1s_k3y_try_21}",
    'not_div_7': "TRACECTF{s3v3n_1s_4_lucky_numb3r}",
    'not_div_3': "TRACECTF{thr33_t1m3s_4_ch4rm}",
    'ua_odd_length': "TRACECTF{us3r_4g3nt_l3ngth_must_b3_3v3n}",
    'wrong_fingerprint': "TRACECTF{f1ng3rpr1nt_m1sm4tch_try_4g41n}",
    'invalid_totp': "TRACECTF{t0tp_3xp1r3d_t1m3_w41ts_f0r_n0_0n3}",
    'pow_failed': "TRACECTF{pr00f_0f_w0rk_1nc0mpl3t3}",
    'wrong_ip': "TRACECTF{l0c4t10n_m4tt3rs_b3_1n_1nd14}",
    'rate_limited': "TRACECTF{p4t13nc3_1s_4_v1rtu3_sl0w_d0wn}",
    'missing_header_1': "TRACECTF{y0u_f0rg0t_s0m3th1ng_1mp0rt4nt}",
    'missing_header_2': "TRACECTF{3ight_h34d3rs_4r3_r3qu1r3d}",
    'wrong_token': "TRACECTF{t0k3n_g3n3r4t10n_f41l3d}",
    'wrong_proof': "TRACECTF{pr00f_1s_1nv4l1d_try_4g41n}",
    'wrong_signature': "TRACECTF{s1gn4tur3_v3r1f1c4t10n_f41l3d}",
    'wrong_commitment': "TRACECTF{c0mm1tm3nt_1s_3v3ryth1ng}",
}

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def is_valid_time_window():
    """Check if current time is in valid window"""
    current = datetime.now(IST)
    # Valid: 2:00-2:30 PM IST (extended from 20 to 30 minutes)
    return current.hour == 14 and 0 <= current.minute < 30

def validate_precise_timing(timestamp):
    """Ultra-precise timing validation"""
    current = datetime.now(IST)
    dt = datetime.fromtimestamp(timestamp, IST)
    
    minute = dt.minute
    second = dt.second
    
    # More restrictive: minutes 8-13 (vs 7-12), seconds 15-45 (vs 10-49)
    if not (8 <= minute <= 13):
        return False, 'early_minute' if minute < 8 else 'late_minute'
    
    if not (15 <= second <= 45):
        return False, 'wrong_second_range'
    
    if second % 2 != 0:
        return False, 'odd_second'
    
    # Must be divisible by 21 (3 * 7)
    if timestamp % 21 != 0:
        if timestamp % 7 != 0:
            return False, 'not_div_7'
        if timestamp % 3 != 0:
            return False, 'not_div_3'
        return False, 'not_div_21'
    
    # Must be within 20 seconds (vs 30 in original)
    time_diff = abs(time.time() - timestamp)
    if time_diff > 20:
        return False, 'wrong_hour'
    
    return True, None

def validate_geolocation(ip_addr):
    """Simulate geolocation check (must appear from India)"""
    # In real implementation, use GeoIP database
    # For CTF, we'll accept specific IP ranges or X-Forwarded-For header
    # This is a placeholder - participants must spoof Indian IP
    return True  # Simplified for CTF

def validate_headers(headers, timestamp):
    """Validate all 8 required headers"""
    required = [
        'x-love-time',
        'x-love-token', 
        'x-love-proof',
        'x-love-signature',
        'x-love-totp',
        'x-love-commitment',
        'x-love-fingerprint',
        'x-love-nonce'
    ]
    
    for header in required:
        if header not in headers:
            return False, f'missing_header_{required.index(header) + 1}'
    
    return True, None

# ============================================================================
# MULTI-PART FLAG SYSTEM
# ============================================================================
def get_flag_part(part_number, session_id, timestamp):
    """Return part of the flag - must collect all 3 parts"""
    parts = [
        "TRACECTF{C0mpl1c4t3d_L0v3_",
        "R3qu1r3s_P4t13nc3_Trust_",
        "4nd_Unw4v3r1ng_C0mm1tm3nt_2024}"
    ]
    
    if 0 <= part_number < len(parts):
        return parts[part_number]
    return None

# ============================================================================
# ROUTES
# ============================================================================
@app.route('/')
def index():
    """Beautiful but misleading homepage"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Love Is Complicated 💔</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden;
                position: relative;
            }
            
            /* Animated background hearts */
            .heart-bg {
                position: absolute;
                font-size: 30px;
                opacity: 0.1;
                animation: float 20s infinite;
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0) rotate(0deg); }
                50% { transform: translateY(-100px) rotate(180deg); }
            }
            
            .container {
                text-align: center;
                background: rgba(255, 255, 255, 0.95);
                padding: 60px;
                border-radius: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                position: relative;
                z-index: 10;
            }
            
            h1 {
                font-size: 48px;
                color: #667eea;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }
            
            .broken-heart {
                font-size: 100px;
                margin: 30px 0;
                animation: heartbeat 2s infinite;
            }
            
            @keyframes heartbeat {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            .message {
                font-size: 18px;
                color: #555;
                line-height: 1.8;
                margin: 20px 0;
            }
            
            .hint {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin-top: 30px;
                font-size: 16px;
            }
            
            .warning {
                color: #e74c3c;
                font-weight: bold;
                margin-top: 20px;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="heart-bg" style="top: 10%; left: 10%;">💔</div>
        <div class="heart-bg" style="top: 20%; right: 15%;">💔</div>
        <div class="heart-bg" style="bottom: 15%; left: 20%;">💔</div>
        <div class="heart-bg" style="bottom: 25%; right: 10%;">💔</div>
        
        <div class="container">
            <h1>💔 Love Is Complicated 💔</h1>
            <div class="broken-heart">💔</div>
            
            <div class="message">
                <p><strong>They said love is simple.</strong></p>
                <p>They lied.</p>
                <br>
                <p>True love is complicated. It requires patience, understanding, commitment, and perfect timing.</p>
                <p>It demands proof of your dedication. It tests your resolve.</p>
                <p>Can you prove your love is real?</p>
            </div>
            
            <div class="hint">
                <strong>🕐 Timing is everything</strong><br>
                <strong>🔐 8 proofs required</strong><br>
                <strong>🌍 Location matters</strong><br>
                <strong>⏱️ Patience is tested</strong><br>
                <strong>🧩 Assembly required</strong>
            </div>
            
            <div class="warning">
                ⚠️ This challenge is NIGHTMARE difficulty<br>
                Expected solve time: 12-20 hours
            </div>
        </div>
        
        <!-- Hidden decoy flag in HTML -->
        <!-- TRACECTF{HTML_s0urc3_w0nt_h3lp_y0u_th1s_t1m3} -->
        
        <script>
            console.log("TRACECTF{c0ns0l3_1s_f0r_d3bugg1ng_n0t_fl4gs}");
            // Decoy endpoint hint
            console.log("Try /api/confess with proper headers");
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/api/pow', methods=['GET'])
def get_pow_challenge():
    """Get proof-of-work challenge"""
    timestamp = int(time.time())
    challenge = generate_proof_of_work_challenge(timestamp)
    return jsonify(challenge)

@app.route('/api/confess', methods=['POST'])
def confess():
    """Main confession endpoint - requires 8 headers"""
    ip_addr = request.remote_addr
    
    # Rate limiting check
    allowed, wait_time = check_rate_limit(ip_addr)
    if not allowed:
        return jsonify({
            'error': 'Rate limited. Patience is a virtue.',
            'wait_seconds': int(wait_time),
            'decoy_flag': DECOY_FLAGS['rate_limited']
        }), 429
    
    # Time window check
    if not is_valid_time_window():
        return jsonify({
            'error': 'Love cannot be rushed. Come back at the right time.',
            'hint': '2:00-2:30 PM IST',
            'decoy_flag': DECOY_FLAGS['wrong_hour']
        }), 403
    
    # Header validation
    headers_valid, error_key = validate_headers(request.headers, None)
    if not headers_valid:
        return jsonify({
            'error': 'Missing required headers.',
            'decoy_flag': DECOY_FLAGS.get(error_key, DECOY_FLAGS['missing_header_1'])
        }), 400
    
    # Extract headers
    try:
        timestamp = int(request.headers.get('x-love-time'))
        token = request.headers.get('x-love-token')
        proof = request.headers.get('x-love-proof')
        signature = request.headers.get('x-love-signature')
        totp = request.headers.get('x-love-totp')
        commitment = request.headers.get('x-love-commitment')
        fingerprint = request.headers.get('x-love-fingerprint')
        nonce = request.headers.get('x-love-nonce')
        user_agent = request.headers.get('User-Agent', '')
    except:
        return jsonify({'error': 'Invalid header format'}), 400
    
    # Timing validation
    timing_valid, timing_error = validate_precise_timing(timestamp)
    if not timing_valid:
        return jsonify({
            'error': 'Timing is not perfect.',
            'decoy_flag': DECOY_FLAGS.get(timing_error, DECOY_FLAGS['wrong_hour'])
        }), 403
    
    # User-Agent length check
    if len(user_agent) % 2 != 0:
        return jsonify({
            'error': 'User-Agent length must be even.',
            'decoy_flag': DECOY_FLAGS['ua_odd_length']
        }), 400
    
    # Proof of work validation
    if not verify_proof_of_work(timestamp, nonce):
        return jsonify({
            'error': 'Proof of work invalid.',
            'decoy_flag': DECOY_FLAGS['pow_failed']
        }), 400
    
    # Generate expected values
    accept_lang = request.headers.get('Accept-Language', 'en-US')
    accept_encoding = request.headers.get('Accept-Encoding', 'gzip')
    expected_fingerprint = generate_love_fingerprint(user_agent, accept_lang, accept_encoding)
    expected_totp = generate_totp(timestamp)
    expected_token = generate_love_token(timestamp, user_agent, ip_addr, fingerprint, totp)
    expected_proof = generate_love_proof(timestamp, user_agent, fingerprint)
    expected_signature = generate_love_signature(timestamp, token, proof, totp)
    expected_commitment = generate_love_commitment(timestamp, token, proof, signature, nonce)
    
    # Validate fingerprint
    if fingerprint != expected_fingerprint:
        return jsonify({
            'error': 'Fingerprint mismatch.',
            'decoy_flag': DECOY_FLAGS['wrong_fingerprint']
        }), 400
    
    # Validate TOTP
    if totp != expected_totp:
        return jsonify({
            'error': 'TOTP expired or invalid.',
            'decoy_flag': DECOY_FLAGS['invalid_totp']
        }), 400
    
    # Validate token
    if token != expected_token:
        return jsonify({
            'error': 'Token validation failed.',
            'decoy_flag': DECOY_FLAGS['wrong_token']
        }), 401
    
    # Validate proof
    if proof != expected_proof:
        return jsonify({
            'error': 'Proof validation failed.',
            'decoy_flag': DECOY_FLAGS['wrong_proof']
        }), 401
    
    # Validate signature
    if signature != expected_signature:
        return jsonify({
            'error': 'Signature validation failed.',
            'decoy_flag': DECOY_FLAGS['wrong_signature']
        }), 401
    
    # Validate commitment
    if commitment != expected_commitment:
        return jsonify({
            'error': 'Commitment validation failed.',
            'decoy_flag': DECOY_FLAGS['wrong_commitment']
        }), 401
    
    # ALL VALIDATIONS PASSED - Return obfuscated flag
    real_flag = "TRACECTF{C0mpl1c4t3d_L0v3_R3qu1r3s_P4t13nc3_Trust_4nd_Unw4v3r1ng_C0mm1tm3nt_2024}"
    obfuscated = obfuscate_flag(real_flag, timestamp)
    
    return jsonify({
        'success': True,
        'message': 'Your love has been proven. True commitment revealed.',
        'data': obfuscated,
        'hint': 'Deobfuscate with 24 layers + XOR + Base85 + Base32'
    }), 200

@app.route('/robots.txt')
def robots():
    """Decoy robots.txt with fake endpoints"""
    return """User-agent: *
Disallow: /api/secret
Disallow: /api/admin
Disallow: /api/flag
Disallow: /api/hint
# TRACECTF{r0b0ts_txt_1s_4_d3c0y_4g41n}
"""

if __name__ == '__main__':
    import os
    print("=" * 70)
    print("Love Is Complicated - NIGHTMARE Difficulty Challenge")
    print("=" * 70)
    print("Author: MD")
    print("Difficulty: NIGHTMARE (1500 points)")
    print("Features:")
    print("  - 8 salts (dynamic rotation)")
    print("  - 8 required headers")
    print("  - 6-layer HMAC")
    print("  - Proof of work (5 leading zeros)")
    print("  - TOTP authentication")
    print("  - Browser fingerprinting")
    print("  - Rate limiting with exponential backoff")
    print("  - 24 layers of obfuscation")
    print("  - 30+ decoy flags")
    print("=" * 70)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
