import matplotlib 
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import matplotlib.gridspec as gridspec
import numpy as np
import math
from matplotlib.animation import FuncAnimation 

#kezdeti adatok
x_piros_start = 1
y_piros_start = 1

init_piros_hossz = 4
init_piros_min_szog = 0
init_piros_max_szog = 90
init_piros_szog = (init_piros_min_szog + init_piros_max_szog) / 2 

init_kek_hossz = 3

init_kek_min_szog_REL = -90   
init_kek_max_szog_REL = 90  
init_kek_szog_REL = (init_kek_min_szog_REL + init_kek_max_szog_REL) / 2 

p_hossz_aktualis = init_piros_hossz
k_hossz_aktualis = init_kek_hossz
p_szog_aktualis = init_piros_szog
k_szog_REL_aktualis = init_kek_szog_REL

p_min_szog_aktualis = init_piros_min_szog
p_max_szog_aktualis = init_piros_max_szog
k_min_szog_REL_aktualis = init_kek_min_szog_REL
k_max_szog_REL_aktualis = init_kek_max_szog_REL

click_pontok = [] 
anim_obj = None 
anim_pontok = [] 
angle_data_list = [] 

text_display = None
coord_A = (0, 0); coord_B = (0, 0); coord_C = (0, 0); coord_D = (0, 0)

fig = plt.figure(figsize=(10, 10), constrained_layout=True)
gs_main = fig.add_gridspec(2, 1, height_ratios=[5, 1])
gs_top = gs_main[0, 0].subgridspec(1, 3, width_ratios=[1, 5, 2])
ax = fig.add_subplot(gs_top[0, 1]) 
ax_text = fig.add_subplot(gs_top[0, 2]) 
gs_controls = gs_main[1, 0].subgridspec(3, 6) 

def get_endpoint(start_x, start_y, hossz, szog_fok):
    szog_rad = math.radians(szog_fok)
    x_end = start_x + hossz * math.cos(szog_rad)
    y_end = start_y + hossz * math.sin(szog_rad)
    return (x_end, y_end)

def solve_ik_all_solutions(target_x, target_y):
    L1 = p_hossz_aktualis
    L2 = k_hossz_aktualis
    tx = target_x - x_piros_start
    ty = target_y - y_piros_start
    D_squared = tx**2 + ty**2
    D = math.sqrt(D_squared)
    
    if D > L1 + L2 + 1e-9 or D < abs(L1 - L2) - 1e-9:
        return [] 
        
    try:
        cos_theta2 = (D_squared - L1**2 - L2**2) / (2 * L1 * L2)
        if cos_theta2 > 1.0: cos_theta2 = 1.0
        if cos_theta2 < -1.0: cos_theta2 = -1.0
        
        solutions = []
        possible_k_rel_rads = [math.acos(cos_theta2), -math.acos(cos_theta2)]
        
        for k_szog_REL_rad in possible_k_rel_rads:
            p_szog_rad = math.atan2(ty, tx) - math.atan2(
                L2 * math.sin(k_szog_REL_rad),
                L1 + L2 * math.cos(k_szog_REL_rad)
            )
            
            p_szog_deg = math.degrees(p_szog_rad)
            k_szog_REL_deg = math.degrees(k_szog_REL_rad)
            
            solutions.append((p_szog_deg, k_szog_REL_deg))
            
        return solutions
    except (ValueError, ZeroDivisionError):
        return []

(x_joint_init, y_joint_init) = get_endpoint(x_piros_start, y_piros_start, init_piros_hossz, init_piros_szog)
(x_kek_end_init, y_kek_end_init) = get_endpoint(x_joint_init, y_joint_init, init_kek_hossz, init_piros_szog + init_kek_szog_REL)

workspace_plot, = ax.plot([], [], marker='o', linestyle='None', 
                          markersize=15, markeredgewidth=0, 
                          color='#e0e0e0', 
                          zorder=0, label='Munkaterület')

line_piros, = ax.plot([], [], 'r-', lw=3, label='Piros vonal', zorder=10)
line_kek, = ax.plot([], [], 'b-', lw=3, label='Kék vonal', zorder=10)

line_piros_min, = ax.plot([], [], 'r:', lw=1, zorder=5, label='Piros tartomány')
line_piros_max, = ax.plot([], [], 'r:', lw=1, zorder=5)
line_kek_min, = ax.plot([], [], 'b:', lw=1, zorder=5, label='Kék tartomány')
line_kek_max, = ax.plot([], [], 'b:', lw=1, zorder=5)
line_munkavonal, = ax.plot([], [], 'g-', lw=2, zorder=8, label='Munkavonal')

bbox_style = dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.7)
label_A = ax.text(0, 0, 'A', fontsize=12, fontweight='bold', bbox=bbox_style, zorder=15)
label_B = ax.text(0, 0, 'B', fontsize=12, fontweight='bold', bbox=bbox_style, zorder=15)
label_C = ax.text(0, 0, 'C', fontsize=12, fontweight='bold', bbox=bbox_style, zorder=15)
label_D = ax.text(0, 0, 'D', fontsize=12, fontweight='bold', bbox=bbox_style, zorder=15)

#koordinátarendszer beállítások
ax.set_title('Robotkar Szimuláció', fontsize=14) 
ax.grid(True)
ax.set_aspect('equal') 
handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))

ax_text.axis('off') 
ax_text.legend(unique_labels.values(), unique_labels.keys(), fontsize=12, loc='upper left', bbox_to_anchor=(0, 1.0))
text_display = ax_text.text(0.0, 0.65, "", fontsize=14, va='top', wrap=True, family='monospace')

#vezérlők
ax_p_hossz = fig.add_subplot(gs_controls[0, 0:2]) 
ax_p_min = fig.add_subplot(gs_controls[0, 2:4]) 
ax_p_max = fig.add_subplot(gs_controls[0, 4:6]) 
ax_k_hossz = fig.add_subplot(gs_controls[1, 0:2]) 
ax_k_min = fig.add_subplot(gs_controls[1, 2:4]) 
ax_k_max = fig.add_subplot(gs_controls[1, 4:6]) 
ax_button = fig.add_subplot(gs_controls[2, 1:3]) 
ax_button_start = fig.add_subplot(gs_controls[2, 3:5])

text_box_piros_hossz = TextBox(ax_p_hossz, "Piros Hossz:", str(init_piros_hossz), color='mistyrose')
text_box_piros_min = TextBox(ax_p_min, "Piros Min Szög:", str(init_piros_min_szog), color='mistyrose')
text_box_piros_max = TextBox(ax_p_max, "Piros Max Szög:", str(init_piros_max_szog), color='mistyrose')
text_box_kek_hossz = TextBox(ax_k_hossz, "Kék Hossz:", str(init_kek_hossz), color='lightblue')
text_box_kek_min = TextBox(ax_k_min, "Kék Min Szög (Rel):", str(init_kek_min_szog_REL), color='lightblue')
text_box_kek_max = TextBox(ax_k_max, "Kék Max Szög (Rel):", str(init_kek_max_szog_REL), color='lightblue')
button = Button(ax_button, 'Módosít', color='lightgoldenrodyellow', hovercolor='0.975')
button_start = Button(ax_button_start, 'Start Animáció', color='lightgreen', hovercolor='0.975')

def set_info_text(p_ang=None, k_rel_ang=None, angle_list=None):
    global text_display, coord_A, coord_B, coord_C, coord_D
    text_str = ""
    if angle_list is not None:
        text_str = "Munkavonal szögei:\n"
        text_display.set_fontsize(12) 
        for i, angles in enumerate(angle_list):
            p_szog_list, k_szog_rel_list = angles
            text_str += f"{i+1:2}. P:{p_szog_list:5.1f}° K:{k_szog_rel_list:5.1f}°\n"
    elif p_ang is not None:
        text_display.set_fontsize(14) 
        text_str = "Aktuális szögek:\n"
        text_str += f"Piros: {p_ang: 6.1f}°\n"
        text_str += f"Kék (Rel): {k_rel_ang: 6.1f}°\n"
    
    text_str += "------------------\nSarokpontok (XY):\n"
    text_str += f"A: ({coord_A[0]: 6.2f}, {coord_A[1]: 6.2f})\n"
    text_str += f"B: ({coord_B[0]: 6.2f}, {coord_B[1]: 6.2f})\n"
    text_str += f"C: ({coord_C[0]: 6.2f}, {coord_C[1]: 6.2f})\n"
    text_str += f"D: ({coord_D[0]: 6.2f}, {coord_D[1]: 6.2f})"
    if text_display: text_display.set_text(text_str)

def update_plot(event):
    global p_hossz_aktualis, k_hossz_aktualis, click_pontok, anim_obj
    global p_szog_aktualis, k_szog_REL_aktualis
    global p_min_szog_aktualis, p_max_szog_aktualis, k_min_szog_REL_aktualis, k_max_szog_REL_aktualis
    global coord_A, coord_B, coord_C, coord_D
    
    try:
        p_hossz = float(text_box_piros_hossz.text) 
        p_min_szog = float(text_box_piros_min.text)
        p_max_szog = float(text_box_piros_max.text)
        k_hossz = float(text_box_kek_hossz.text)
        k_min_szog_rel = float(text_box_kek_min.text)
        k_max_szog_rel = float(text_box_kek_max.text)
        
        if p_hossz <= 0 or k_hossz <= 0: raise ValueError("A hossz nem lehet <= 0.")
        if p_min_szog > 360 or p_max_szog > 360: raise ValueError("Piros szög > 360°.")
        if k_min_szog_rel < -360 or k_max_szog_rel < -360: raise ValueError("Kék szög < -360°.")
        if k_min_szog_rel > 360 or k_max_szog_rel > 360: raise ValueError("Kék szög > 360°.")
        if p_min_szog > p_max_szog: raise ValueError("Piros min > max.")
        if k_min_szog_rel > k_max_szog_rel: raise ValueError("Kék min > max.")

    except ValueError as e:
        print(f"Validálási hiba: {e}")
        text_display.set_text(f"HIBA:\n{str(e)}\n\nÉrtékek visszaállítva.")
        text_box_piros_hossz.set_val(str(p_hossz_aktualis))
        text_box_piros_min.set_val(str(p_min_szog_aktualis))
        text_box_piros_max.set_val(str(p_max_szog_aktualis))
        text_box_kek_hossz.set_val(str(k_hossz_aktualis))
        text_box_kek_min.set_val(str(k_min_szog_REL_aktualis))
        text_box_kek_max.set_val(str(k_max_szog_REL_aktualis))
        fig.canvas.draw_idle()
        return 

    p_hossz_aktualis = p_hossz
    k_hossz_aktualis = k_hossz
    p_min_szog_aktualis = p_min_szog
    p_max_szog_aktualis = p_max_szog
    k_min_szog_REL_aktualis = k_min_szog_rel
    k_max_szog_REL_aktualis = k_max_szog_rel
    
    click_pontok = []
    line_munkavonal.set_data([], [])
    if anim_obj and anim_obj.event_source: anim_obj.event_source.stop()
    anim_obj = None

    p_szog_aktualis = (p_min_szog + p_max_szog) / 2
    k_szog_REL_aktualis = (k_min_szog_rel + k_max_szog_rel) / 2
    
    (new_x_joint, new_y_joint) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_szog_aktualis)
    line_piros.set_data([x_piros_start, new_x_joint], [y_piros_start, new_y_joint])
    
    abs_kek_szog = p_szog_aktualis + k_szog_REL_aktualis
    (new_x_kek_end, new_y_kek_end) = get_endpoint(new_x_joint, new_y_joint, k_hossz, abs_kek_szog)
    line_kek.set_data([new_x_joint, new_x_kek_end], [new_y_joint, new_y_kek_end])
    
    #segédvonalak
    (x_p_min, y_p_min) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_min_szog)
    (x_p_max, y_p_max) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_max_szog)
    line_piros_min.set_data([x_piros_start, x_p_min], [y_piros_start, y_p_min])
    line_piros_max.set_data([x_piros_start, x_p_max], [y_piros_start, y_p_max])
    
    (x_k_min, y_k_min) = get_endpoint(new_x_joint, new_y_joint, k_hossz, p_szog_aktualis + k_min_szog_rel)
    (x_k_max, y_k_max) = get_endpoint(new_x_joint, new_y_joint, k_hossz, p_szog_aktualis + k_max_szog_rel)
    line_kek_min.set_data([new_x_joint, x_k_min], [new_y_joint, y_k_min])
    line_kek_max.set_data([new_x_joint, x_k_max], [new_y_joint, y_k_max])
    
    RESOLUTION = 40 
    p_vals = np.linspace(p_min_szog, p_max_szog, RESOLUTION)
    k_vals = np.linspace(k_min_szog_rel, k_max_szog_rel, RESOLUTION)
    
    P_grid, K_grid = np.meshgrid(np.radians(p_vals), np.radians(k_vals))
    
    X_grid = x_piros_start + p_hossz * np.cos(P_grid) + k_hossz * np.cos(P_grid + K_grid)
    Y_grid = y_piros_start + p_hossz * np.sin(P_grid) + k_hossz * np.sin(P_grid + K_grid)
    
    workspace_plot.set_data(X_grid.flatten(), Y_grid.flatten())
    
    def calc_abs_pos(p_ang, k_rel):
        jx, jy = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_ang)
        return get_endpoint(jx, jy, k_hossz, p_ang + k_rel)

    coord_A = calc_abs_pos(p_min_szog, k_min_szog_rel)
    coord_B = calc_abs_pos(p_min_szog, k_max_szog_rel)
    coord_C = calc_abs_pos(p_max_szog, k_max_szog_rel)
    coord_D = calc_abs_pos(p_max_szog, k_min_szog_rel)
    
    label_A.set_position(coord_A); label_B.set_position(coord_B)
    label_C.set_position(coord_C); label_D.set_position(coord_D)
    
    set_info_text(p_ang=p_szog_aktualis, k_rel_ang=k_szog_REL_aktualis)
    
    teljes_hossz = p_hossz + k_hossz
    margó = teljes_hossz * 0.2
    ax.set_xlim(x_piros_start - (teljes_hossz + margó)*0.5, x_piros_start + (teljes_hossz + margó))
    ax.set_ylim(y_piros_start - (teljes_hossz + margó)*0.5, y_piros_start + (teljes_hossz + margó))

    fig.canvas.draw_idle()

def onclick(event):
    global click_pontok
    if event.inaxes != ax: return
    if len(click_pontok) >= 2: click_pontok = []
    click_pontok.append((event.xdata, event.ydata))
    if len(click_pontok) == 2:
        x_data = [click_pontok[0][0], click_pontok[1][0]]
        y_data = [click_pontok[0][1], click_pontok[1][1]]
        line_munkavonal.set_data(x_data, y_data)
    else:
        line_munkavonal.set_data([], [])
    fig.canvas.draw_idle()

def on_start_anim(event):
    global anim_obj, anim_pontok, angle_data_list
    if len(click_pontok) < 2:
        print("Animációs hiba: Nincs munkavonal.")
        text_display.set_text("Animációs hiba:\nNincs munkavonal kijelölve.")
        fig.canvas.draw_idle()
        return
        
    x_vals = np.linspace(click_pontok[0][0], click_pontok[1][0], 10) 
    y_vals = np.linspace(click_pontok[0][1], click_pontok[1][1], 10)
    anim_pontok = list(zip(x_vals, y_vals))
    
    angle_data_list = [] 
    is_valid = True
    prev_solution = None 

    for (x, y) in anim_pontok:
        possible_solutions = solve_ik_all_solutions(x, y)
        
        if not possible_solutions:
            is_valid = False
            break
        
        valid_candidates = []
        eps = 0.1
        for sol in possible_solutions:
            p_deg, k_rel_deg = sol
            
            p_ok = (p_min_szog_aktualis - eps <= p_deg <= p_max_szog_aktualis + eps)
            k_ok = (k_min_szog_REL_aktualis - eps <= k_rel_deg <= k_max_szog_REL_aktualis + eps)
            
            if p_ok and k_ok:
                valid_candidates.append(sol)
        
        if not valid_candidates:
            is_valid = False
            break
            
        if prev_solution is None:
            chosen = valid_candidates[0]
        else:
            chosen = min(valid_candidates, key=lambda s: abs(s[0]-prev_solution[0]) + abs(s[1]-prev_solution[1]))
            
        angle_data_list.append(chosen)
        prev_solution = chosen
            
    if not is_valid:
        print("Animációs hiba: Kívül esik a határokon.")
        text_display.set_text("Animációs hiba:\nA pont nem elérhető,\nvagy a szöghatárokon kívül esik.")
        if anim_obj and anim_obj.event_source: anim_obj.event_source.stop()
        anim_obj = None
        fig.canvas.draw_idle()
        return
    
    set_info_text(angle_list=angle_data_list)
    if anim_obj and anim_obj.event_source: anim_obj.event_source.stop()
    anim_obj = FuncAnimation(fig, animate, frames=len(anim_pontok), init_func=init_anim, interval=200, blit=False, repeat=False)
    fig.canvas.draw_idle()

def init_anim(): return ()

def animate(frame):
    global p_szog_aktualis, k_szog_REL_aktualis
    angles = angle_data_list[frame] 
    if angles is None: return ()
    p_szog, k_szog_rel = angles
    p_szog_aktualis = p_szog
    k_szog_REL_aktualis = k_szog_rel
    
    (new_x_joint, new_y_joint) = get_endpoint(x_piros_start, y_piros_start, p_hossz_aktualis, p_szog)
    line_piros.set_data([x_piros_start, new_x_joint], [y_piros_start, new_y_joint])
    
    (new_x_kek_end, new_y_kek_end) = get_endpoint(new_x_joint, new_y_joint, k_hossz_aktualis, p_szog + k_szog_rel)
    line_kek.set_data([new_x_joint, new_x_kek_end], [new_y_joint, new_y_kek_end])
    return ()

button.on_clicked(update_plot)
button_start.on_clicked(on_start_anim) 
fig.canvas.mpl_connect('button_press_event', onclick) 
update_plot(None)
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')
#megjelenítés
plt.show()