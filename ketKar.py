import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import matplotlib.gridspec as gridspec
import numpy as np
import math
from matplotlib.patches import Polygon

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


fig = plt.figure(figsize=(10, 10), constrained_layout=True)

gs_main = fig.add_gridspec(2, 1, height_ratios=[5, 1])
ax = fig.add_subplot(gs_main[0, 0])
gs_controls = gs_main[1, 0].subgridspec(3, 4)

def get_endpoint(start_x, start_y, hossz, szog_fok):
    szog_rad = math.radians(szog_fok)
    x_end = start_x + hossz * math.cos(szog_rad)
    y_end = start_y + hossz * math.sin(szog_rad)
    return (x_end, y_end)

(x_joint_init, y_joint_init) = get_endpoint(x_piros_start, y_piros_start, init_piros_hossz, init_piros_szog)
init_kek_szog_GLOBAL = init_piros_szog + init_kek_szog_REL
(x_kek_end_init, y_kek_end_init) = get_endpoint(x_joint_init, y_joint_init, init_kek_hossz, init_kek_szog_GLOBAL)
(x_p_min_init, y_p_min_init) = get_endpoint(x_piros_start, y_piros_start, init_piros_hossz, init_piros_min_szog)
(x_p_max_init, y_p_max_init) = get_endpoint(x_piros_start, y_piros_start, init_piros_hossz, init_piros_max_szog)
init_k_min_glob = init_piros_szog + init_kek_min_szog
init_k_max_glob = init_piros_szog + init_kek_max_szog
(x_k_min_init, y_k_min_init) = get_endpoint(x_joint_init, y_joint_init, init_kek_hossz, init_k_min_glob)
(x_k_max_init, y_k_max_init) = get_endpoint(x_joint_init, y_joint_init, init_kek_hossz, init_k_max_glob)

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


#Munkaterület:
workspace_plot, = ax.plot([], [], marker=',', linestyle='None', visible=False) 

workspace_patch = Polygon(np.array([]).reshape(0, 2), closed=True, color='lightgray', zorder=0, label='Munkaterület')
ax.add_patch(workspace_patch)

ax.set_title('Robotkar Szimuláció (Automatikus méretezés)')
ax.grid(True)
ax.set_aspect('equal') 
ax.margins(0.15) 
handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))
ax.legend(unique_labels.values(), unique_labels.keys()) 

ax_p_hossz = fig.add_subplot(gs_controls[0, 0]) 
ax_p_min   = fig.add_subplot(gs_controls[0, 1]) 
ax_p_max   = fig.add_subplot(gs_controls[0, 2]) 
ax_k_hossz = fig.add_subplot(gs_controls[1, 0]) 
ax_k_min   = fig.add_subplot(gs_controls[1, 1]) 
ax_k_max   = fig.add_subplot(gs_controls[1, 2]) 
ax_button = fig.add_subplot(gs_controls[2, 1:3]) 

text_box_piros_hossz = TextBox(ax_p_hossz, "Piros Hossz:", str(init_piros_hossz))
text_box_piros_min   = TextBox(ax_p_min,   "Piros Min Szög:", str(init_piros_min_szog))
text_box_piros_max   = TextBox(ax_p_max,   "Piros Max Szög:", str(init_piros_max_szog))
text_box_kek_hossz = TextBox(ax_k_hossz, "Kék Hossz:", str(init_kek_hossz))
text_box_kek_min   = TextBox(ax_k_min,   "Kék Min Szög (Rel):", str(init_kek_min_szog))
text_box_kek_max   = TextBox(ax_k_max,   "Kék Max Szög (Rel):", str(init_kek_max_szog))
button = Button(ax_button, 'Módosít', color='lightgoldenrodyellow', hovercolor='0.975')

#Módosítás
def update_plot(event):
    try:
        p_hossz = float(text_box_piros_hossz.text) 
        p_min_szog = float(text_box_piros_min.text)
        p_max_szog = float(text_box_piros_max.text)
        
        k_hossz = float(text_box_kek_hossz.text)
        k_min_szog = float(text_box_kek_min.text)
        k_max_szog = float(text_box_kek_max.text)
        
    except ValueError:
        print("Hiba: Kérjük, érvényes számot adjon meg az összes mezőben.")
        return

    p_aktualis_szog = (p_min_szog + p_max_szog) / 2
    k_aktualis_szog_REL = (k_min_szog + k_max_szog) / 2 
    k_aktualis_szog_GLOBAL = p_aktualis_szog + k_aktualis_szog_REL

    (new_x_joint, new_y_joint) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_aktualis_szog)
    line_piros.set_data([x_piros_start, new_x_joint], [y_piros_start, new_y_joint])
    
    (x_p_min, y_p_min) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_min_szog)
    (x_p_max, y_p_max) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_max_szog)
    line_piros_min.set_data([x_piros_start, x_p_min], [y_piros_start, y_p_min])
    line_piros_max.set_data([x_piros_start, x_p_max], [y_piros_start, y_p_max])

    (new_x_kek_end, new_y_kek_end) = get_endpoint(new_x_joint, new_y_joint, k_hossz, k_aktualis_szog_GLOBAL)
    line_kek.set_data([new_x_joint, new_x_kek_end], [new_y_joint, new_y_kek_end])

    k_global_min_szog = p_aktualis_szog + k_min_szog
    k_global_max_szog = p_aktualis_szog + k_max_szog
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

    
    #1. Belső ív
    inner_arc_x = []
    inner_arc_y = []
    for p_ang in p_angles:
        joint_x, joint_y = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_ang)
        k_ang_glob = p_ang + k_min_szog
        end_x, end_y = get_endpoint(joint_x, joint_y, k_hossz, k_ang_glob)
        inner_arc_x.append(end_x)
        inner_arc_y.append(end_y)
        
    #2. Külső-jobb oldal
    right_side_x = []
    right_side_y = []
    (joint_x, joint_y) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_max_szog)
    for k_ang_rel in k_angles_REL:
        k_ang_glob = p_max_szog + k_ang_rel
        end_x, end_y = get_endpoint(joint_x, joint_y, k_hossz, k_ang_glob)
        right_side_x.append(end_x)
        right_side_y.append(end_y)

    #3. Külső ív 
    outer_arc_x = []
    outer_arc_y = []
    for p_ang in p_angles[::-1]:
        joint_x, joint_y = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_ang)
        k_ang_glob = p_ang + k_max_szog
        end_x, end_y = get_endpoint(joint_x, joint_y, k_hossz, k_ang_glob)
        outer_arc_x.append(end_x)
        outer_arc_y.append(end_y)
        
    # 4. Belső-bal oldal (Fordított)
    left_side_x = []
    left_side_y = []
    (joint_x, joint_y) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_min_szog)
    for k_ang_rel in k_angles_REL[::-1]:
        k_ang_glob = p_min_szog + k_ang_rel
        end_x, end_y = get_endpoint(joint_x, joint_y, k_hossz, k_ang_glob)
        left_side_x.append(end_x)
        left_side_y.append(end_y)

    # Összefűzés
    poly_x_points = inner_arc_x + right_side_x + outer_arc_x + left_side_x
    poly_y_points = inner_arc_y + right_side_y + outer_arc_y + left_side_y
    
    vertices = list(zip(poly_x_points, poly_y_points))

    workspace_patch.set_xy(vertices)
    
    ax.relim() 
    ax.autoscale_view() 
    
    fig.canvas.draw_idle()

button.on_clicked(update_plot)

update_plot(None)

#Eredmény:
plt.show()