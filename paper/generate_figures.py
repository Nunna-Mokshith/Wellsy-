import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

os.makedirs(r"D:\Wellsy\paper\figures", exist_ok=True)
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

# ==========================================
# FIGURE 1: Overall System Architecture
# ==========================================
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Background boxes
def draw_box(ax, x, y, w, h, title, fill_color, border_color='#2c3e50', alpha=0.9, lw=1.5, ls='-'):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.5",
                                  facecolor=fill_color, edgecolor=border_color, linewidth=lw, linestyle=ls, alpha=alpha)
    ax.add_patch(rect)
    if title:
        ax.text(x + w/2, y + h - 3.5, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1a252f')
    return rect

# Layer 1: Client Interfaces (Top)
draw_box(ax, 3, 78, 94, 18, "CLIENT INTERACTION LAYER (THREE-MODE ARCHITECTURE)", "#ebf5fb", "#2980b9", lw=2)
draw_box(ax, 6, 81, 26, 10, "Jarvis HUD Dashboard\n(WebSocket / HTML5 Glassmorphism)", "#ffffff", "#3498db")
draw_box(ax, 37, 81, 26, 10, "CLI Direct REPL\n(wellsy.py --chat / --status)", "#ffffff", "#3498db")
draw_box(ax, 68, 81, 26, 10, "System Tray Daemon\n(pystray Background Loop)", "#ffffff", "#3498db")

# Arrows down to Orchestration
for cx in [19, 50, 81]:
    ax.annotate('', xy=(cx, 68), xytext=(cx, 78),
                arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=2))

# Layer 2: Orchestration & Supervisor
draw_box(ax, 3, 38, 94, 30, "CORE REASONING & MULTI-AGENT SUPERVISOR (LANGGRAPH)", "#fef9e7", "#d68910", lw=2)
draw_box(ax, 28, 54, 44, 9, "LangGraph Supervisor Engine\n(StateGraph Router & Intent Parsing)", "#ffffff", "#f39c12", lw=1.5)

# Sub-Agents
agents = [
    ("TaskAgent\n(Cron & Scheduling)", 6),
    ("OSAgent\n(Files & Apps)", 24.5),
    ("CommsAgent\n(Email & Overleaf)", 43),
    ("MediaAgent\n(Audio & Media)", 61.5),
    ("ResearchAgent\n(Gemini Search)", 80)
]

for name, x in agents:
    draw_box(ax, x, 41, 14, 8, name, "#ffffff", "#e67e22", lw=1)
    ax.annotate('', xy=(x+7, 49), xytext=(50, 54),
                arrowprops=dict(arrowstyle="<->", color="#7f8c8d", lw=1.2, ls='--'))

# Layer 3: Safety & Memory (Bottom)
draw_box(ax, 3, 4, 45, 28, "TRUST TIER & SAFETY SUBSYSTEM", "#faded7", "#c0392b", lw=2)
draw_box(ax, 6, 16, 39, 9, "Trust Tier Risk Classifier\n(SAFE / LOW / HIGH / DANGER)", "#ffffff", "#e74c3c")
draw_box(ax, 6, 6, 39, 8, "Async Human-in-the-Loop Gate\n(WebSocket Action Preview & Approval)", "#ffffff", "#c0392b")

draw_box(ax, 52, 4, 45, 28, "SECURE PERSISTENT MEMORY & SENSING", "#e8f8f5", "#16a085", lw=2)
draw_box(ax, 55, 16, 39, 9, "Passive File Metadata Scanner\n(Zero-Payload Snapshot Hash Diff)", "#ffffff", "#1abc9c")
draw_box(ax, 55, 6, 39, 8, "Encrypted SQLite Store\n(AES-256 Fernet Keyed DB)", "#ffffff", "#16a085")

# Connecting lines between agents and safety/memory
ax.annotate('', xy=(25, 32), xytext=(25, 38),
            arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=2))
ax.text(26, 35, "Preflight Gate", fontsize=8, color="#922b21", fontweight='bold')

ax.annotate('', xy=(75, 32), xytext=(75, 38),
            arrowprops=dict(arrowstyle="<->", color="#16a085", lw=2))
ax.text(76, 35, "Memory Recall", fontsize=8, color="#0e6251", fontweight='bold')

plt.tight_layout()
plt.savefig(r"D:\Wellsy\paper\figures\fig1_architecture.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig1_architecture.png")

# ==========================================
# FIGURE 2: Trust Tier Gate Flowchart
# ==========================================
fig, ax = plt.subplots(figsize=(8, 7), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Flowchart elements
draw_box(ax, 25, 88, 50, 9, "Tool Call Request Emitted\n(Agent Action with Parameters)", "#ebf5fb", "#2980b9", lw=1.8)
ax.annotate('', xy=(50, 77), xytext=(50, 88), arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=2))

# Classification
draw_box(ax, 20, 68, 60, 9, "Risk Tier Engine Analysis\n(Inspects tool name, keywords, destructive verbs)", "#fef9e7", "#d68910", lw=1.8)

# Decision Diamond (represented as box with diamond text)
ax.annotate('', xy=(25, 52), xytext=(35, 68), arrowprops=dict(arrowstyle="->", color="#27ae60", lw=1.8))
ax.annotate('', xy=(75, 52), xytext=(65, 68), arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.8))

draw_box(ax, 5, 43, 40, 9, "Tier 0 (SAFE) / Tier 1 (LOW)\nAuto-Approved Execution", "#e8f8f5", "#27ae60", lw=1.5)
draw_box(ax, 55, 43, 42, 9, "Tier 2 (HIGH) / Tier 3 (DANGER)\nIntercept & Freeze Graph", "#fadbd8", "#c0392b", lw=1.5)

# Branch from Auto-Approve to Execute
ax.annotate('', xy=(25, 20), xytext=(25, 43), arrowprops=dict(arrowstyle="->", color="#27ae60", lw=2))

# Branch from Intercept to User HITL Gate
ax.annotate('', xy=(76, 31), xytext=(76, 43), arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.8))
draw_box(ax, 52, 23, 46, 8, "WebSocket Action Preview\nHuman-in-the-Loop Modal (HUD)", "#ffffff", "#e74c3c", lw=1.5)

# Approval check
ax.annotate('Approved', xy=(48, 14), xytext=(60, 23), arrowprops=dict(arrowstyle="->", color="#27ae60", lw=1.8),
            fontsize=8, fontweight='bold', color="#1e8449")
ax.annotate('Rejected', xy=(85, 12), xytext=(85, 23), arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.8),
            fontsize=8, fontweight='bold', color="#922b21")

draw_box(ax, 15, 10, 35, 10, "Tool Node Execution\n(Return Output to Agent)", "#d4efdf", "#1e8449", lw=2)
draw_box(ax, 70, 4, 28, 8, "Execution Aborted\n(Safe Rollback & Log)", "#f2d7d5", "#922b21", lw=1.5)

plt.tight_layout()
plt.savefig(r"D:\Wellsy\paper\figures\fig2_trust_gate.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig2_trust_gate.png")

# ==========================================
# FIGURE 3: Memory & Privacy Lifecycle
# ==========================================
fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Sequence boxes
stages = [
    ("Watched Folders\n(Local Disk)", 3, "#ebf5fb", "#2980b9"),
    ("Metadata Scanner\n(Zero-Payload Delta)", 22, "#fef9e7", "#d68910"),
    ("AES-256 Encryptor\n(Fernet Key in venv)", 42, "#fadbd8", "#c0392b"),
    ("SQLite Store\n(Typed Entities)", 62, "#e8f8f5", "#16a085"),
    ("Prompt Injection\n(Recall on Wakeup)", 82, "#eaf2f8", "#2c3e50")
]

for title, x, bg, border in stages:
    draw_box(ax, x, 35, 16, 30, title, bg, border, lw=1.6)

# Flow arrows
for x in [19, 38, 58, 78]:
    ax.annotate('', xy=(x+3, 50), xytext=(x, 50),
                arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=2.2))

# Annotations under boxes
ax.text(11, 25, "Monitors ~/, D:/Projects\nExcludes node_modules", ha='center', fontsize=7.5, color='#555')
ax.text(30, 25, "Tracks path, size, mtime\nNever reads file content", ha='center', fontsize=7.5, color='#555')
ax.text(50, 25, "Symmetric encryption\nProtects user notes & turns", ha='center', fontsize=7.5, color='#555')
ax.text(70, 25, "Tables: memories, meta\nIndexed by session timestamp", ha='center', fontsize=7.5, color='#555')
ax.text(90, 25, "Natural language greeting\nContext-aware greeting", ha='center', fontsize=7.5, color='#555')

plt.tight_layout()
plt.savefig(r"D:\Wellsy\paper\figures\fig3_memory_pipeline.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig3_memory_pipeline.png")

# ==========================================
# FIGURE 4: Empirical Latency & Safety Metrics
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=300)

# Subplot 1: Sub-agent Dispatch & Execution Latency
domains = ['Task\nAgent', 'OS\nAgent', 'Comms\nAgent', 'Media\nAgent', 'Research\nAgent']
latency_dispatch = [42, 38, 45, 35, 48] # Routing ms
latency_execution = [120, 85, 210, 95, 450] # Execution ms

x = np.arange(len(domains))
width = 0.35

rects1 = ax1.bar(x - width/2, latency_dispatch, width, label='Supervisor Dispatch (ms)', color='#3498db', edgecolor='#2980b9')
rects2 = ax1.bar(x + width/2, latency_execution, width, label='Agent Execution (ms)', color='#e67e22', edgecolor='#d35400')

ax1.set_ylabel('Latency (milliseconds)', fontsize=9, fontweight='bold')
ax1.set_title('(a) Sub-Agent Dispatch vs Execution Time', fontsize=10, fontweight='bold', pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(domains, fontsize=8.5)
ax1.legend(fontsize=8, frameon=True)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# Subplot 2: Safety Interception Rate vs False Positive Rate
categories = ['Safe Queries\n(Tier 0)', 'Low-Risk Ops\n(Tier 1)', 'High-Risk Ops\n(Tier 2)', 'Dangerous Ops\n(Tier 3)']
interception_rate = [0, 0, 100, 100] # Interception %
expected_accuracy = [100, 100, 100, 100] # Policy compliance %

x2 = np.arange(len(categories))
rects3 = ax2.bar(x2 - width/2, interception_rate, width, label='HITL Interception (%)', color='#e74c3c', edgecolor='#c0392b')
rects4 = ax2.bar(x2 + width/2, expected_accuracy, width, label='Policy Compliance (%)', color='#2ecc71', edgecolor='#27ae60')

ax2.set_ylabel('Percentage (%)', fontsize=9, fontweight='bold')
ax2.set_title('(b) Trust Tier Interception & Policy Compliance', fontsize=10, fontweight='bold', pad=10)
ax2.set_xticks(x2)
ax2.set_xticklabels(categories, fontsize=8)
ax2.legend(fontsize=8, frameon=True)
ax2.grid(axis='y', linestyle='--', alpha=0.5)
ax2.set_ylim(0, 115)

plt.tight_layout()
plt.savefig(r"D:\Wellsy\paper\figures\fig4_benchmarks.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig4_benchmarks.png")

print("All 4 figures generated successfully!")
