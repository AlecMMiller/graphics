from vulkan import *

class QueueFamilyIndices:
    def __init__(self) -> None:
        self.graphics_queue_family = None
        self.present_queue_family = None

    def is_complete(self):
        return self.graphics_queue_family is not None and self.present_queue_family is not None

def find_queue_families(device, instance, surface, debug):
    indices = QueueFamilyIndices()

    surface_support = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceSupportKHR")

    queue_families = vkGetPhysicalDeviceQueueFamilyProperties(device)

    if debug:
        print(f"Found {len(queue_families)} queue families")

    for i, queue_family in enumerate(queue_families):
        if queue_family.queueFlags & VK_QUEUE_GRAPHICS_BIT:
            indices.graphics_queue_family = i
            if debug:
                print(f"Using graphics queue family {i}")


        if surface_support(device, i, surface):
            indices.present_queue_family = i
            if debug:
                print(f"Using present queue family {i}")

        if indices.is_complete():
            break

    return indices

def get_queues(physicalDevice, device, instance, surface, debug):
    indices = find_queue_families(physicalDevice, instance, surface, debug)

    return [
        vkGetDeviceQueue(device, indices.graphics_queue_family, 0),
        vkGetDeviceQueue(device, indices.present_queue_family, 0)
    ]
