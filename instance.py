from vulkan import *

def limit_supported_extensions(extensions):
    supported = vkEnumerateInstanceExtensionProperties(None)
    supported = [s.extensionName for s in supported]

    return [e for e in extensions if e in supported]

def limit_supported_layers(layers):
    supported = vkEnumerateInstanceLayerProperties()
    supported = [s.layerName for s in supported]

    return [l for l in layers if l in supported]

def get_layers():
    layers = vkEnumerateInstanceLayerProperties()
    layers = [l.layerName for l in layers]

    if 'VK_LAYER_KHRONOS_validation' in layers:
        return ['VK_LAYER_KHRONOS_validation']
    elif 'VK_LAYER_LUNARG_standard_validation' in layers:
        return ['VK_LAYER_LUNARG_standard_validation']
    else:
        return []

def make_instance(app_name: str, extensions: list, debug_mode: bool = False):
    version = VK_MAKE_VERSION(1, 0, 0)

    if debug_mode:
        print('Vulkan version:', VK_VERSION_MAJOR(version), VK_VERSION_MINOR(version), VK_VERSION_PATCH(version))

    app_info = VkApplicationInfo(
        sType=VK_STRUCTURE_TYPE_APPLICATION_INFO,
        pNext=None,
        pApplicationName=app_name.encode(),
        applicationVersion=version,
        pEngineName=b'No Engine',
        engineVersion=version,
        apiVersion=version
    )

    extensions = limit_supported_extensions(extensions)

    if debug_mode:
        print('Extensions:', extensions)

    layers = get_layers()
    layers = limit_supported_layers(layers)

    if debug_mode:
        print('Layers:', layers)

    create_info = VkInstanceCreateInfo(
        sType=VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
        pNext=None,
        flags=0,
        pApplicationInfo=app_info,
        enabledLayerCount=len(layers),
        ppEnabledLayerNames=layers,
        enabledExtensionCount=len(extensions),
        ppEnabledExtensionNames=extensions
    )

    try:
        return vkCreateInstance(create_info, None)
    except VkError as e:
        print(e)
        return None