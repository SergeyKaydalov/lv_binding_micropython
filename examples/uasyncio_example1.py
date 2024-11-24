##################################################################################################
#
# Example of LVGL with uasyncio event loop on unix and esp32 ports
#
# Running on Linux: (need micropython-dev for uasyncio):
#   ports/unix/micropython-dev -i lib/lv_bindings/examples/uasyncio_example1.py
#
# Important differences from non-uasyncio examples:
#
# - Import lv_utils and call lv_utils.event_loop (optional for ili9XXX)
# - Pass asynchronous=True
# - Call uasyncio.Loop.run_forever()
#
##################################################################################################

# Workaround for including frozen modules when running micropython with a script argument
# https://github.com/micropython/micropython/issues/6419
import usys as sys
sys.path.append('')

# Imports

from urandom import getrandbits, seed
from utime import ticks_us
from uasyncio import sleep, create_task, Loop, CancelledError
import lv_utils
import lvgl as lv


lv.init()

# Create event loop instance so it can process events
event_loop = lv_utils.event_loop(asynchronous=True)

seed(ticks_us())


##################################################################################################
# Display initialization
##################################################################################################

disp = lv.linux_fbdev_create()
lv.linux_fbdev_set_file(disp, "/dev/fb0")

##################################################################################################
# Stylized Message Box class
##################################################################################################

class MsgBox(lv.win):

    def drag_event_handler(self, e):
        self.move_foreground()
        indev = lv.indev_get_act()
        indev.get_vect(self.vect)
        x = self.get_x() + self.vect.x
        y = self.get_y() + self.vect.y
        self.set_pos(x, y)

    def __init__(self, parent):
        super().__init__(parent)
        self.vect = lv.point_t()

        self.set_size(100,80)
        self.add_title("Pop")
        msg_box_close_btn = self.add_button(lv.SYMBOL.CLOSE, 20)
        msg_box_close_btn.add_event(lambda e: self.close_msg_box(), lv.EVENT.RELEASED, None)

        header = self.get_header()
        header.set_style_bg_color(lv.color_hex3(0xFEE), lv.PART.MAIN)

        content = self.get_content()
        content.set_style_bg_color(lv.color_hex3(0xFFF), lv.PART.MAIN)

        self.set_style_border_width(4, lv.PART.MAIN)
        self.set_style_border_color(lv.color_hex3(0xF88), lv.PART.MAIN)
        self.set_style_shadow_color(lv.color_hex3(0x000), lv.PART.MAIN)
        self.set_style_shadow_opa(50, lv.PART.MAIN)
        self.set_style_shadow_width(20, lv.PART.MAIN)
        self.set_style_shadow_offset_x(10, lv.PART.MAIN)
        self.set_style_shadow_offset_y(10, lv.PART.MAIN)
        self.set_style_shadow_spread(0, lv.PART.MAIN)
        self.set_style_radius(10, lv.PART.MAIN)

        self.label = lv.label(content)

        for element in [content, header]:
            element.add_event(self.drag_event_handler, lv.EVENT.PRESSING, None)

        self.opened = True

    def is_open(self):
        return self.opened

    def close_msg_box(self):
        if self.is_open():
            self.anim = lv.anim_t()
            self.anim.init()
            self.anim.set_var(self)
            self.anim.set_time(500)
            self.anim.set_values(lv.OPA.COVER,lv.OPA.TRANSP)
            self.anim.set_custom_exec_cb(lambda obj, val:
                    self.set_style_opa(val, lv.PART.MAIN))
            self.anim.set_path_cb(lv.anim_t.path_ease_in)
            self.anim.set_ready_cb(lambda a: self.del_async())
            lv.anim_t.start(self.anim)
            self.opened = False

    def set_text(self, txt):

        # If the msg box is already closed, cancel the calling task
        if not self.is_open():
            raise CancelledError()

        self.label.set_text(txt)

##################################################################################################
# Async task
##################################################################################################

async def btn_event_task(obj=None, event=-1):

    # Create and position the a new msg box

    msg_box = MsgBox(scr)
    msg_box.set_pos(getrandbits(7), 50 + getrandbits(7))

    # Countdown

    for i in range(10, 0, -1):
        msg_box.set_text(str(i))
        await sleep(1)

    # Close the msg box

    msg_box.close_msg_box()

async def label_upd_task(obj):
    for i in range(10, 0, -1):
        obj.set_text(str(i))
        await sleep(1)


##################################################################################################
# Create objects and screen
##################################################################################################

rt_style = lv.style_t()
rt_style.set_bg_color(lv.color_make(80,90,100))
rt_style.set_text_font(lv.font_unscii_8)

scr = lv.screen_active()
scr.add_style(rt_style, lv.PART.MAIN)
#root = lv.obj(scr)
#root.add_style(rt_style, lv.PART.MAIN)
btn = lv.button(scr)
btn.align(lv.ALIGN.TOP_MID, 0, 10)
#btn.add_event_cb(lambda e: create_task(btn_event_task()), lv.EVENT.CLICKED, None)

label = lv.label(btn)
label.set_text('Click Me Again!')
Loop.create_task(label_upd_task(label))
##################################################################################################
# Start event loop
##################################################################################################

Loop.run_forever()


