"""
Ultra-Optimized High-End 3D Cinematic Cyber Defense Hero Video Generator
Branding: บริษัท GoHard (GoHard Cyber Defense)
Performance: Precomputed gradients & vignettes, 30+ FPS render speed.
Quality: True 3D perspective projection, no harsh side cuts, edge-to-edge organic visuals.
"""

import math
import subprocess
import numpy as np
import cv2

WIDTH, HEIGHT = 1920, 1080
BLOOM_W, BLOOM_H = 480, 270
FPS = 60
DURATION = 6.0
TOTAL_FRAMES = int(FPS * DURATION) # 360 frames

RAW_OUTPUT = r"d:\Mini project ML\review\raw.mp4"

# 3D Math Helper Functions
def rotate_x(x, y, z, angle):
    c, s = math.cos(angle), math.sin(angle)
    return x, y * c - z * s, y * s + z * c

def rotate_y(x, y, z, angle):
    c, s = math.cos(angle), math.sin(angle)
    return x * c + z * s, y, -x * s + z * c

def rotate_z(x, y, z, angle):
    c, s = math.cos(angle), math.sin(angle)
    return x * c - y * s, x * s + y * c, z

def project_3d(x, y, z, fov=880.0, cx=960.0, cy=540.0):
    depth = z + 1050.0
    if depth < 1.0:
        depth = 1.0
    scale = fov / depth
    px = int(cx + x * scale)
    py = int(cy + y * scale)
    return px, py, scale

# 1. Precompute Edge-to-Edge Base Canvas (Deep Midnight Cyber Gradient)
y_coords = np.linspace(0, 1, HEIGHT, dtype=np.float32).reshape(HEIGHT, 1)
base_b = (18 + 26 * y_coords).astype(np.uint8)
base_g = (10 + 14 * y_coords).astype(np.uint8)
base_r = (6 + 8 * y_coords).astype(np.uint8)
PRECOMPUTED_BASE = np.dstack([
    np.broadcast_to(base_b, (HEIGHT, WIDTH)),
    np.broadcast_to(base_g, (HEIGHT, WIDTH)),
    np.broadcast_to(base_r, (HEIGHT, WIDTH))
])

# 2. Precompute Smooth Vignette Map (Soft radial gradient, NO vertical lines!)
center_x, center_y = WIDTH // 2, HEIGHT // 2
vignette_map = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
cv2.circle(vignette_map, (center_x, center_y), int(WIDTH * 0.72), 1.0, -1)
vignette_map = cv2.GaussianBlur(vignette_map, (201, 201), 0)
VIGNETTE_MULT = (0.72 + 0.28 * vignette_map)[:, :, np.newaxis]

# 3. 3D Icosahedron Geodesic Shield Vertices
PHI = (1.0 + math.sqrt(5.0)) / 2.0
ico_verts_raw = [
    (-1,  PHI, 0), ( 1,  PHI, 0), (-1, -PHI, 0), ( 1, -PHI, 0),
    (0, -1,  PHI), (0,  1,  PHI), (0, -1, -PHI), (0,  1, -PHI),
    ( PHI, 0, -1), ( PHI, 0,  1), (-PHI, 0, -1), (-PHI, 0,  1)
]
ico_verts = []
for vx, vy, vz in ico_verts_raw:
    l = math.sqrt(vx*vx + vy*vy + vz*vz)
    ico_verts.append((vx/l * 185.0, vy/l * 185.0, vz/l * 185.0))

ico_edges = []
for i in range(len(ico_verts)):
    for j in range(i + 1, len(ico_verts)):
        dist = math.sqrt(sum((ico_verts[i][k] - ico_verts[j][k])**2 for k in range(3)))
        if dist < 215.0:
            ico_edges.append((i, j))

# 4. Particles and Stars
np.random.seed(2026)
N_STREAKS = 80
streak_phi = np.random.uniform(-math.pi/2.2, math.pi/2.2, N_STREAKS)
streak_theta = np.random.uniform(0, math.tau, N_STREAKS)
streak_radii = np.random.uniform(900, 1600, N_STREAKS)
streak_speeds = np.random.uniform(320, 560, N_STREAKS)

star_xs = np.random.uniform(0, WIDTH, 280)
star_ys = np.random.uniform(0, HEIGHT, 280)
star_twinkle = np.random.uniform(0, math.tau, 280)

N_SPARKS = 90
spark_angles = np.random.uniform(0, math.tau, N_SPARKS)
spark_v = np.random.uniform(120, 340, N_SPARKS)

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
    "-preset", "veryfast",
    "-pix_fmt", "yuv420p",
    RAW_OUTPUT
]

proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
print(f"Rendering {TOTAL_FRAMES} frames of 3D GoHard Cyber Defense Shield...")

for f in range(TOTAL_FRAMES):
    t = f / FPS
    norm_t = t / DURATION
    
    # 1. Base Canvas
    frame = PRECOMPUTED_BASE.copy()
    
    # Lightweight low-res bloom buffer (480x270)
    bloom_buf = np.zeros((BLOOM_H, BLOOM_W, 3), dtype=np.uint8)
    bx_scale, by_scale = BLOOM_W / WIDTH, BLOOM_H / HEIGHT

    # 2. Stars
    for si in range(280):
        sx, sy = int(star_xs[si]), int(star_ys[si])
        alpha = 0.4 + 0.5 * math.sin(star_twinkle[si] + t * 3.0)
        col = (int(160 * alpha), int(120 * alpha), int(90 * alpha))
        cv2.circle(frame, (sx, sy), 1, col, -1)

    # 3. 3D Perspective Cyber Grid Floor with Fog
    horizon_y = int(HEIGHT * 0.53)
    grid_speed = (t * 70.0) % 40.0
    for gy in range(horizon_y + 12, HEIGHT, 26):
        dist_factor = (gy - horizon_y) / (HEIGHT - horizon_y)
        fog_alpha = min(1.0, dist_factor ** 1.5)
        line_col = (int(65 * fog_alpha), int(42 * fog_alpha), int(18 * fog_alpha))
        cv2.line(frame, (0, gy), (WIDTH, gy), line_col, 1)

    for gx in range(-WIDTH // 2, WIDTH + WIDTH // 2, 130):
        cv2.line(frame, (center_x, horizon_y), (gx, HEIGHT), (42, 24, 12), 1, cv2.LINE_AA)

    # 4. Inward Threat Waves (Red Attack Vectors)
    threat_power = max(0.0, 1.0 - (t / 3.8) ** 1.8)
    if threat_power > 0.02:
        for i in range(N_STREAKS):
            cur_r = (streak_radii[i] - streak_speeds[i] * t) % 1150.0 + 170.0
            p_phi = streak_phi[i]
            p_th = streak_theta[i] + t * 0.35
            
            tx = cur_r * math.cos(p_phi) * math.cos(p_th)
            ty = cur_r * math.sin(p_phi) * 0.55
            tz = cur_r * math.cos(p_phi) * math.sin(p_th)
            
            tail_r = cur_r + 48.0
            tail_th = p_th - 0.06
            tail_x = tail_r * math.cos(p_phi) * math.cos(tail_th)
            tail_y = tail_r * math.sin(p_phi) * 0.55
            tail_z = tail_r * math.cos(p_phi) * math.sin(tail_th)
            
            px, py, sc = project_3d(tx, ty, tz, cx=center_x, cy=center_y)
            tx_tail, ty_tail, _ = project_3d(tail_x, tail_y, tail_z, cx=center_x, cy=center_y)
            
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                intensity = threat_power * min(1.0, sc * 1.4)
                col_head = (int(35 * intensity), int(75 * intensity), int(255 * intensity))
                cv2.line(frame, (px, py), (tx_tail, ty_tail), col_head, 2, cv2.LINE_AA)
                cv2.circle(frame, (px, py), max(2, int(4 * sc)), (120, 180, 255), -1, cv2.LINE_AA)
                # Draw on low-res bloom
                b_px, b_py = int(px * bx_scale), int(py * by_scale)
                if 0 <= b_px < BLOOM_W and 0 <= b_py < BLOOM_H:
                    cv2.circle(bloom_buf, (b_px, b_py), 3, (10, 40, 160), -1)

    # 5. Holographic 3D Geodesic Shield (GoHard Quantum Shield)
    rot_y = t * 0.42
    rot_x = math.sin(t * 0.3) * 0.32
    rot_z = t * 0.12
    
    shield_deploy = min(1.0, t / 1.5)
    shield_scale = shield_deploy * (1.0 + 0.03 * math.sin(t * 4.0))

    proj_verts = []
    for vx, vy, vz in ico_verts:
        sx, sy, sz = vx * shield_scale, vy * shield_scale, vz * shield_scale
        rx, ry, rz = rotate_x(sx, sy, sz, rot_x)
        rx, ry, rz = rotate_y(rx, ry, rz, rot_y)
        rx, ry, rz = rotate_z(rx, ry, rz, rot_z)
        px, py, sc = project_3d(rx, ry, rz, cx=center_x, cy=center_y)
        proj_verts.append((px, py, rz, sc))

    if shield_deploy > 0.05:
        shield_glow = min(1.0, t / 2.0)
        c_b = int(120 * shield_glow)
        c_g = int(240 * shield_glow)
        c_r = int(10 * shield_glow)
        
        for i1, i2 in ico_edges:
            p1 = proj_verts[i1]
            p2 = proj_verts[i2]
            avg_z = (p1[2] + p2[2]) / 2.0
            edge_alpha = max(0.18, min(1.0, (avg_z + 400.0) / 700.0))
            col = (int(c_b * edge_alpha), int(c_g * edge_alpha), int(c_r * edge_alpha))
            cv2.line(frame, (p1[0], p1[1]), (p2[0], p2[1]), col, 2 if avg_z > 0 else 1, cv2.LINE_AA)
            
        for px, py, rz, sc in proj_verts:
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                node_alpha = max(0.3, min(1.0, (rz + 300.0) / 600.0))
                cv2.circle(frame, (px, py), max(3, int(5 * sc)), (int(190 * node_alpha), int(255 * node_alpha), int(90 * node_alpha)), -1, cv2.LINE_AA)
                b_px, b_py = int(px * bx_scale), int(py * by_scale)
                if 0 <= b_px < BLOOM_W and 0 <= b_py < BLOOM_H:
                    cv2.circle(bloom_buf, (b_px, b_py), 4, (40, 110, 20), -1)

    # 6. Nested 3D Holographic Gimbal Rings
    for r_radius, r_axis, r_speed, r_col in [
        (230.0, 'xy', 0.55, (140, 230, 20)),
        (280.0, 'yz', -0.38, (180, 210, 0)),
        (330.0, 'xz', 0.28, (160, 240, 40))
    ]:
        ring_pts = []
        n_pts = 42
        r_rot = t * r_speed
        for p_i in range(n_pts):
            p_ang = p_i * (math.tau / n_pts)
            rx = r_radius * math.cos(p_ang)
            ry = r_radius * math.sin(p_ang)
            rz = 0.0
            if r_axis == 'yz':
                rx, rz = rz, rx
            elif r_axis == 'xz':
                ry, rz = rz, ry
            rx, ry, rz = rotate_x(rx, ry, rz, rot_x + r_rot * 0.2)
            rx, ry, rz = rotate_y(rx, ry, rz, rot_y + r_rot)
            px, py, sc = project_3d(rx, ry, rz, cx=center_x, cy=center_y)
            ring_pts.append((px, py, rz))
            
        for p_i in range(n_pts):
            if (p_i + int(t * 12)) % 4 != 0:
                p1 = ring_pts[p_i]
                p2 = ring_pts[(p_i + 1) % n_pts]
                if p1[2] > -220:
                    cv2.line(frame, (p1[0], p1[1]), (p2[0], p2[1]), r_col, 1, cv2.LINE_AA)

    # 7. Deflection Sparks & Impact Ripples
    if 1.0 < t < 4.8:
        wave_t = (t - 1.0) / 3.8
        spark_act = math.sin(wave_t * math.pi)
        for sp in range(N_SPARKS):
            sp_dist = 180.0 + (spark_v[sp] * (t - 1.0)) % 290.0
            sp_ang = spark_angles[sp] + t * 0.5
            sp_x = center_x + int(sp_dist * math.cos(sp_ang))
            sp_y = center_y + int(sp_dist * math.sin(sp_ang) * 0.6)
            if 0 <= sp_x < WIDTH and 0 <= sp_y < HEIGHT:
                sp_col = (int(170 * spark_act), int(240 * spark_act), int(70 * spark_act))
                cv2.circle(frame, (sp_x, sp_y), 2, sp_col, -1, cv2.LINE_AA)

    # 8. Central Quantum Singularity / Core Node (GoHard Core)
    core_breathe = 1.0 + 0.05 * math.sin(t * 3.5)
    core_r = int(60 * core_breathe)
    
    cv2.circle(frame, (center_x, center_y), core_r + 28, (80, 180, 20), 2, cv2.LINE_AA)
    cv2.circle(frame, (center_x, center_y), core_r + 14, (120, 230, 40), 2, cv2.LINE_AA)
    cv2.circle(frame, (center_x, center_y), core_r, (160, 255, 60), -1, cv2.LINE_AA)
    cv2.circle(frame, (center_x, center_y), int(core_r * 0.68), (24, 18, 10), -1, cv2.LINE_AA)
    cv2.circle(frame, (center_x, center_y), int(core_r * 0.38), (106, 255, 0), -1, cv2.LINE_AA)
    cv2.circle(frame, (center_x, center_y), int(core_r * 0.16), (255, 255, 240), -1, cv2.LINE_AA)
    
    # Bloom for central core
    b_cx, b_cy = int(center_x * bx_scale), int(center_y * by_scale)
    cv2.circle(bloom_buf, (b_cx, b_cy), int(core_r * bx_scale * 1.8), (70, 160, 30), -1)

    # 9. Fast Optical Bloom Blur
    bloom_blur = cv2.GaussianBlur(bloom_buf, (31, 31), 0)
    bloom_up = cv2.resize(bloom_blur, (WIDTH, HEIGHT))
    frame = cv2.add(frame, bloom_up)

    # 10. Organic Precomputed Radial Vignette (Edge-to-edge smooth falloff)
    frame = (frame.astype(np.float32) * VIGNETTE_MULT).astype(np.uint8)

    # Send to ffmpeg
    proc.stdin.write(frame.tobytes())

proc.stdin.close()
proc.wait()
print("GoHard 3D Shield Video Render complete:", RAW_OUTPUT)
