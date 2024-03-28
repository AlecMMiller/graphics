from vulkan import *

class QueueFamilyIndices:
    def __init__(self) -> None:
        self.graphics_queue_family = None
        self.present_queue_family = None

    def is_complete(self):
        return self.graphics_queue_family is not None and self.present_queue_family is not None
    
class SwapChainSupportDetails:
    def __init__(self) -> None:
        self.capabilities = None
        self.formats = None
        self.present_modes = None

class SwapChainBundle:
    def __init__(self) -> None:
        self.swapchain = None
        self.images = None
        self.format = None
        self.extent = None

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

def get_queues(physicalDevice, device, instance, surface, debug):
    indices = find_queue_families(physicalDevice, instance, surface, debug)

    return [
        vkGetDeviceQueue(device, indices.graphics_queue_family, 0),
        vkGetDeviceQueue(device, indices.present_queue_family, 0)
    ]

def query_swapchain_support(physicalDevice, instance, surface, debug):
    details = SwapChainSupportDetails()

    getCapabilities = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceCapabilitiesKHR")
    getFormats = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceFormatsKHR")
    getPresentModes = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfacePresentModesKHR")

    details.capabilities = getCapabilities(physicalDevice, surface)
    details.formats = getFormats(physicalDevice, surface)
    details.present_modes = getPresentModes(physicalDevice, surface)

    if debug:
        print("Swap chain support details:")
        print(f"\tMin image count: {details.capabilities.minImageCount}")
        print(f"\tMax image count: {details.capabilities.maxImageCount}")

        print(f"\tCurrent extent: {details.capabilities.currentExtent.width}x{details.capabilities.currentExtent.height}")

    return details

def choose_swap_surface_format(formats, debug):
    for format in formats:
        if format.format == VK_FORMAT_B8G8R8A8_UNORM and format.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR:
            return format

    if debug:
        print("No suitable format found, using first available")

    return formats[0]

def choose_swap_present_mode(modes, debug):
    for mode in modes:
        if mode == VK_PRESENT_MODE_MAILBOX_KHR:
            return mode

    if debug:
        print("No suitable present mode found, using FIFO")

    return VK_PRESENT_MODE_FIFO_KHR

def choose_swap_extent(width, height, capabilities, debug):
    extent = VkExtent2D(width=width, height=height)

    extent.width = min(max(capabilities.minImageExtent.width, width), capabilities.maxImageExtent.width)
    extent.height = min(max(capabilities.minImageExtent.height, height), capabilities.maxImageExtent.height)

    if debug:
        print(f"Chosen extent: {extent.width}x{extent.height}")

    return extent

def create_swapchain(instance, physicalDevice, logicalDevice, surface, width, height, debug):
    support = query_swapchain_support(physicalDevice, instance, surface, debug)
    format = choose_swap_surface_format(support.formats, debug)
    present_mode = choose_swap_present_mode(support.present_modes, debug)
    extent = choose_swap_extent(width, height, support.capabilities, debug)
    image_count = support.capabilities.minImageCount + 1
    if support.capabilities.maxImageCount > 0 and image_count > support.capabilities.maxImageCount:
        image_count = support.capabilities.maxImageCount

    indices = find_queue_families(physicalDevice, instance, surface, debug)

    if indices.graphics_queue_family != indices.present_queue_family:
        imageSharingMode = VK_SHARING_MODE_CONCURRENT
        queueFamilyIndexCount = 2
        queueFamilyIndices = [indices.graphics_queue_family, indices.present_queue_family]
    else:
        imageSharingMode = VK_SHARING_MODE_EXCLUSIVE
        queueFamilyIndexCount = 0
        queueFamilyIndices = None

    create_info = VkSwapchainCreateInfoKHR(
        surface=surface,
        minImageCount=image_count,
        imageFormat=format.format,
        imageColorSpace=format.colorSpace,
        imageExtent=extent,
        imageArrayLayers=1,
        imageUsage=VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
        imageSharingMode=imageSharingMode,
        queueFamilyIndexCount=queueFamilyIndexCount,
        pQueueFamilyIndices=queueFamilyIndices,
        preTransform=support.capabilities.currentTransform,
        compositeAlpha=VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
        presentMode=present_mode,
        clipped=VK_TRUE,
        oldSwapchain=None
    )

    bundle = SwapChainBundle()

    vkSwapchainKHR = vkGetDeviceProcAddr(logicalDevice, "vkCreateSwapchainKHR")
    bundle.swapchain = vkSwapchainKHR(logicalDevice, create_info, None)
    vkGetSwapchainImagesKHR = vkGetDeviceProcAddr(logicalDevice, "vkGetSwapchainImagesKHR")
    bundle.images = vkGetSwapchainImagesKHR(logicalDevice, bundle.swapchain)

    bundle.format = format.format
    bundle.extent = extent

    return bundle
