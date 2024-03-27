from vulkan import *
import sdl2

def get_surface_wayland(instance, wm_info, debug_mode = False):
    if debug_mode:
        print('Creating Wayland surface')
    vkCreateWaylandSurfaceKHR = vkGetInstanceProcAddr(instance, "vkCreateWaylandSurfaceKHR")
    surface_create = VkWaylandSurfaceCreateInfoKHR(
        sType=VK_STRUCTURE_TYPE_WAYLAND_SURFACE_CREATE_INFO_KHR,
        display=wm_info.info.wl.display,
        surface=wm_info.info.wl.surface,
        flags=0)
    return vkCreateWaylandSurfaceKHR(instance, surface_create, None)


def get_surface_win32(instance, wm_info, debug_mode = False):
    if debug_mode:
        print('Creating Win32 surface')
    vkCreateWin32SurfaceKHR = vkGetInstanceProcAddr(instance, "vkCreateWin32SurfaceKHR")
    surface_create = VkWin32SurfaceCreateInfoKHR(
        sType=VK_STRUCTURE_TYPE_WIN32_SURFACE_CREATE_INFO_KHR,
        hinstance=wm_info.info.win.hinstance,
        hwnd=wm_info.info.win.window,
        flags=0)
    return vkCreateWin32SurfaceKHR(instance, surface_create, None)

def get_surface_x11(instance, wm_info, debug_mode = False):
    if debug_mode:
        print('Creating X11 surface')
    vkCreateXlibSurfaceKHR = vkGetInstanceProcAddr(instance, "vkCreateXlibSurfaceKHR")
    surface_create = VkXlibSurfaceCreateInfoKHR(
        sType=VK_STRUCTURE_TYPE_XLIB_SURFACE_CREATE_INFO_KHR,
        dpy=wm_info.info.x11.display,
        window=wm_info.info.x11.window,
        flags=0)
    return vkCreateXlibSurfaceKHR(instance, surface_create, None)

def get_surface(instance, wm_info, debug_mode = False):
    if wm_info.subsystem == sdl2.SDL_SYSWM_WINDOWS:
        return get_surface_win32(instance, wm_info, debug_mode)
    elif wm_info.subsystem == sdl2.SDL_SYSWM_X11:
        return get_surface_x11(instance, wm_info, debug_mode)
    elif wm_info.subsystem == sdl2.SDL_SYSWM_WAYLAND:
        return get_surface_wayland(instance, wm_info, debug_mode)
    else:
        raise Exception("Platform not supported")
    