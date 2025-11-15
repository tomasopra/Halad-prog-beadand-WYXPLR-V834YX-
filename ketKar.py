import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import matplotlib.gridspec as gridspec
import numpy as np
import math

#kezdeti adatok:
x_piros_start = 1
y_piros_start = 1

init_piros_hossz = 4
init_piros_szog = 45
init_piros_min_szog = 0
init_piros_max_szog = 90
init_kek_hossz = 3
init_kek_szog = -30
init_kek_min_szog = -90
init_kek_max_szog = 0


fig = plt.figure(figsize=(10, 10), constrained_layout=True)
gs = fig.add_gridspec(7, 4)
ax = fig.add_subplot(gs[0:4, :])

def get_endpoint(start_x, start_y, hossz, szog_fok):
    szog_rad = math.radians(szog_fok)
    x_end = start_x + hossz * math.cos(szog_rad)
    y_end = start_y + hossz * math.sin(szog_rad)
    return (x_end, y_end)

(x_joint_init, y_joint_init) = get_endpoint(x_piros_start, y_piros_start, init_piros_hossz, init_piros_szog)
(x_kek_end_init, y_kek_end_init) = get_endpoint(x_joint_init, y_joint_init, init_kek_hossz, init_kek_szog)
(x_p_min_init, y_p_min_init) = get_endpoint(x_piros_start, y_piros_start, init_piros_hossz, init_piros_min_szog)
(x_p_max_init, y_p_max_init) = get_endpoint(x_piros_start, y_piros_start, init_piros_hossz, init_piros_max_szog)
(x_k_min_init, y_k_min_init) = get_endpoint(x_joint_init, y_joint_init, init_kek_hossz, init_kek_min_szog)
(x_k_max_init, y_k_max_init) = get_endpoint(x_joint_init, y_joint_init, init_kek_hossz, init_kek_max_szog)

#Vonalak kirajzolása:
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


ax.set_title('Robotkar Szimuláció (Robusztus GridSpec Elrendezés)')
ax.grid(True)

ax.set_aspect('equal', adjustable='box') 
ax.axis([-5, 15, -5, 15]) 

handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))
ax.legend(unique_labels.values(), unique_labels.keys()) 

ax_p_hossz = fig.add_subplot(gs[4, 0])
ax_p_szog  = fig.add_subplot(gs[4, 1])
ax_p_min   = fig.add_subplot(gs[4, 2])
ax_p_max   = fig.add_subplot(gs[4, 3])

ax_k_hossz = fig.add_subplot(gs[5, 0])
ax_k_szog  = fig.add_subplot(gs[5, 1])
ax_k_min   = fig.add_subplot(gs[5, 2])
ax_k_max   = fig.add_subplot(gs[5, 3]) 


ax_button = fig.add_subplot(gs[6, 1:3])

#Paraméterezés:
text_box_piros_hossz = TextBox(ax_p_hossz, "Piros Hossz:", str(init_piros_hossz))
text_box_piros_szog  = TextBox(ax_p_szog,  "Piros Szög (°):", str(init_piros_szog))
text_box_piros_min   = TextBox(ax_p_min,   "Piros Min Szög:", str(init_piros_min_szog))
text_box_piros_max   = TextBox(ax_p_max,   "Piros Max Szög:", str(init_piros_max_szog))

text_box_kek_hossz = TextBox(ax_k_hossz, "Kék Hossz:", str(init_kek_hossz))
text_box_kek_szog  = TextBox(ax_k_szog,  "Kék Szög (°):", str(init_kek_szog))
text_box_kek_min   = TextBox(ax_k_min,   "Kék Min Szög:", str(init_kek_min_szog))
text_box_kek_max   = TextBox(ax_k_max,   "Kék Max Szög:", str(init_kek_max_szog))


button = Button(ax_button, 'Módosít', color='lightgoldenrodyellow', hovercolor='0.975')

def update_plot(event):
    try:
        p_hossz = float(text_box_piros_hossz.text) 
        p_szog = float(text_box_piros_szog.text)
        p_min_szog = float(text_box_piros_min.text)
        p_max_szog = float(text_box_piros_max.text)
        
        k_hossz = float(text_box_kek_hossz.text)
        k_szog = float(text_box_kek_szog.text)
        k_min_szog = float(text_box_kek_min.text)
        k_max_szog = float(text_box_kek_max.text)
        
    except ValueError:
        print("Hiba: Kérjük, érvényes számot adjon meg az összes mezőben.")
        return

    
    (new_x_joint, new_y_joint) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_szog)
    line_piros.set_data([x_piros_start, new_x_joint], [y_piros_start, new_y_joint])
    
    (x_p_min, y_p_min) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_min_szog)
    (x_p_max, y_p_max) = get_endpoint(x_piros_start, y_piros_start, p_hossz, p_max_szog)
    line_piros_min.set_data([x_piros_start, x_p_min], [y_piros_start, y_p_min])
    line_piros_max.set_data([x_piros_start, x_p_max], [y_piros_start, y_p_max])

    (new_x_kek_end, new_y_kek_end) = get_endpoint(new_x_joint, new_y_joint, k_hossz, k_szog)
    line_kek.set_data([new_x_joint, new_x_kek_end], [new_y_joint, new_y_kek_end])

    (x_k_min, y_k_min) = get_endpoint(new_x_joint, new_y_joint, k_hossz, k_min_szog)
    (x_k_max, y_k_max) = get_endpoint(new_x_joint, new_y_joint, k_hossz, k_max_szog)
    line_kek_min.set_data([new_x_joint, x_k_min], [new_y_joint, y_k_min])
    line_kek_max.set_data([new_x_joint, x_k_max], [new_y_joint, y_k_max])
    
    fig.canvas.draw_idle()

button.on_clicked(update_plot)

#Eredmény:
plt.show()