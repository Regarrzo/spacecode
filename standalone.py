# Here's shortest example which I could make.
import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

i = 0
def resized():
    global i
    i += 1
    print(f"Callback called {i} times.")

with dpg.window(tag="#main_window", label="tutorial"):
    dpg.add_button(label="Press me")
dpg.set_primary_window("#main_window", True)

with dpg.item_handler_registry(tag="#resize_handler"):
    dpg.add_item_resize_handler(callback=resized)
#Next two strings bind function resize to window and viewport resize events.
#Any of two may be commented as it will not affect on the bug     
dpg.bind_item_handler_registry("#main_window", "#resize_handler")
dpg.set_viewport_resize_callback(resized)

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()