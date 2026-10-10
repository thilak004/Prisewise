import matplotlib.pyplot as plt
import numpy as np

def create_aditya_logo():
    fig, ax = plt.subplots(figsize=(6, 1.2), dpi=300)
    ax.axis('off')
    
    # Draw circular sunburst emblem on the left
    theta = np.linspace(0, 2*np.pi, 24, endpoint=False)
    center_x, center_y = 0.12, 0.5
    r_outer = 0.28
    r_inner = 0.18
    
    # Outer rays
    for t in theta:
        x_pts = [center_x, center_x + r_outer * np.cos(t)]
        y_pts = [center_y, center_y + r_outer * np.sin(t)]
        ax.plot(x_pts, y_pts, color='#D97706', lw=1.2)
        
    # Concentric rings
    c1 = plt.Circle((center_x, center_y), r_inner, color='#D97706', fill=False, lw=1.5)
    c2 = plt.Circle((center_x, center_y), r_inner*0.6, color='#DC2626', fill=False, lw=1.2)
    c3 = plt.Circle((center_x, center_y), r_inner*0.25, color='#D97706', fill=True)
    ax.add_patch(c1)
    ax.add_patch(c2)
    ax.add_patch(c3)
    
    # Text "ADITYA UNIVERSITY"
    ax.text(0.30, 0.46, "ADITYA", fontsize=24, weight='bold', color='#E05326', fontname='DejaVu Sans', va='center')
    ax.text(0.61, 0.46, "UNIVERSITY", fontsize=24, weight='bold', color='#1E427B', fontname='DejaVu Sans', va='center')
    
    ax.set_xlim(0, 1.2)
    ax.set_ylim(0, 1.0)
    plt.tight_layout()
    plt.savefig('docs_assets/aditya_logo.png', bbox_inches='tight', transparent=True)
    plt.close()
    print("Created aditya_logo.png successfully")

if __name__ == '__main__':
    create_aditya_logo()
