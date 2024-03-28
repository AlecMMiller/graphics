import sdl2
from vulkan import *
import ctypes
import instance
import logging
import device
import surface
import queue
import swapchain
class Engine:
    def __init__(self) -> None:
        self.debugMode = True

        self.width = 640
        self.height = 480

        if self.debugMode:
            print('Creating graphics engine')

        self.build_window()
        self.make_instance()
        self.make_debug_messenger()
        self.make_surface()
        self.make_device()

    def make_debug_messenger(self):
        if not self.debugMode:
            return
        
        self.debug_messenger = logging.make_debug_messenger(self.instance)

    def build_window(self):
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            raise Exception(sdl2.SDL_GetError())

        self.window = sdl2.SDL_CreateWindow(
        'Hello World'.encode('ascii'),
        sdl2.SDL_WINDOWPOS_UNDEFINED,
        sdl2.SDL_WINDOWPOS_UNDEFINED, self.width, self.height, 0)

        if not self.window:
            raise Exception(sdl2.SDL_GetError())

        self.wm_info = sdl2.SDL_SysWMinfo()
        sdl2.SDL_VERSION(self.wm_info.version)
        sdl2.SDL_GetWindowWMInfo(self.window, ctypes.byref(self.wm_info))

    def get_desired_extensions(self):
        extensions = [VK_KHR_SURFACE_EXTENSION_NAME]

        if self.wm_info == None:
            raise Exception('No window manager info')

        if self.wm_info.subsystem == sdl2.SDL_SYSWM_WINDOWS:
            extensions.append(VK_KHR_WIN32_SURFACE_EXTENSION_NAME)
        elif self.wm_info.subsystem == sdl2.SDL_SYSWM_X11:
            extensions.append(VK_KHR_XLIB_SURFACE_EXTENSION_NAME)
        elif self.wm_info.subsystem == sdl2.SDL_SYSWM_WAYLAND:
            extensions.append(VK_KHR_WAYLAND_SURFACE_EXTENSION_NAME)
        else:
            raise Exception("Platform not supported")

        if self.debugMode:
            extensions.append(VK_EXT_DEBUG_REPORT_EXTENSION_NAME)
        
        return extensions

    def make_instance(self):
        extensions = self.get_desired_extensions()
        self.instance = instance.make_instance('Foo', extensions, self.debugMode)

    def make_surface(self):
        self.surface = surface.get_surface(self.instance, self.wm_info, self.debugMode)

    def make_device(self):
        self.physical_device = device.choose_physical_device(self.instance, self.debugMode)
        self.device = device.create_logical_device(self.physical_device, self.instance, self.surface, self.debugMode)
        (self.graphics_queue, self.present_queue) = queue.get_queues(self.physical_device, self.device, self.instance, self.surface, self.debugMode)
        bundle = swapchain.create_swapchain(self.instance, self.physical_device, self.device, self.surface, self.width, self.height, self.debugMode)
        self.swapchain = bundle.swapchain
        self.swapchain_images = bundle.images
        self.format = bundle.format
        self.extent = bundle.extent

    def close(self):
        if self.debugMode:
            print('Closing graphics engine')

        swapchain_destroy_function = vkGetInstanceProcAddr(self.instance, 'vkDestroySwapchainKHR')
        swapchain_destroy_function(self.device, self.swapchain, None)

        vkDestroyDevice(self.device, None)

        surface_destroy_function = vkGetInstanceProcAddr(self.instance, 'vkDestroySurfaceKHR')
        surface_destroy_function(self.instance, self.surface, None)

        if self.debug_messenger:
            destroyFunction = vkGetInstanceProcAddr(self.instance, 'vkDestroyDebugReportCallbackEXT')
            destroyFunction(self.instance, self.debug_messenger, None)

        vkDestroyInstance(self.instance, None)

if __name__ == '__main__':
    engine = Engine()
    engine.close()