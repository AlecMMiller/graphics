from vulkan import *

def debug_callback(*args):
    print(f"Validation layer: {args[5]} - {args[6]}")
    return 0

def make_debug_messenger(instance):
    createInfo = VkDebugReportCallbackCreateInfoEXT(
        sType=VK_STRUCTURE_TYPE_DEBUG_REPORT_CALLBACK_CREATE_INFO_EXT,
        pNext=None,
        flags=VK_DEBUG_REPORT_ERROR_BIT_EXT | VK_DEBUG_REPORT_WARNING_BIT_EXT,
        pfnCallback=debug_callback
    )

    creationFunction = vkGetInstanceProcAddr(instance, 'vkCreateDebugReportCallbackEXT')

    return creationFunction(instance, createInfo, None)
