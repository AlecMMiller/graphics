from vulkan import *

class QueueFamilyIndices:
    def __init__(self) -> None:
        self.graphics_queue_family = None
        self.present_queue_family = None

    def is_complete(self):
        return self.graphics_queue_family is not None and self.present_queue_family is not None

def is_suitable_device(device, debug_mode):
    requested_extensions = [VK_KHR_SWAPCHAIN_EXTENSION_NAME]

    supported_extensions = [
        e.extensionName for e in vkEnumerateDeviceExtensionProperties(device, None)
    ]

    for extension in requested_extensions:
        if extension not in supported_extensions:
            return False
    
    return True

def choose_physical_device(instance, debug_mode):
    if debug_mode:
        print('Choosing physical device')

    devices = vkEnumeratePhysicalDevices(instance)

    if debug_mode:
        print(f"Found {len(devices)} devices")

    for device in devices:
        if debug_mode:
            log_device_properties(device)
        if is_suitable_device(device, debug_mode):
            return device
            
def log_device_properties(device):
    properties = vkGetPhysicalDeviceProperties(device)
    print(f"Device name: {properties.deviceName}")
    
    if properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU:
        print("Device type: Integrated GPU")
    elif properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU:
        print("Device type: Discrete GPU")
    elif properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_VIRTUAL_GPU:
        print("Device type: Virtual GPU")
    elif properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_CPU:
        print("Device type: CPU")
    else:
        print("Device type: Unknown")

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

def create_logical_device(physicalDevice, instance, surface, debug):
    indices = find_queue_families(physicalDevice, instance, surface, debug)
    unique_indices = [indices.graphics_queue_family]
    if indices.present_queue_family not in unique_indices:
        unique_indices.append(indices.present_queue_family)


    queueCreateInfos = []

    for index in unique_indices:
        queueCreateInfo = VkDeviceQueueCreateInfo(
            sType=VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            queueFamilyIndex=index,
            queueCount=1,
            pQueuePriorities=[1.0]
        )

        queueCreateInfos.append(queueCreateInfo)

    deviceFeatures = VkPhysicalDeviceFeatures()

    deviceCreateInfo = VkDeviceCreateInfo(
        sType=VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
        queueCreateInfoCount=len(queueCreateInfos),
        pQueueCreateInfos=queueCreateInfos,
        pEnabledFeatures=[deviceFeatures]
    )

    return vkCreateDevice(physicalDevice, deviceCreateInfo, None)

def get_queues(physicalDevice, device, instance, surface, debug):
    indices = find_queue_families(physicalDevice, instance, surface, debug)

    return [
        vkGetDeviceQueue(device, indices.graphics_queue_family, 0),
        vkGetDeviceQueue(device, indices.present_queue_family, 0)
    ]
