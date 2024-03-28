from vulkan import *
import queue

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

def create_logical_device(physicalDevice, instance, surface, debug):
    indices = queue.find_queue_families(physicalDevice, instance, surface, debug)
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

    deviceExtensions = [
        VK_KHR_SWAPCHAIN_EXTENSION_NAME
    ]

    deviceCreateInfo = VkDeviceCreateInfo(
        sType=VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
        queueCreateInfoCount=len(queueCreateInfos),
        pQueueCreateInfos=queueCreateInfos,
        pEnabledFeatures=[deviceFeatures],
        enabledExtensionCount=len(deviceExtensions),
        ppEnabledExtensionNames=deviceExtensions
    )

    return vkCreateDevice(physicalDevice, deviceCreateInfo, None)

