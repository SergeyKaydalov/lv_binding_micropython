# A simple test for Linux Frame Buffer
# Registers FB display and mouse evdev and shows line cursor
# then shows a button on screen.

import lvgl as lv
from lv_utils import event_loop
import evdev

lv.init()

# Register FB display driver

event_loop = event_loop()
disp = lv.linux_fbdev_create()
lv.linux_fbdev_set_file(disp, "/dev/fb0")

# Register mouse device and crosshair cursor


#mouse = evdev.mouse_indev(lv.screen_active())

# Create a screen and a button

style = lv.style_t()
style.init()
style.set_bg_color(lv.palette_main(lv.PALETTE.DEEP_ORANGE));
#style.set_bg_color(lv.color_make(56,67,20))
#style.set_text_font(lv.font_unscii_8)

btn = lv.button(lv.screen_active())
btn.add_style(style, lv.PART.MAIN)
btn.align(lv.ALIGN.CENTER, 0, 0)
label = lv.label(btn)
label.set_text("Hello World!")
while True:
    pass

