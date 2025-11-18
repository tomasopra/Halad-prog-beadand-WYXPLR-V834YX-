import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import matplotlib.gridspec as gridspec
import numpy as np
import math
from matplotlib.patches import Polygon
from matplotlib.animation import FuncAnimation 

#kezdeti adatok:
x_piros_start = 1
y_piros_start = 1

init_piros_hossz = 4
init_piros_min_szog = 0
init_piros_max_szog = 90
init_piros_szog = (init_piros_min_szog + init_piros_max_szog) / 2 

init_kek_hossz = 3
init_kek_min_szog = -90 
init_kek_max_szog = 0 
init_kek_szog_REL = (init_kek_min_szog + init_kek_max_szog) / 2 

p_hossz_aktualis = init_piros_hossz
k_hossz_aktualis = init_kek_hossz
p_szog_aktualis = init_piros_szog
k_szog_REL_aktualis = init_kek_szog_REL

click_pontok = [] 
anim_obj = None 
anim_pontok = [] 
angle_data_list = [] 

text_display = None

fig = plt.figure(figsize=(10, 10), constrained_layout=True)

gs_main = fig.add_gridspec(2, 1, height_ratios=[5, 1])
gs_top = gs_main[0, 0].subgridspec(1, 2, width_ratios=[4, 1])
ax = fig.add_subplot(gs_top[0, 0])
ax_text = fig.add_subplot(gs_top[0, 1])
gs_controls = gs_main[1, 0].subgridspec(3, 4) 

def get_endpoint(start_x, start_y, hossz, szog_fok):
    szog_rad = math.radians(szog_fok)
    x_end = start_x + hossz * math.cos(szog_rad)
    y_end = start_y + hossz * math.sin(szog_rad)
    return (x_end, y_end)

def solve_ik(target_x, target_y):
    L1 = p_hossz_aktualis
    L2 = k_hossz_aktualis
    tx = target_x - x_piros_start
    ty = target_y - y_piros_start
    D_squared = tx**2 + ty**2
    D = math.sqrt(D_squared)
    
    if D > L1 + L2 or D < abs(L1 - L2):
        print(f"Figyelmeztetés: A ({target_x:.1f}, {target_y:.1f}) pont elérhetetlen.")
        return None 
    try:
        cos_theta2 = (D_squared - L1**2 - L2**2) / (2 * L1 * L2)
        if cos_theta2 > 1.0: cos_theta2 = 1.0
        if cos_theta2 < -1.0: cos_theta2 = -1.0
        k_szog_REL_rad = -math.acos(cos_theta2) 
        p_szog_rad = math.atan2(ty, tx) - math.atan2(
            L2 * math.sin(k_szog_REL_rad),
            L1 + L2 * math.cos(k_szog_REL_rad)
        )
        return (math.degrees(p_szog_rad), math.degrees(k_szog_REL_rad))
    except (ValueError, ZeroDivisionError):
        return None

(x_joint_init, y_joint_init) = get_endpoint(x_piros_start, y_piros_start, init_piros_hossz, init_piros_szog)
init_kek_szog_GLOBAL = init_piros_szog + init_kek_szog_REL
(x_kek_end_init, y_kek_end_init) = get_endpoint(x_joint_init, y_joint_init, init_kek_hossz, init_kek_szog_GLOBAL)
(x_p_min_init, y_p_min_init) = get_endpoint(x_piros_start, y_piros_start, init_piros_hossz, init_piros_min_szog)
(x_p_max_init, y_p_max_init) = get_endpoint(x_piros_start, y_piros_start, init_piros_hossz, init_piros_max_szog)
init_k_min_glob = init_piros_szog + init_kek_min_szog
init_k_max_glob = init_piros_szog + init_kek_max_szog
(x_k_min_init, y_k_min_init) = get_endpoint(x_joint_init, y_joint_init, init_kek_hossz, init_k_min_glob)
(x_k_max_init, y_k_max_init) = get_endpoint(x_joint_init, y_joint_init, init_kek_hossz, init_k_max_glob)

#vonalak
line_piros, = ax.plot([x_piros_start, x_joint_init], [y_piros_start, y_joint_init], 
                      'r-', lw=3, label='Piros vonal', zorder=10)
line_kek, = ax.plot([x_joint_init, x_kek_end_init], [y_joint_init, y_kek_end_init], 
                     'b-', lw=3, label='Kék vonal', zorder=10)
line_piros_min, = ax.plot([x_piros_start, x_p_min_init], [y_piros_start, y_p_min_init], 
                          'r:', lw=1, zorder=5, label='Piros tartomány')
line_piros_max, = ax.plot([x_piros_start, x_p_max_init], [y_piros_start, y_p_max_init], 'r:', lw=1, zorder=5)
line_kek_min, = ax.plot([x_joint_init, x_k_min_init], [y_joint_init, y_k_min_init], 
                         'b:', lw=1, zorder=5, label='Kék tartomány')
line_kek_max, = ax.plot([x_joint_init, x_k_max_init], [y_joint_init, y_k_max_init], 'b:', lw=1, zorder=5)
line_munkavonal, = ax.plot([], [], 'g-', lw=2, zorder=8, label='Munkavonal')

#munkaterület
workspace_plot, = ax.plot([], [], marker=',', linestyle='None', visible=False) 
workspace_patch = Polygon(np.array([]).reshape(0, 2), closed=True, color='lightgray', zorder=0, label='Munkaterület')
ax.add_patch(workspace_patch)


ax.set_title('Robotkar Szimuláció (Animációval)')
ax.grid(True)
ax.set_aspect('equal') 
ax.margins(0.15) 
handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))
ax.legend(unique_labels.values(), unique_labels.keys()) 


ax_text.axis('off') 
text_display = ax_text.text(0.05, 0.95, "", 
                            fontsize=9, 
                            va='top', 
                            wrap=True)

ax_p_hossz = fig.add_subplot(gs_controls[0, 0]) 
ax_p_min   = fig.add_subplot(gs_controls[0, 1]) 
ax_p_max   = fig.add_subplot(gs_controls[0, 2]) 
ax_k_hossz = fig.add_subplot(gs_controls[1, 0]) 
ax_k_min   = fig.add_subplot(gs_controls[1, 1]) 
ax_k_max   = fig.add_subplot(gs_controls[1, 2]) 
ax_button = fig.add_subplot(gs_controls[2, 0:2]) 
ax_button_start = fig.add_subplot(gs_controls[2, 2:4])

text_box_piros_hossz = TextBox(ax_p_hossz, "Piros Hossz:", str(init_piros_hossz))
text_box_piros_min   = TextBox(ax_p_min,   "Piros Min Szög:", str(init_piros_min_szog))
text_box_piros_max   = TextBox(ax_p_max,   "Piros Max Szög:", str(init_piros_max_szog))
text_box_kek_hossz = TextBox(ax_k_hossz, "Kék Hossz:", str(init_kek_hossz))
text_box_kek_min   = TextBox(ax_k_min,   "Kék Min Szög (Rel):", str(init_kek_min_szog))
text_box_kek_max   = TextBox(ax_k_max,   "Kék Max Szög (Rel):", str(init_kek_max_szog))
button = Button(ax_button, 'Módosít', color='lightgoldenrodyellow', hovercolor='0.975')
button_start = Button(ax_button_start, 'Start Animáció', color='lightgreen', hovercolor='0.975')


def update_plot(event):
    global p_hossz_aktualis, k_hossz_aktualis, click_pontok, anim_obj
    global p_szog_aktualis, k_szog_REL_aktualis
    
    try:
        p_hossz = float(text_box_piros_hossz.text) 
        p_min_szog = float(text_box_piros_min.text)
        p_max_szog = float(text_box_piros_max.text)
        k_hossz = float(text_box_kek_hossz.text)
        k_min_szog = float(text_box_kek_min.text) 
        k_max_szog = float(text_box_kek_max.text) 
        
        p_hossz_aktualis = p_hossz
        k_hossz_aktualis = k_hossz
        
        click_pontok = []
        line_munkavonal.set_data([], [])
        
        if anim_obj and anim_obj.event_source:
            anim_obj.event_source.stop()
        anim_obj = None
        
    except ValueError:
        print("Hiba: Kérjük, érvényes számot adjon meg az összes mezőben.")
        return

    p_szog_aktualis = (p_min_szog + p_max_szog) / 2
    k_szog_REL_aktualis = (k_min_szog + k_max_szog) / 2
    
    #A munkaterület és vonalak frissítése
    k_aktualis_szog_GLOBAL = p_szog_aktualis + k_szog_REL_aktualis
    (new_x_joint, new_y_joint) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_szog_aktualis)
    line_piros.set_data([x_piros_start, new_x_joint], [y_piros_start, new_y_joint])
    (x_p_min, y_p_min) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_min_szog)
    (x_p_max, y_p_max) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_max_szog)
    line_piros_min.set_data([x_piros_start, x_p_min], [y_piros_start, y_p_min])
    line_piros_max.set_data([x_piros_start, x_p_max], [y_piros_start, y_p_max])
    (new_x_kek_end, new_y_kek_end) = get_endpoint(new_x_joint, new_y_joint, k_hossz, k_aktualis_szog_GLOBAL)
    line_kek.set_data([new_x_joint, new_x_kek_end], [new_y_joint, new_y_kek_end])
    k_global_min_szog = p_szog_aktualis + k_min_szog
    k_global_max_szog = p_szog_aktualis + k_max_szog
    (x_k_min, y_k_min) = get_endpoint(new_x_joint, new_y_joint, k_hossz, k_global_min_szog)
    (x_k_max, y_k_max) = get_endpoint(new_x_joint, new_y_joint, k_hossz, k_global_max_szog)
    line_kek_min.set_data([new_x_joint, x_k_min], [new_y_joint, y_k_min])
    line_kek_max.set_data([new_x_joint, x_k_max], [new_y_joint, y_k_max])
    N_STEPS = 50 
    p_angles = np.linspace(p_min_szog, p_max_szog, N_STEPS)
    k_angles_REL = np.linspace(k_min_szog, k_max_szog, N_STEPS)
    all_x_points = []
    all_y_points = []
    for p_ang in p_angles:
        (joint_x, joint_y) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_ang)
        for k_ang_rel in k_angles_REL:
            k_ang_glob = p_ang + k_ang_rel
            (end_x, end_y) = get_endpoint(joint_x, joint_y, k_hossz, k_ang_glob)
            all_x_points.append(end_x)
            all_y_points.append(end_y)
    workspace_plot.set_data(all_x_points, all_y_points) 
    inner_arc_x = []
    inner_arc_y = []
    for p_ang in p_angles:
        joint_x, joint_y = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_ang)
        k_ang_glob = p_ang + k_min_szog
        end_x, end_y = get_endpoint(joint_x, joint_y, k_hossz, k_ang_glob)
        inner_arc_x.append(end_x)
        inner_arc_y.append(end_y)
    right_side_x = []
    right_side_y = []
    (joint_x, joint_y) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_max_szog)
    for k_ang_rel in k_angles_REL:
        k_ang_glob = p_max_szog + k_ang_rel
        end_x, end_y = get_endpoint(joint_x, joint_y, k_hossz, k_ang_glob)
        right_side_x.append(end_x)
        right_side_y.append(end_y)
    outer_arc_x = []
    outer_arc_y = []
    for p_ang in p_angles[::-1]:
        joint_x, joint_y = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_ang)
        k_ang_glob = p_ang + k_max_szog
        end_x, end_y = get_endpoint(joint_x, joint_y, k_hossz, k_ang_glob)
        outer_arc_x.append(end_x)
        outer_arc_y.append(end_y)
    left_side_x = []
    left_side_y = []
    (joint_x, joint_y) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_min_szog)
    for k_ang_rel in k_angles_REL[::-1]:
        k_ang_glob = p_min_szog + k_ang_rel
        end_x, end_y = get_endpoint(joint_x, joint_y, k_hossz, k_ang_glob)
        left_side_x.append(end_x)
        left_side_y.append(end_y)
    poly_x_points = inner_arc_x + right_side_x + outer_arc_x + left_side_x
    poly_y_points = inner_arc_y + right_side_y + outer_arc_y + left_side_y
    vertices = list(zip(poly_x_points, poly_y_points))
    workspace_patch.set_xy(vertices)
    
    text_str = f"Aktuális szögek:\n\nPiros: {p_szog_aktualis:.1f}°\n\nKék (Rel): {k_szog_REL_aktualis:.1f}°"
    text_display.set_text(text_str)
    
    ax.relim() 
    ax.autoscale_view() 
    fig.canvas.draw_idle()

def onclick(event):
    global click_pontok
    if event.inaxes != ax:
        return
    if len(click_pontok) >= 2:
        click_pontok = []
    click_pontok.append((event.xdata, event.ydata))
    if len(click_pontok) == 2:
        x_data = [click_pontok[0][0], click_pontok[1][0]]
        y_data = [click_pontok[0][1], click_pontok[1][1]]
        line_munkavonal.set_data(x_data, y_data)
    else:
        line_munkavonal.set_data([], [])
    fig.canvas.draw_idle()

#Animáció
def on_start_anim(event):
    global anim_obj, anim_pontok, angle_data_list
    
    if len(click_pontok) < 2:
        print("Animációs hiba: Nincs munkavonal kijelölve (kattints kétszer a grafikonra).")
        return
        
    x_vals = np.linspace(click_pontok[0][0], click_pontok[1][0], 10)
    y_vals = np.linspace(click_pontok[0][1], click_pontok[1][1], 10)
    anim_pontok = list(zip(x_vals, y_vals))
    
    angle_data_list = []
    text_str = "Munkavonal szögei:\n\n"
    
    for i, (x, y) in enumerate(anim_pontok):
        angles = solve_ik(x, y)
        angle_data_list.append(angles)
        
        if angles:
            p_szog, k_szog_REL = angles
            text_str += f"{i+1}. P: {p_szog:.1f}°, K: {k_szog_REL:.1f}°\n"
        else:
            text_str += f"{i+1}. Elérhetetlen\n"

    text_display.set_text(text_str)
    

    if anim_obj and anim_obj.event_source:
        anim_obj.event_source.stop()
        
    anim_obj = FuncAnimation(
        fig,                
        animate,            
        frames=len(anim_pontok), 
        init_func=init_anim,  
        interval=200,       
        blit=False,         
        repeat=False        
    )
    fig.canvas.draw_idle()

def init_anim():
    return ()

def animate(frame):
    """Az animáció egy képkockája."""
    global p_szog_aktualis, k_szog_REL_aktualis, angle_data_list
    
    angles = angle_data_list[frame] 
    
    if angles is None:
        return ()
        
    p_szog, k_szog_REL = angles
    
    p_szog_aktualis = p_szog
    k_szog_REL_aktualis = k_szog_REL
    
    p_hossz = p_hossz_aktualis
    k_hossz = k_hossz_aktualis
    k_szog_GLOBAL = p_szog + k_szog_REL
    
    (new_x_joint, new_y_joint) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_szog)
    line_piros.set_data([x_piros_start, new_x_joint], [y_piros_start, new_y_joint])
    
    (new_x_kek_end, new_y_kek_end) = get_endpoint(new_x_joint, new_y_joint, k_hossz, k_szog_GLOBAL)
    line_kek.set_data([new_x_joint, new_x_kek_end], [new_y_joint, new_y_kek_end])
    
    return ()


button.on_clicked(update_plot)
button_start.on_clicked(on_start_anim) 
fig.canvas.mpl_connect('button_press_event', onclick) 

update_plot(None)

#Eredmény:
plt.show()