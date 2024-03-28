from vulkan import *
import queue

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

def create_swapchain(instance, physicalDevice, logicalDevice, surface, width, height, debug):
    support = query_swapchain_support(physicalDevice, instance, surface, debug)
    format = choose_swap_surface_format(support.formats, debug)
    present_mode = choose_swap_present_mode(support.present_modes, debug)
    extent = choose_swap_extent(width, height, support.capabilities, debug)
    image_count = support.capabilities.minImageCount + 1
    if support.capabilities.maxImageCount > 0 and image_count > support.capabilities.maxImageCount:
        image_count = support.capabilities.maxImageCount

    indices = queue.find_queue_families(physicalDevice, instance, surface, debug)

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
