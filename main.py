import os
import sys
from tkinter import *
from pygame import mixer
from random import random, choice
from math import sin, cos, tan, pi, exp

WIDTH = 800
HEIGHT = 500


class Droplet:
    def __init__(self, layer, angle, master=None):
        global WIDTH, HEIGHT
        self.master = master
        self.y = 40 + 10 * random()
        self.x = self.y * tan(angle)

        delta = abs(int(tan(angle) * WIDTH))

        self.line = self.master.create_line(0, 0, -30*sin(angle), -30*cos(angle),
                                            fill=transparency(self.master, 0.3 + layer * 0.02), width=1)
        self.master.move(self.line, (WIDTH + 2 * delta) * random() - delta, -5)
        self.master.pack()

        self.movement(layer, angle)

    def movement(self, layer, angle):
        if self.master.coords(self.line)[1] > HEIGHT - 100 + layer * 5:
            self.impact(layer, angle)
            return
        self.master.move(self.line, self.x, self.y)
        self.master.after(10, lambda: self.movement(layer, angle))

    def impact(self, layer, angle):
        Splash(self.master.coords(self.line)[0], self.master.coords(self.line)[1], layer, angle, self.master)

        spray_count = int(6 * random())
        for i in range(spray_count):
            Spray(self.master.coords(self.line)[0], self.master.coords(self.line)[1], layer, angle, self.master)

        self.master.delete(self.line)


class Splash:
    def __init__(self, x, y, layer, angle, master=None):
        self.master = master
        self.width = 1.5
        self.height = 0.5

        self.splash = self.master.create_oval(
            0, 0, self.width, self.height, fill=transparency(self.master, 0.2), outline="")
        self.master.move(self.splash, x, y)
        self.ripple(x, y, self.width, self.height, layer, angle)

    def ripple(self, x, y, width, height, layer, angle):
        width += 0.75 + 2.5 * (- cos(angle) + 1) * (layer + 20) / 40
        height += 0.25 * (layer + 10) / 30
        alpha = 0.1 + (layer / 150) - 0.05 * random()

        if width > (7 + 18 * (- cos(angle) + 1)) * (layer + 20) / 40:
            self.master.delete(self.splash)
            return

        [x0, y0, x1, y1] = self.master.coords(self.splash)
        self.master.coords(self.splash, x0 - width * cos(angle), y0 - height, x1 + width, y1 + height)
        self.master.itemconfig(self.splash,
                               fill=transparency(self.master, alpha),
                               outline=transparency(self.master, 2 * alpha))

        self.master.after(50, lambda: self.ripple(x, y, width, height, layer, angle))


class Spray:
    def __init__(self, x, y, layer, angle, master=None):
        self.master = master
        alpha = transparency(self.master, 0.5 + (layer / 80) - 0.1 * random())
        self.spray = self.master.create_oval(0, 0, 1, 1, fill=alpha, outline="")
        self.master.move(self.spray, x, y)
        self.movement(x, y, 40 * (random() - 0.5) + 30 * tan(angle), 5 * random() - 20, angle, 0)

    def movement(self, x, y, dx, dy, angle, distance=0):
        self.master.move(self.spray, dx, dy)
        if distance > 2 + 3 * random():
            self.master.delete(self.spray)
        else:
            self.master.after(50, lambda: self.movement(x + dx, y + dy, dx, dy, angle, distance + 1))


class Snow:
    def __init__(self, layer, angle, master=None):
        global WIDTH
        self.master = master
        self.y = 15 + 3 * random()
        self.x = self.y * (1 + 2 * random()) * tan(angle)
        self.size = 0.2 * layer + 3 * random() + 1
        self.alpha = 0.2 + layer * 0.01

        delta = abs(int(tan(angle) * WIDTH))

        self.oval = self.master.create_oval(0, 0, self.size, self.size,
                                            fill=transparency(self.master, self.alpha), outline="")
        self.master.move(self.oval, (WIDTH + 2.5 * delta) * random() - 1.5 * delta, -5)
        self.master.pack()

        self.movement(layer, angle)

    def movement(self, layer, angle):
        if self.master.coords(self.oval)[1] > HEIGHT - 120 + layer * 5:
            self.land(self.alpha, -1 + 3 * random())
            return
        self.master.move(self.oval, self.x, self.y)
        self.master.after(20, lambda: self.movement(layer, angle))

    def land(self, alpha, direction):
        if self.x <= self.master.winfo_width():
            if int(5 * random()) == 4 and abs(wind_speed.get()) > 10:
                self.master.move(self.oval, 2 * wind_speed.get(), 0.1 * direction * wind_speed.get())
            if alpha <= 0.1:
                self.master.delete(self.oval)
                return
        else:
            self.master.delete(self.oval)
            return
        self.master.itemconfig(self.oval, fill=transparency(self.master, alpha))
        self.master.after(50, lambda: self.land(alpha, direction))
        alpha = 0.95 * alpha


class Lightning:
    def __init__(self, strength, x, y, slant=0, branch=False, branched=0, master=None):
        self.master = master
        self.path = [[x, y]]

        for i in range(1, 1000):

            radius = 5 * random()
            angle = ((120 * random() - 60) + 20 * slant) * pi / 180
            x_new, y_new = self.rotate(self.path[i - 1][0], self.path[i - 1][1], radius, angle)
            self.path.append([x_new, y_new])

            if branching.get():
                branch_slant = choice([-1.5, -1, 1, 1.5])

                if not branch and random() < 0.075 and y_new < 175:
                    Lightning(strength / 2, x_new, y_new, slant + branch_slant, True, 0, self.master)

                if branch:
                    if strength >= 1:
                        if 1000 * random() < len(self.path):
                            Lightning(strength - strength / 5, x_new, y_new, slant - branch_slant, True, branched + 1, self.master)
                            Lightning(strength - strength / 2, x_new, y_new, slant + branch_slant, True, 0, self.master)
                            break
                        elif random() < 0.05:
                            strength -= strength / 5
                    elif 5000 * random() < 1 + 4 * len(self.path):
                        break

            if y_new > 350 and temperature.get() > -75:
                Reflection(x_new - 5, y_new + 3, 0, strength, slant, self.master)
                break

        alpha = abs(-(exp(-strength) - 1))
        self.bolt = self.master.create_line(self.path, fill=transparency(self.master, alpha), width=strength, smooth=True)
        self.master.after(50, lambda: self.fade(alpha - 0.3 / (strength + 1)))

    def fade(self, alpha):
        if alpha <= 0.1:
            self.master.delete(self.bolt)
            return
        self.master.itemconfig(self.bolt, fill=transparency(self.master, alpha))
        self.master.after(75, lambda: self.fade(alpha))
        alpha = 0.75 * alpha

    def rotate(self, x, y, radius, angle):
        x_prime = - radius * sin(angle)
        y_prime = radius * cos(angle)
        return x + x_prime, y + y_prime


class Reflection:
    def __init__(self, x, y, count, strength, slant, master=None):
        self.master = master
        self.total_ref = 40

        alpha = 0.4 * (strength + 10) / 16 * (self.total_ref - count / 2) / self.total_ref
        opacity = transparency(self.master, alpha)

        self.reflection = self.master.create_line(0, 0, min(20, 4 * strength) + 0.3 * count, 0, fill=opacity, width=min(4, strength))
        self.master.move(self.reflection, x - (0.5 * slant * count) + count * (random() - 0.5), y + 4 * count)
        self.fade(alpha, 0)

        if count < self.total_ref:
            count += 1
            Reflection(x, y, count, strength, slant, self.master)

    def fade(self, alpha, frame):
        if frame > 4:
            self.master.delete(self.reflection)
            return
        self.master.itemconfig(self.reflection, fill=transparency(self.master, alpha))
        self.master.after(100, lambda: self.fade(alpha * 0.9, frame + 1))


class Steam:
    def __init__(self, x, y, size, alpha, count, master=None):
        self.master = master
        self.steam = self.master.create_oval(0, 0, size, size,
                                             fill=transparency(self.master, max(alpha, brightness.get() / 1000)),
                                             outline="", tags='steam')
        self.master.move(self.steam, x, y)
        self.master.tag_lower(self.steam)
        self.master.tag_raise(self.steam, 'steam')
        self.fade(alpha, 0)

        if count < 20 * random() + 30:
            self.master.after(50, lambda: Steam(x + 0.2 * size * (random() - 0.7) + 0.3 * wind_speed.get(),
                                                y - (2 * random() + 3) - 0.2 * size, size + 9 * random()
                                                + 1, max(0.02, alpha * 0.8), count + 1, self.master))

    def fade(self, alpha, frame):
        if frame > 50:
            self.master.delete(self.steam)
            return
        self.master.itemconfig(self.steam, fill=transparency(self.master, max(alpha, brightness.get() / 1000)))
        self.master.after(20, lambda: self.fade(max(0.02, alpha * 0.95), frame + 1))


def transparency(c, alpha):

    background = int(c['background'].strip('gray')) / 100
    opacity = int((alpha + (1 - alpha) * background) * 100)
    opacity_string = 'gray' + str(opacity)
    return opacity_string


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == "__main__":

    def instructions():
        select_sound.play()
        root_2 = Toplevel()
        root_2.title("Instructions")
        Label(root_2, image=instructions_image).pack()

    def sound_system(prev_icategory=0, prev_wcategory=0, prev_tcategory=0):
        int_categories = (-100, -50, 0, 30, 70, 100)
        win_categories = (0, 5, 15, 35, 45)
        temp_categories = (-100, -75, 100)
        now_intensity = intensity.get()
        now_wind_speed = wind_speed.get()
        now_temperature = temperature.get()

        now_icategory = prev_icategory
        for i in range(len(int_categories) - 1):
            if int_categories[i] <= now_intensity < int_categories[i + 1]:
                now_icategory = i

        now_wcategory = prev_wcategory
        for i in range(len(win_categories) - 1):
            if win_categories[i] <= abs(now_wind_speed) < win_categories[i + 1]:
                now_wcategory = i

        now_tcategory = prev_tcategory
        for i in range(len(temp_categories) - 1):
            if temp_categories[i] <= now_temperature < temp_categories[i + 1]:
                now_tcategory = i

        if now_icategory != prev_icategory or now_tcategory != prev_tcategory:
            light_rain_sound.stop()
            medium_rain_sound.stop()
            heavy_rain_sound.stop()
            downpour_sound.stop()
            if now_temperature >= -75:
                if now_icategory == 0:
                    light_rain_sound.set_volume(0.5)
                    light_rain_sound.play(-1)
                elif now_icategory == 1:
                    light_rain_sound.set_volume(1)
                    light_rain_sound.play(-1)
                elif now_icategory == 2:
                    medium_rain_sound.set_volume(0.7)
                    medium_rain_sound.play(-1)
                elif now_icategory == 3:
                    heavy_rain_sound.set_volume(0.75)
                    heavy_rain_sound.play(-1)
                elif now_icategory == 4:
                    downpour_sound.play(-1)

        if now_wcategory != prev_wcategory:
            light_wind_sound.stop()
            strong_wind_sound.stop()
            if now_wcategory == 1:
                light_wind_sound.set_volume(0.5)
                light_wind_sound.play(-1)
            elif now_wcategory == 2:
                light_wind_sound.set_volume(1)
                light_wind_sound.play(-1)
            elif now_wcategory == 3:
                strong_wind_sound.set_volume(0.7)
                strong_wind_sound.play(-1)

        root.after(10, lambda: sound_system(now_icategory, now_wcategory, now_tcategory))

    def rain():
        inty = 0.002475 * (intensity.get() - 100) ** 2 + 1
        angle = wind_speed.get() * pi / 180
        layer = int(20 * random())
        if temperature.get() > -75:
            Droplet(layer, angle, canvas)
            if hurricane.get():
                for i in range(2):
                    Droplet(layer, angle, canvas)
        else:
            Snow(layer, angle, canvas)
            if hurricane.get():
                for i in range(2):
                    Snow(layer, angle, canvas)
        root.after(int(inty), rain)

    def storm(natural=True):
        global WIDTH
        inty = 0.002475 * (intensity.get() - 100) ** 2 + 1
        spawn_point = WIDTH * random()
        if natural:
            if thunderstorm.get():
                event = random()
            else:
                event = 0
        else:
            event = 0.2 * random() + 0.8
        if event > 0.8:
            if event < 0.92:
                strength = 2
                flash(25)
                thunder_sound.set_volume(0.3)
            elif event < 0.97:
                strength = 4
                flash(50)
                thunder_sound.set_volume(0.7)
            else:
                strength = 6
                flash(75)
                thunder_sound.set_volume(1)
            Lightning(strength, spawn_point, -100, 0, False, 0, canvas)
            thunder_sound.play()
        if natural:
            root.after(int(inty) * 500, lambda: storm(True))

    def boil():
        global WIDTH
        if temperature.get() > 75:
            angle = wind_speed.get() * pi / 180
            delta = abs(int(tan(angle) * WIDTH))
            Steam((WIDTH + 2 * delta) * random() - delta, 150 * random() + 350, 10 * random() + 10, 0.3, 0, canvas)
        root.after(200, boil)

    def flash(opacity):
        sky_flash()
        brightness.set(opacity)
        if opacity < 0.05:
            brightness.set(0)
            return
        root.after(30, lambda: flash(int(0.925 * opacity)))

    def sky_flash():
        global WIDTH
        flash = canvas.create_rectangle(0, 0, WIDTH, 350, fill=transparency(canvas, 0.01), outline="")
        canvas.tag_lower(flash)
        root.after(30, lambda: canvas.delete(flash))

    def whiten():
        alpha = int((abs(temperature.get()) * 0.2 + brightness.get() * 0.8) * abs(intensity.get() + 200) / 300)
        sky_alpha.set("gray" + str(alpha))
        canvas.configure(bg=sky_alpha.get())
        root.after(30, whiten)

    def cooldown():
        button.configure(state=DISABLED)
        storm(False)
        root.after(500, lambda: button.configure(state=NORMAL))

    def change(event):
        button.config(image=circle_glow_image)
        button.image = circle_glow_image

    def change_back(event):
        button.config(image=circle_image)
        button.image = circle_image

    def settings(id):
        select_sound.play()
        if id == 1:
            if branching.get():
                settings1.configure(image=off_image)
                settings1_label.configure(text="OFF", font=('HP Simplified', 12))
                branching.set(False)
            else:
                settings1.configure(image=on_image)
                settings1_label.configure(text="ON", font=('HP Simplified', 12, 'bold'))
                branching.set(True)
        elif id == 2:
            if thunderstorm.get():
                settings2.configure(image=off_image)
                settings2_label.configure(text="OFF", font=('HP Simplified', 12))
                thunderstorm.set(False)
            else:
                settings2.configure(image=on_image)
                settings2_label.configure(text="ON", font=('HP Simplified', 12, 'bold'))
                thunderstorm.set(True)
        elif id == 3:
            if hurricane.get():
                settings3.configure(image=off_image)
                settings3_label.configure(text="OFF", font=('HP Simplified', 12))
                hurricane.set(False)
            else:
                settings3.configure(image=on_image)
                settings3_label.configure(text="ON", font=('HP Simplified', 12, 'bold'))
                hurricane.set(True)


    root = Tk()
    root.title("The Rain Maker")
    root.configure(bg="gray0")
    left_frame = Frame(root)
    right_frame = Frame(root)
    right_frame.configure(bg='gray0')
    left_frame.grid(row=0, column=0, padx=(20, 0))
    right_frame.grid(row=0, column=1, padx=(0, 20))

    # image1 = PhotoImage(file=resource_path("light.png"))
    # image2 = PhotoImage(file=resource_path("heavy.png"))
    # image3 = PhotoImage(file=resource_path("left.png"))
    # image4 = PhotoImage(file=resource_path("right.png"))
    # image5 = PhotoImage(file=resource_path("cold.png"))
    # image6 = PhotoImage(file=resource_path("hot.png"))
    # circle_image = PhotoImage(file=resource_path("circle.png"))
    # circle_glow_image = PhotoImage(file=resource_path("circle_glow.png"))
    # off_image = PhotoImage(file=resource_path("off.png"))
    # on_image = PhotoImage(file=resource_path("on.png"))
    # sky_image = PhotoImage(file=resource_path("snowy.png"))
    # help_image = PhotoImage(file=resource_path("help.png"))
    # instructions_image = PhotoImage(file=resource_path("instructions.png"))

    image1 = PhotoImage(file="Pictures\\light.png")
    image2 = PhotoImage(file="Pictures\\heavy.png")
    image3 = PhotoImage(file="Pictures\\left.png")
    image4 = PhotoImage(file="Pictures\\right.png")
    image5 = PhotoImage(file="Pictures\\cold.png")
    image6 = PhotoImage(file="Pictures\\hot.png")
    circle_image = PhotoImage(file="Pictures\\circle.png")
    circle_glow_image = PhotoImage(file="Pictures\\circle_glow.png")
    off_image = PhotoImage(file="Pictures\\off.png")
    on_image = PhotoImage(file="Pictures\\on.png")
    sky_image = PhotoImage(file="Pictures\\snowy.png")
    help_image = PhotoImage(file="Pictures\\help.png")
    instructions_image = PhotoImage(file="Pictures\\instructions.png")

    intensity = IntVar()
    wind_speed = IntVar()
    temperature = IntVar()
    brightness = IntVar()
    brightness.set(0)
    branching = BooleanVar()
    branching.set(True)
    thunderstorm = BooleanVar()
    thunderstorm.set(False)
    hurricane = BooleanVar()
    hurricane.set(False)
    sky_alpha = StringVar()
    sky_alpha.set("gray0")

    canvas = Canvas(left_frame, width=WIDTH, height=HEIGHT)
    canvas.configure(bg=sky_alpha.get())
    canvas.create_image(0, 0, image=sky_image, anchor="nw")
    canvas.pack()

    # mixer.init()
    # light_rain_sound = mixer.Sound(resource_path("light_rain.mp3"))
    # medium_rain_sound = mixer.Sound(resource_path("medium_rain.mp3"))
    # heavy_rain_sound = mixer.Sound(resource_path("heavy_rain.mp3"))
    # downpour_sound = mixer.Sound(resource_path("downpour.mp3"))
    # thunder_sound = mixer.Sound(resource_path("thunder.mp3"))
    # light_wind_sound = mixer.Sound(resource_path("light_wind.mp3"))
    # strong_wind_sound = mixer.Sound(resource_path("strong_wind.mp3"))
    # select_sound = mixer.Sound(resource_path("select.mp3"))
    # sound_system()

    mixer.init()
    light_rain_sound = mixer.Sound("Sound Effects\\light_rain.mp3")
    medium_rain_sound = mixer.Sound("Sound Effects\\medium_rain.mp3")
    heavy_rain_sound = mixer.Sound("Sound Effects\\heavy_rain.mp3")
    downpour_sound = mixer.Sound("Sound Effects\\downpour.mp3")
    thunder_sound = mixer.Sound("Sound Effects\\thunder.mp3")
    light_wind_sound = mixer.Sound("Sound Effects\\light_wind.mp3")
    strong_wind_sound = mixer.Sound("Sound Effects\\strong_wind.mp3")
    select_sound = mixer.Sound("Sound Effects\\select.mp3")
    sound_system()

    title = Label(right_frame, text="The Rain Maker", font=('HP Simplified', 30), foreground='white',
                  background='black')
    instructions_top = Label(right_frame, text="\nDrag the sliders to control the rain.", font=('HP Simplified', 12),
                             foreground='white', background='black')
    intensity_slider = Scale(right_frame, from_=-100, to=100, length=250, sliderlength=10, orient='horizontal',
                             fg='white', troughcolor='gray50', background='black', activebackground='white',
                             highlightbackground='black',
                             showvalue=0, sliderrelief=FLAT, label="Intensity", font=('HP Simplified', 12),
                             variable=intensity)
    wind_speed_slider = Scale(right_frame, from_=-45, to=45, length=250, sliderlength=10, orient='horizontal',
                              fg='white', troughcolor='gray50', background='black', activebackground='white',
                              highlightbackground='black',
                              showvalue=0, sliderrelief=FLAT, label="Wind speed", font=('HP Simplified', 12),
                              variable=wind_speed)
    temperature_slider = Scale(right_frame, from_=-100, to=100, length=250, sliderlength=10, orient='horizontal',
                               fg='white', troughcolor='gray50', background='black', activebackground='white',
                               highlightbackground='black',
                               showvalue=0, sliderrelief=FLAT, label="Temperature", font=('HP Simplified', 12),
                               variable=temperature)
    settings1 = Button(right_frame, text="Forked lightning", foreground="white", font=('HP Simplified', 12),
                       image=on_image, background="black", border=0, activebackground="black", compound="right",
                       command=lambda: settings(1))
    settings2 = Button(right_frame, text="Natural lightning", foreground="white", font=('HP Simplified', 12),
                       image=off_image, background="black", border=0, activebackground="black", compound="right",
                       command=lambda: settings(2))
    settings3 = Button(right_frame, text="Super storm", foreground="white", font=('HP Simplified', 12),
                       image=off_image, background="black", border=0, activebackground="black", compound="right",
                       command=lambda: settings(3))
    settings1_label = Label(right_frame, text="OFF", foreground="white", background="black", font=('HP Simplified', 12))
    settings2_label = Label(right_frame, text="OFF", foreground="white", background="black", font=('HP Simplified', 12))
    settings3_label = Label(right_frame, text="OFF", foreground="white", background="black", font=('HP Simplified', 12))
    button = Button(right_frame, image=circle_image, background="black", activebackground="black", border=0,
                    command=cooldown)
    button.bind("<Enter>", change)
    button.bind("<Leave>", change_back)
    instructions_bottom = Label(right_frame, text="\nClick the button above to summon lightning.\n",
                                font=('HP Simplified', 12), foreground='white', background='black')
    help_button = Button(right_frame, image=help_image, background='black', activebackground='black', border=0,
                         command=instructions)

    icon1 = Label(right_frame, image=image1, background='black')
    icon2 = Label(right_frame, image=image2, background='black')
    icon3 = Label(right_frame, image=image3, background='black')
    icon4 = Label(right_frame, image=image4, background='black')
    icon5 = Label(right_frame, image=image5, background='black')
    icon6 = Label(right_frame, image=image6, background='black')

    title.grid(row=0, column=0, columnspan=10, pady=(20, 0))
    instructions_top.grid(row=1, column=0, columnspan=10)
    intensity_slider.grid(row=2, rowspan=2, column=1, columnspan=8, padx=0, pady=(20, 5))
    wind_speed_slider.grid(row=4, rowspan=2, column=1,  columnspan=8, padx=0, pady=5)
    temperature_slider.grid(row=6, rowspan=2, column=1,  columnspan=8, padx=0, pady=(5, 20))
    icon1.grid(row=3, column=0, padx=(20, 0))
    icon2.grid(row=3, column=9, padx=(0, 5))
    icon3.grid(row=5, column=0, padx=(20, 0))
    icon4.grid(row=5, column=9, padx=(0, 5))
    icon5.grid(row=7, column=0, padx=(20, 0))
    icon6.grid(row=7, column=9, padx=(0, 5))
    button.grid(row=8, rowspan=5, column=0, columnspan=4, padx=(20, 0), pady=(20, 0))
    settings1.grid(row=10, column=6, columnspan=3, sticky="e")
    settings2.grid(row=11, column=6, columnspan=3, sticky="e")
    settings3.grid(row=12, column=6, columnspan=3, sticky="e")
    settings1_label.grid(row=10, column=9, sticky="w")
    settings2_label.grid(row=11, column=9, sticky="w")
    settings3_label.grid(row=12, column=9, sticky="w")
    instructions_bottom.grid(row=13, rowspan=3, column=0, columnspan=9, padx=(20, 0), pady=(0, 20))
    help_button.grid(row=13, rowspan=2, column=9, columnspan=2)

    whiten()
    root.after(200, rain)
    root.after(200, boil)
    root.after(1000, storm)

    mainloop()
