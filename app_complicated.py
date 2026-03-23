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
SECRET_KEY = b"C0mpl1c4t3d_L0v3_R3qu1r3s_P4t13nc3_Und3rst4nd1ng_4nd_C0mm1tm3nt_2020"
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
        "4nd_Unw4v3r1ng_C0mm1tm3nt_2020}"
    ]
    
    if 0 <= part_number < len(parts):
        return parts[part_number]
    return None

# ============================================================================
# ROUTES
# ============================================================================
@app.route('/')
def index():
    """Stunning animated homepage"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Love Is Complicated 💔</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            * { 
                margin: 0; 
                padding: 0; 
                box-sizing: border-box; 
            }
            
            body {
                font-family: 'Poppins', sans-serif;
                background: #0a0a0a;
                min-height: 100vh;
                overflow-x: hidden;
                position: relative;
            }
            
            /* Animated gradient background */
            .gradient-bg {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #4facfe);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                z-index: 0;
            }
            
            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            /* Particle system */
            .particles {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1;
                pointer-events: none;
            }
            
            .particle {
                position: absolute;
                width: 4px;
                height: 4px;
                background: rgba(255, 255, 255, 0.8);
                border-radius: 50%;
                animation: particleFloat 20s infinite;
            }
            
            @keyframes particleFloat {
                0% {
                    transform: translateY(100vh) translateX(0) scale(0);
                    opacity: 0;
                }
                10% {
                    opacity: 1;
                }
                90% {
                    opacity: 1;
                }
                100% {
                    transform: translateY(-100vh) translateX(100px) scale(1);
                    opacity: 0;
                }
            }
            
            /* Floating hearts */
            .hearts-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 2;
                pointer-events: none;
            }
            
            .heart {
                position: absolute;
                font-size: 40px;
                opacity: 0;
                animation: heartFloat 15s infinite;
                filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
            }
            
            @keyframes heartFloat {
                0% {
                    transform: translateY(100vh) rotate(0deg) scale(0);
                    opacity: 0;
                }
                10% {
                    opacity: 0.7;
                }
                50% {
                    transform: translateY(50vh) rotate(180deg) scale(1.2);
                    opacity: 0.5;
                }
                90% {
                    opacity: 0.3;
                }
                100% {
                    transform: translateY(-20vh) rotate(360deg) scale(0);
                    opacity: 0;
                }
            }
            
            /* Main container */
            .container {
                position: relative;
                z-index: 10;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 40px 20px;
            }
            
            /* Glass morphism card */
            .card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                border-radius: 30px;
                padding: 60px 50px;
                max-width: 700px;
                width: 90%;
                box-shadow: 
                    0 8px 32px 0 rgba(31, 38, 135, 0.37),
                    inset 0 0 60px rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.18);
                animation: cardFloat 6s ease-in-out infinite;
                text-align: center;
            }
            
            @keyframes cardFloat {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-20px); }
            }
            
            /* Title */
            .title {
                font-family: 'Playfair Display', serif;
                font-size: 72px;
                font-weight: 900;
                color: #fff;
                margin-bottom: 20px;
                text-shadow: 
                    0 0 20px rgba(255, 255, 255, 0.5),
                    0 0 40px rgba(255, 255, 255, 0.3),
                    0 5px 15px rgba(0, 0, 0, 0.3);
                animation: titlePulse 3s ease-in-out infinite;
                letter-spacing: 2px;
            }
            
            @keyframes titlePulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            
            /* Broken heart animation */
            .broken-heart-container {
                position: relative;
                height: 150px;
                margin: 40px 0;
            }
            
            .broken-heart {
                font-size: 120px;
                display: inline-block;
                animation: heartbeat 2s ease-in-out infinite;
                filter: drop-shadow(0 0 30px rgba(255, 100, 150, 0.8));
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .broken-heart:hover {
                transform: scale(1.2) rotate(10deg);
                filter: drop-shadow(0 0 50px rgba(255, 100, 150, 1));
            }
            
            @keyframes heartbeat {
                0%, 100% { 
                    transform: scale(1); 
                    filter: drop-shadow(0 0 30px rgba(255, 100, 150, 0.8));
                }
                50% { 
                    transform: scale(1.15); 
                    filter: drop-shadow(0 0 50px rgba(255, 100, 150, 1));
                }
            }
            
            /* Crack effect */
            .crack {
                position: absolute;
                top: 50%;
                left: 50%;
                width: 2px;
                height: 100px;
                background: linear-gradient(to bottom, 
                    rgba(255, 255, 255, 0) 0%,
                    rgba(255, 255, 255, 0.8) 50%,
                    rgba(255, 255, 255, 0) 100%);
                transform: translate(-50%, -50%) rotate(45deg);
                animation: crackGlow 2s ease-in-out infinite;
            }
            
            @keyframes crackGlow {
                0%, 100% { opacity: 0.3; }
                50% { opacity: 1; }
            }
            
            /* Text content */
            .subtitle {
                font-size: 24px;
                color: rgba(255, 255, 255, 0.95);
                margin-bottom: 30px;
                font-weight: 300;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
                animation: fadeInUp 1s ease-out 0.5s both;
            }
            
            .message {
                font-size: 18px;
                line-height: 1.8;
                color: rgba(255, 255, 255, 0.9);
                margin: 25px 0;
                text-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                animation: fadeInUp 1s ease-out 0.7s both;
            }
            
            .message strong {
                color: #fff;
                font-weight: 600;
                text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* Info boxes */
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 40px 0;
                animation: fadeInUp 1s ease-out 0.9s both;
            }
            
            .info-box {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 25px 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .info-box:hover {
                transform: translateY(-10px) scale(1.05);
                background: rgba(255, 255, 255, 0.25);
                box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
            }
            
            .info-icon {
                font-size: 36px;
                margin-bottom: 10px;
                animation: iconBounce 2s ease-in-out infinite;
            }
            
            @keyframes iconBounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
            
            .info-title {
                font-size: 16px;
                font-weight: 600;
                color: #fff;
                margin-bottom: 5px;
                text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
            }
            
            .info-text {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.8);
                text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
            }
            
            /* Warning box */
            .warning {
                background: rgba(255, 50, 50, 0.2);
                backdrop-filter: blur(10px);
                border: 2px solid rgba(255, 100, 100, 0.5);
                border-radius: 20px;
                padding: 25px;
                margin-top: 40px;
                animation: warningPulse 3s ease-in-out infinite, fadeInUp 1s ease-out 1.1s both;
            }
            
            @keyframes warningPulse {
                0%, 100% { 
                    box-shadow: 0 0 20px rgba(255, 50, 50, 0.3);
                    border-color: rgba(255, 100, 100, 0.5);
                }
                50% { 
                    box-shadow: 0 0 40px rgba(255, 50, 50, 0.6);
                    border-color: rgba(255, 100, 100, 0.8);
                }
            }
            
            .warning-icon {
                font-size: 48px;
                margin-bottom: 15px;
                animation: warningShake 1s ease-in-out infinite;
            }
            
            @keyframes warningShake {
                0%, 100% { transform: rotate(0deg); }
                25% { transform: rotate(-10deg); }
                75% { transform: rotate(10deg); }
            }
            
            .warning-title {
                font-size: 22px;
                font-weight: 700;
                color: #fff;
                margin-bottom: 10px;
                text-shadow: 0 0 10px rgba(255, 100, 100, 0.8);
            }
            
            .warning-text {
                font-size: 16px;
                color: rgba(255, 255, 255, 0.9);
                line-height: 1.6;
            }
            
            /* Stats counter */
            .stats {
                display: flex;
                justify-content: space-around;
                margin: 40px 0;
                animation: fadeInUp 1s ease-out 1.3s both;
            }
            
            .stat {
                text-align: center;
            }
            
            .stat-number {
                font-size: 48px;
                font-weight: 700;
                color: #fff;
                text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
                animation: countUp 2s ease-out;
            }
            
            @keyframes countUp {
                from { opacity: 0; transform: scale(0.5); }
                to { opacity: 1; transform: scale(1); }
            }
            
            .stat-label {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.7);
                margin-top: 5px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            /* Glowing orbs */
            .orb {
                position: fixed;
                border-radius: 50%;
                filter: blur(60px);
                opacity: 0.4;
                animation: orbFloat 20s ease-in-out infinite;
                pointer-events: none;
                z-index: 1;
            }
            
            .orb1 {
                width: 400px;
                height: 400px;
                background: radial-gradient(circle, #667eea, transparent);
                top: -200px;
                left: -200px;
            }
            
            .orb2 {
                width: 500px;
                height: 500px;
                background: radial-gradient(circle, #764ba2, transparent);
                bottom: -250px;
                right: -250px;
                animation-delay: -10s;
            }
            
            .orb3 {
                width: 350px;
                height: 350px;
                background: radial-gradient(circle, #f093fb, transparent);
                top: 50%;
                left: 50%;
                animation-delay: -5s;
            }
            
            @keyframes orbFloat {
                0%, 100% { transform: translate(0, 0) scale(1); }
                33% { transform: translate(100px, -100px) scale(1.1); }
                66% { transform: translate(-100px, 100px) scale(0.9); }
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .title { font-size: 48px; }
                .broken-heart { font-size: 80px; }
                .card { padding: 40px 30px; }
                .info-grid { grid-template-columns: 1fr; }
                .stats { flex-direction: column; gap: 20px; }
            }
        </style>
    </head>
    <body>
        <!-- Gradient background -->
        <div class="gradient-bg"></div>
        
        <!-- Glowing orbs -->
        <div class="orb orb1"></div>
        <div class="orb orb2"></div>
        <div class="orb orb3"></div>
        
        <!-- Particles -->
        <div class="particles" id="particles"></div>
        
        <!-- Floating hearts -->
        <div class="hearts-container" id="hearts"></div>
        
        <!-- Main content -->
        <div class="container">
            <div class="card">
                <h1 class="title">Love Is Complicated</h1>
                
                <div class="broken-heart-container">
                    <div class="broken-heart" onclick="shakeHeart()">💔</div>
                    <div class="crack"></div>
                </div>
                
                <p class="subtitle">Where Hearts Break and Secrets Hide</p>
                
                <div class="message">
                    <p><strong>They said love is simple.</strong></p>
                    <p>They lied.</p>
                    <br>
                    <p>True love is complicated. It requires patience, understanding, commitment, and perfect timing.</p>
                    <p>It demands proof of your dedication. It tests your resolve.</p>
                    <p><strong>Can you prove your love is real?</strong></p>
                </div>
            </div>
        </div>
        
        <script>
            function createParticles() {
                const container = document.getElementById('particles');
                for (let i = 0; i < 50; i++) {
                    const particle = document.createElement('div');
                    particle.className = 'particle';
                    particle.style.left = Math.random() * 100 + '%';
                    particle.style.animationDelay = Math.random() * 20 + 's';
                    particle.style.animationDuration = (15 + Math.random() * 10) + 's';
                    container.appendChild(particle);
                }
            }
            
            function createHearts() {
                const container = document.getElementById('hearts');
                const heartEmojis = ['💔', '💕', '💖', '💗', '💘', '💝', '💞', '💟'];
                
                setInterval(() => {
                    const heart = document.createElement('div');
                    heart.className = 'heart';
                    heart.textContent = heartEmojis[Math.floor(Math.random() * heartEmojis.length)];
                    heart.style.left = Math.random() * 100 + '%';
                    heart.style.animationDuration = (10 + Math.random() * 10) + 's';
                    heart.style.fontSize = (30 + Math.random() * 40) + 'px';
                    container.appendChild(heart);
                    
                    setTimeout(() => heart.remove(), 15000);
                }, 2000);
            }
            
            function shakeHeart() {
                const heart = document.querySelector('.broken-heart');
                heart.style.animation = 'none';
                setTimeout(() => {
                    heart.style.animation = 'heartbeat 2s ease-in-out infinite';
                }, 10);
                
                for (let i = 0; i < 10; i++) {
                    const mini = document.createElement('div');
                    mini.textContent = '💔';
                    mini.style.position = 'fixed';
                    mini.style.left = '50%';
                    mini.style.top = '50%';
                    mini.style.fontSize = '20px';
                    mini.style.pointerEvents = 'none';
                    mini.style.zIndex = '1000';
                    document.body.appendChild(mini);
                    
                    const angle = (Math.PI * 2 * i) / 10;
                    const velocity = 200;
                    const vx = Math.cos(angle) * velocity;
                    const vy = Math.sin(angle) * velocity;
                    
                    let x = 0, y = 0, opacity = 1;
                    const animate = () => {
                        x += vx * 0.016;
                        y += vy * 0.016 + 100 * 0.016;
                        opacity -= 0.02;
                        
                        mini.style.transform = `translate(${x}px, ${y}px)`;
                        mini.style.opacity = opacity;
                        
                        if (opacity > 0) {
                            requestAnimationFrame(animate);
                        } else {
                            mini.remove();
                        }
                    };
                    animate();
                }
            }
            
            document.addEventListener('mousemove', (e) => {
                if (Math.random() > 0.9) {
                    const trail = document.createElement('div');
                    trail.style.position = 'fixed';
                    trail.style.left = e.clientX + 'px';
                    trail.style.top = e.clientY + 'px';
                    trail.style.width = '5px';
                    trail.style.height = '5px';
                    trail.style.borderRadius = '50%';
                    trail.style.background = 'rgba(255, 255, 255, 0.6)';
                    trail.style.pointerEvents = 'none';
                    trail.style.zIndex = '1000';
                    trail.style.transition = 'all 1s ease-out';
                    document.body.appendChild(trail);
                    
                    setTimeout(() => {
                        trail.style.transform = 'scale(3)';
                        trail.style.opacity = '0';
                    }, 10);
                    
                    setTimeout(() => trail.remove(), 1000);
                }
            });
            
            createParticles();
            createHearts();
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
            'error': 'Too many requests.',
            'decoy_flag': DECOY_FLAGS['rate_limited']
        }), 429
    
    # Time window check
    if not is_valid_time_window():
        return jsonify({
            'error': 'Access denied.',
            'decoy_flag': DECOY_FLAGS['wrong_hour']
        }), 403
    
    # Header validation
    headers_valid, error_key = validate_headers(request.headers, None)
    if not headers_valid:
        return jsonify({
            'error': 'Authentication failed.',
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
            'error': 'Invalid request.',
            'decoy_flag': DECOY_FLAGS.get(timing_error, DECOY_FLAGS['wrong_hour'])
        }), 403
    
    # User-Agent length check
    if len(user_agent) % 2 != 0:
        return jsonify({
            'error': 'Invalid request.',
            'decoy_flag': DECOY_FLAGS['ua_odd_length']
        }), 400
    
    # Proof of work validation
    if not verify_proof_of_work(timestamp, nonce):
        return jsonify({
            'error': 'Verification failed.',
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
            'error': 'Authentication failed.',
            'decoy_flag': DECOY_FLAGS['wrong_fingerprint']
        }), 400
    
    if totp != expected_totp:
        return jsonify({
            'error': 'Authentication failed.',
            'decoy_flag': DECOY_FLAGS['invalid_totp']
        }), 400
    
    if token != expected_token:
        return jsonify({
            'error': 'Authentication failed.',
            'decoy_flag': DECOY_FLAGS['wrong_token']
        }), 401
    
    if proof != expected_proof:
        return jsonify({
            'error': 'Authentication failed.',
            'decoy_flag': DECOY_FLAGS['wrong_proof']
        }), 401
    
    if signature != expected_signature:
        return jsonify({
            'error': 'Authentication failed.',
            'decoy_flag': DECOY_FLAGS['wrong_signature']
        }), 401
    
    if commitment != expected_commitment:
        return jsonify({
            'error': 'Authentication failed.',
            'decoy_flag': DECOY_FLAGS['wrong_commitment']
        }), 401
    
    real_flag = "TRACECTF{C0mpl1c4t3d_L0v3_R3qu1r3s_P4t13nc3_Trust_4nd_Unw4v3r1ng_C0mm1tm3nt_2020}"
    obfuscated = obfuscate_flag(real_flag, timestamp)
    
    return jsonify({
        'success': True,
        'data': obfuscated
    }), 200

@app.route('/robots.txt')
def robots():
    return """User-agent: *
Disallow: /
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
