#!/usr/bin/env python3
"""Generate SVG scenario images for tournament rounds 3 and 4."""
from pathlib import Path

IMG = Path(__file__).resolve().parents[1] / "app" / "static" / "images"
IMG.mkdir(parents=True, exist_ok=True)

IMAGES = {
    "r3_phishing_email.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
<rect width="800" height="600" fill="#f0f4f8"/>
<rect x="40" y="30" width="720" height="540" rx="8" fill="#fff" stroke="#cbd5e1" stroke-width="2"/>
<text x="60" y="70" font-family="Segoe UI,Arial" font-size="14" fill="#64748b">Hộp thư — Inbox (3 chưa đọc)</text>
<rect x="60" y="90" width="680" height="80" fill="#f8fafc" stroke="#e2e8f0"/>
<text x="80" y="120" font-family="Segoe UI,Arial" font-size="13" fill="#334155" font-weight="600">IT Security Team</text>
<text x="80" y="142" font-family="Segoe UI,Arial" font-size="12" fill="#64748b">security-noreply@it-helpdesk-support.net</text>
<text x="600" y="120" font-family="Segoe UI,Arial" font-size="11" fill="#94a3b8">Hôm nay 08:42</text>
<text x="80" y="200" font-family="Segoe UI,Arial" font-size="16" fill="#0f172a" font-weight="700">[KHẨN] Tài khoản của bạn sẽ bị khóa trong 24 giờ</text>
<text x="80" y="240" font-family="Segoe UI,Arial" font-size="14" fill="#475569">Kính gửi nhân viên,</text>
<text x="80" y="270" font-family="Segoe UI,Arial" font-size="14" fill="#475569">Hệ thống phát hiện đăng nhập bất thường. Vui lòng xác minh ngay.</text>
<rect x="130" y="390" width="260" height="44" rx="6" fill="#2563eb"/>
<text x="195" y="418" text-anchor="middle" font-family="Segoe UI,Arial" font-size="14" fill="#fff" font-weight="600">Xác minh tài khoản ngay</text>
<text x="80" y="480" font-family="Segoe UI,Arial" font-size="11" fill="#94a3b8">Liên kết: https://secure-login-verify.net/auth?id=88421</text>
</svg>""",
    "r3_brute_force.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
<rect width="800" height="600" fill="#0f172a"/>
<text x="40" y="45" font-family="Consolas,monospace" font-size="16" fill="#38bdf8">auth.log — SSH / Web Login Monitor</text>
<rect x="40" y="60" width="720" height="500" fill="#1e293b" stroke="#334155"/>
<text x="60" y="95" font-family="Consolas,monospace" font-size="12" fill="#94a3b8">2026-06-28 02:10:01 SUCCESS admin@192.168.1.5</text>
<text x="60" y="120" font-family="Consolas,monospace" font-size="12" fill="#94a3b8">2026-06-28 02:10:15 SUCCESS user01@192.168.1.12</text>
<rect x="50" y="280" width="700" height="130" fill="#450a0a" opacity="0.35"/>
<text x="60" y="305" font-family="Consolas,monospace" font-size="12" fill="#fca5a5">2026-06-28 02:11:02 FAILED root@203.0.113.44</text>
<text x="60" y="325" font-family="Consolas,monospace" font-size="12" fill="#fca5a5">2026-06-28 02:11:03 FAILED admin@203.0.113.44</text>
<text x="60" y="345" font-family="Consolas,monospace" font-size="12" fill="#fca5a5">2026-06-28 02:11:03 FAILED user@203.0.113.44</text>
<text x="60" y="365" font-family="Consolas,monospace" font-size="12" fill="#fca5a5">2026-06-28 02:11:04 FAILED test@203.0.113.44</text>
<text x="60" y="385" font-family="Consolas,monospace" font-size="12" fill="#fca5a5">... 847 FAILED attempts in 2 min — IP 203.0.113.44</text>
</svg>""",
    "r3_firewall_rule.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
<rect width="800" height="600" fill="#ecfdf5"/>
<text x="40" y="45" font-family="Segoe UI,Arial" font-size="18" fill="#065f46" font-weight="700">Firewall Policy — Production Zone</text>
<rect x="40" y="70" width="720" height="40" fill="#047857"/>
<text x="100" y="96" font-family="Segoe UI,Arial" font-size="13" fill="#fff">Action</text><text x="220" y="96" font-family="Segoe UI,Arial" font-size="13" fill="#fff">Source</text><text x="380" y="96" font-family="Segoe UI,Arial" font-size="13" fill="#fff">Destination</text><text x="560" y="96" font-family="Segoe UI,Arial" font-size="13" fill="#fff">Port</text>
<rect x="40" y="110" width="720" height="36" fill="#fff" stroke="#d1fae5"/><text x="60" y="133" font-size="12" fill="#334155">1 ALLOW</text><text x="220" y="133" font-size="12" fill="#334155">10.0.0.0/8</text><text x="380" y="133" font-size="12" fill="#334155">10.0.1.0/24</text><text x="560" y="133" font-size="12" fill="#334155">443</text>
<rect x="40" y="146" width="720" height="36" fill="#fff" stroke="#d1fae5"/><text x="60" y="169" font-size="12" fill="#334155">2 ALLOW</text><text x="220" y="169" font-size="12" fill="#334155">192.168.0.0/16</text><text x="380" y="169" font-size="12" fill="#334155">192.168.1.10</text><text x="560" y="169" font-size="12" fill="#334155">22</text>
<rect x="40" y="250" width="720" height="44" fill="#fef2f2" stroke="#fecaca" stroke-width="2"/>
<text x="60" y="278" font-size="12" fill="#b91c1c" font-weight="700">3 ALLOW</text><text x="220" y="278" font-size="12" fill="#b91c1c">0.0.0.0/0 (ANY)</text><text x="380" y="278" font-size="12" fill="#b91c1c">0.0.0.0/0 (ANY)</text><text x="560" y="278" font-size="12" fill="#b91c1c">3389 RDP</text>
</svg>""",
    "r3_traffic_graph.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
<rect width="800" height="600" fill="#f8fafc"/>
<text x="40" y="45" font-family="Segoe UI,Arial" font-size="18" fill="#1e293b" font-weight="700">Network Traffic — Last 24 Hours (Mbps)</text>
<line x1="80" y1="480" x2="740" y2="480" stroke="#cbd5e1" stroke-width="2"/>
<line x1="80" y1="80" x2="80" y2="480" stroke="#cbd5e1" stroke-width="2"/>
<polyline points="100,420 180,400 260,410 340,395 420,405 500,390 540,380 580,175 620,420 700,400" fill="none" stroke="#3b82f6" stroke-width="3"/>
<circle cx="585" cy="175" r="8" fill="#ef4444" opacity="0.9"/>
<text x="80" y="520" font-size="11" fill="#64748b">00:00</text><text x="560" y="520" font-size="11" fill="#64748b">02:14</text>
</svg>""",
    "r3_network_topology.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
<rect width="800" height="600" fill="#f1f5f9"/>
<text x="40" y="40" font-family="Segoe UI,Arial" font-size="18" fill="#0f172a" font-weight="700">Internal Network Topology</text>
<rect x="340" y="80" width="120" height="50" rx="6" fill="#3b82f6"/><text x="400" y="112" text-anchor="middle" fill="#fff" font-size="12">Core Switch</text>
<rect x="120" y="200" width="100" height="44" rx="4" fill="#10b981"/><text x="170" y="227" text-anchor="middle" fill="#fff" font-size="11">Server-01</text>
<rect x="560" y="200" width="100" height="44" rx="4" fill="#10b981"/><text x="610" y="227" text-anchor="middle" fill="#fff" font-size="11">Firewall</text>
<line x1="400" y1="130" x2="170" y2="200" stroke="#64748b" stroke-width="2"/>
<line x1="400" y1="130" x2="610" y2="200" stroke="#64748b" stroke-width="2"/>
<rect x="580" y="290" width="110" height="44" rx="4" fill="#f59e0b" stroke="#dc2626" stroke-width="2" stroke-dasharray="6,3"/>
<text x="635" y="318" text-anchor="middle" fill="#fff" font-size="11">HR-PC-07</text>
<line x1="635" y1="334" x2="720" y2="400" stroke="#ef4444" stroke-width="2" stroke-dasharray="4,4"/>
<rect x="680" y="400" width="90" height="40" rx="4" fill="#64748b"/><text x="725" y="425" text-anchor="middle" fill="#fff" font-size="10">Internet</text>
</svg>""",
    "r3_fake_login.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
<rect width="800" height="600" fill="#e2e8f0"/>
<rect x="200" y="60" width="400" height="480" rx="10" fill="#fff" stroke="#cbd5e1" stroke-width="2"/>
<rect x="200" y="60" width="400" height="36" fill="#f1f5f9" stroke="#cbd5e1"/>
<text x="220" y="84" font-family="Segoe UI,Arial" font-size="13" fill="#64748b">http://</text>
<text x="280" y="84" font-family="Segoe UI,Arial" font-size="13" fill="#dc2626">secvire-bank-login.com</text>
<text x="400" y="84" font-family="Segoe UI,Arial" font-size="13" fill="#64748b">/signin</text>
<circle cx="400" cy="160" r="30" fill="#1d4ed8"/><text x="400" y="168" text-anchor="middle" fill="#fff" font-size="20" font-weight="700">B</text>
<text x="400" y="220" text-anchor="middle" font-family="Segoe UI,Arial" font-size="20" fill="#0f172a" font-weight="700">Đăng nhập Internet Banking</text>
<rect x="260" y="260" width="280" height="40" rx="4" fill="#f8fafc" stroke="#cbd5e1"/>
<rect x="260" y="320" width="280" height="40" rx="4" fill="#f8fafc" stroke="#cbd5e1"/>
<rect x="260" y="390" width="280" height="44" rx="6" fill="#1d4ed8"/><text x="400" y="418" text-anchor="middle" fill="#fff" font-size="14">Đăng nhập</text>
</svg>""",
    "r4_soc_warroom.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
<rect width="800" height="600" fill="#0b1120"/>
<text x="24" y="32" font-family="Segoe UI,Arial" font-size="16" fill="#38bdf8" font-weight="700">SOC WAR ROOM — LIVE INCIDENT DASHBOARD</text>
<rect x="20" y="50" width="360" height="200" rx="6" fill="#1e293b" stroke="#334155"/>
<text x="36" y="78" font-size="12" fill="#fbbf24" font-weight="600">Email Gateway Alerts</text>
<rect x="36" y="95" width="320" height="55" rx="4" fill="#451a03" stroke="#f97316"/>
<text x="50" y="118" font-size="11" fill="#fdba74">847 phishing emails blocked</text>
<text x="50" y="136" font-size="10" fill="#fb923c">Subject: [IT] Reset VPN password immediately</text>
<rect x="400" y="50" width="380" height="200" rx="6" fill="#1e293b" stroke="#334155"/>
<text x="416" y="78" font-size="12" fill="#f87171" font-weight="600">Brute Force Monitor</text>
<rect x="430" y="100" width="40" height="120" fill="#7f1d1d"/><rect x="480" y="130" width="40" height="90" fill="#991b1b"/><rect x="530" y="110" width="40" height="110" fill="#b91c1c"/><rect x="580" y="90" width="40" height="130" fill="#dc2626"/><rect x="630" y="85" width="40" height="135" fill="#ef4444"/>
<text x="416" y="190" font-size="10" fill="#fca5a5">2,340 failed logins / 10 min</text>
<rect x="20" y="270" width="360" height="200" rx="6" fill="#1e293b" stroke="#334155"/>
<text x="36" y="298" font-size="12" fill="#34d399" font-weight="600">Outbound Traffic (Exfil Watch)</text>
<polyline points="40,420 100,410 160,405 220,400 280,395 340,180 380,430" fill="none" stroke="#22d3ee" stroke-width="2"/>
<circle cx="340" cy="180" r="6" fill="#ef4444"/>
<rect x="400" y="270" width="380" height="200" rx="6" fill="#1e293b" stroke="#334155"/>
<text x="416" y="298" font-size="12" fill="#a78bfa" font-weight="600">Network Map + Firewall</text>
<circle cx="580" cy="420" r="22" fill="#dc2626" stroke="#fca5a5" stroke-width="2"/>
<text x="580" y="425" text-anchor="middle" fill="#fff" font-size="8">DB-PROD</text>
<rect x="650" y="310" width="110" height="30" rx="3" fill="#450a0a" stroke="#ef4444"/>
<text x="660" y="330" font-size="9" fill="#fca5a5">+ ALLOW :4444 ANY</text>
</svg>""",
}

for name, content in IMAGES.items():
    (IMG / name).write_text(content, encoding="utf-8")
    print("Wrote", name)
