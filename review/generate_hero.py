"""
Render the 6-second 60fps 1080p hero animation for 'The Quantum Shield'
Pipes raw frames directly into ffmpeg for ultra-fast generation.
"""

import sys
import math
import subprocess
import numpy as np
import cv2

WIDTH, HEIGHT = 1920, 1080
FPS = 60
DURATION = 6.0
TOTAL_FRAMES = int(FPS * DURATION) # 360 frames

RAW_OUTPUT = r"d:\Mini project ML\review\raw.mp4"

# Start ffmpeg subprocess to receive raw BGR24 frames
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "bgr24",
    "-r", str(FPS),
    "-i", "-",
    "-c:v", "libx264",
    "-crf", "16",
    "-preset", "medium",
    "-pix_fmt", "yuv420p",
    RAW_OUTPUT
]

proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

print(f"Rendering {TOTAL_FRAMES} frames at {WIDTH}x{HEIGHT}...")

# Pre-generate stars / background particles
np.random.seed(42)
N_STARS = 120
star_x = np.random.uniform(0, WIDTH, N_STARS)
star_y = np.random.uniform(0, HEIGHT, N_STARS)
star_z = np.random.uniform(0.2, 1.0, N_STARS)
star_phase = np.random.uniform(0, math.tau, N_STARS)

# Threat packet particles
N_THREATS = 70
threat_angles = np.random.uniform(0, math.tau, N_THREATS)
threat_speeds = np.random.uniform(250, 450, N_THREATS)
threat_dists = np.random.uniform(700, 1200, N_THREATS)

# Spark particles
N_SPARKS = 80
spark_angles = np.random.uniform(0, math.tau, N_SPARKS)
spark_speeds = np.random.uniform(60, 200, N_SPARKS)

center_x, center_y = WIDTH // 2, HEIGHT // 2

for f in range(TOTAL_FRAMES):
    t = f / FPS # current time in seconds (0.0 to 6.0)
    norm_t = t / DURATION # 0.0 to 1.0
    
    # 1. Canvas base: Deep dark cyber navy (#0A0F1D)
    frame = np.full((HEIGHT, WIDTH, 3), (29, 15, 10), dtype=np.uint8) # BGR
    
    # 2. Subtle radial glow in center
    # Settle glow intensifies toward green at the end
    glow_intensity = 0.3 + 0.5 * (1.0 - math.exp(-norm_t * 3))
    glow_radius = int(300 + 50 * math.sin(t * 3))
    cv2.circle(frame, (center_x, center_y), glow_radius, (60, 45, 15), -1, cv2.LINE_AA)
    cv2.circle(frame, (center_x, center_y), int(glow_radius * 0.6), (90, 70, 20), -1, cv2.LINE_AA)
    
    # 3. 3D Perspective Cyber Grid Lines (moving toward viewer)
    grid_offset = (t * 120) % 60
    for gy in range(int(HEIGHT * 0.55), HEIGHT, 45):
        y_pos = int(gy + grid_offset * (gy / HEIGHT))
        if y_pos < HEIGHT:
            alpha = (y_pos - HEIGHT * 0.55) / (HEIGHT * 0.45)
            color_val = int(45 * alpha)
            cv2.line(frame, (0, y_pos), (WIDTH, y_pos), (color_val + 20, color_val + 10, color_val), 1)
            
    # Grid vertical perspective rays
    for gx in range(0, WIDTH + 1, 160):
        cv2.line(frame, (center_x, int(HEIGHT * 0.55)), (gx, HEIGHT), (40, 25, 15), 1, cv2.LINE_AA)
        
    # 4. Background Starfield / Data Dust
    for i in range(N_STARS):
        sx = int((star_x[i] - (star_z[i] * t * 20)) % WIDTH)
        sy = int((star_y[i] + (star_z[i] * t * 15)) % HEIGHT)
        brightness = int(120 + 80 * math.sin(star_phase[i] + t * 4))
        b = min(255, int(brightness * 1.2))
        g = min(255, int(brightness * 0.9))
        r = min(255, int(brightness * 0.6))
        cv2.circle(frame, (sx, sy), 1 if star_z[i] < 0.6 else 2, (b, g, r), -1)

    # 5. Red Threat Waves (Seconds 0.0 to 3.5)
    threat_life = max(0.0, 1.0 - (t / 3.8))
    if threat_life > 0.05:
        for i in range(N_THREATS):
            # Moves inward toward center
            cur_dist = (threat_dists[i] - threat_speeds[i] * t) % 900 + 120
            ang = threat_angles[i] + t * 0.15
            tx = int(center_x + cur_dist * math.cos(ang))
            ty = int(center_y + cur_dist * math.sin(ang))
            
            # Tail of the packet
            tail_x = int(center_x + (cur_dist + 25) * math.cos(ang))
            tail_y = int(center_y + (cur_dist + 25) * math.sin(ang))
            
            color_threat = (int(30 * threat_life), int(60 * threat_life), int(245 * threat_life)) # BGR Red
            cv2.line(frame, (tx, ty), (tail_x, tail_y), color_threat, 2, cv2.LINE_AA)
            cv2.circle(frame, (tx, ty), 3, (60, 90, 255), -1, cv2.LINE_AA)

    # 6. Quantum Hexagonal Shield (#00D26A Emerald / Cyan)
    # Shield expands and solidifies as time progresses
    shield_phase = min(1.0, t / 1.8) # 0 to 1 in 1.8s
    base_radius = 160 + 20 * math.sin(t * 2.5)
    
    # Draw concentric hexagonal layers
    for layer, scale, speed, alpha in [(1, 1.0, 0.4, 1.0), (2, 1.25, -0.3, 0.6), (3, 1.5, 0.2, 0.35)]:
        if shield_phase < 0.2 and layer > 1:
            continue
        rad = base_radius * scale * shield_phase
        rot = t * speed
        hex_pts = []
        for v in range(6):
            pt_ang = rot + v * (math.tau / 6)
            px = int(center_x + rad * math.cos(pt_ang))
            py = int(center_y + rad * math.sin(pt_ang))
            hex_pts.append((px, py))
            
        pts_arr = np.array(hex_pts, np.int32)
        # Shield Color: Emerald Green (BGR: 106, 210, 0)
        c_b = int(106 * alpha)
        c_g = int(210 * alpha)
        c_r = int(0 * alpha)
        cv2.polylines(frame, [pts_arr], True, (c_b, c_g, c_r), 2 if layer == 1 else 1, cv2.LINE_AA)
        
        # Vertex glowing nodes
        for px, py in hex_pts:
            cv2.circle(frame, (px, py), 4 if layer == 1 else 2, (180, 255, 100), -1, cv2.LINE_AA)
            
    # Shield Energy Field Rings
    pulse_rad = int((base_radius * 0.9 + (t * 80) % 90) * shield_phase)
    cv2.circle(frame, (center_x, center_y), pulse_rad, (120, 210, 0), 1, cv2.LINE_AA)
    
    # 7. Impact Sparks & Dissolution (Peak around t = 1.5 to 4.0)
    if 0.8 < t < 4.8:
        spark_alpha = math.sin((t - 0.8) / 4.0 * math.pi)
        for i in range(N_SPARKS):
            s_dist = 180 + (spark_speeds[i] * (t - 0.8)) % 220
            s_ang = spark_angles[i] + t * 0.8
            spx = int(center_x + s_dist * math.cos(s_ang))
            spy = int(center_y + s_dist * math.sin(s_ang))
            s_col = (int(200 * spark_alpha), int(230 * spark_alpha), int(100 * spark_alpha))
            cv2.circle(frame, (spx, spy), 2, s_col, -1, cv2.LINE_AA)

    # 8. Central Core Server Node (Arrival & Rest State)
    # Becomes prominent, stable, and peaceful in the final 2.5 seconds
    core_rad = 54 + int(4 * math.sin(t * 3))
    # Glowing halo around core
    cv2.circle(frame, (center_x, center_y), core_rad + 18, (80, 160, 20), -1, cv2.LINE_AA)
    cv2.circle(frame, (center_x, center_y), core_rad + 6, (130, 230, 40), -1, cv2.LINE_AA)
    cv2.circle(frame, (center_x, center_y), core_rad, (180, 255, 100), -1, cv2.LINE_AA)
    # Inner dark iris
    cv2.circle(frame, (center_x, center_y), int(core_rad * 0.65), (30, 25, 15), -1, cv2.LINE_AA)
    # Inner jewel
    cv2.circle(frame, (center_x, center_y), int(core_rad * 0.25), (106, 210, 0), -1, cv2.LINE_AA)
    
    # 9. Clean vignette (darker edges for text negative space left & right)
    # Keeps center bright, left and right calm for typography per Law 7
    vignette = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    cv2.circle(vignette, (center_x, center_y), int(WIDTH * 0.6), 1.0, -1)
    vignette = cv2.GaussianBlur(vignette, (201, 201), 0)
    # Darken left 25% and right 25% intentionally for typography
    for c in range(3):
        frame[:, :420, c] = (frame[:, :420, c] * 0.55).astype(np.uint8)
        frame[:, WIDTH-420:, c] = (frame[:, WIDTH-420:, c] * 0.55).astype(np.uint8)

    # Write frame to ffmpeg
    proc.stdin.write(frame.tobytes())

proc.stdin.close()
proc.wait()
print("Raw render complete:", RAW_OUTPUT)
