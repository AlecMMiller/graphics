import glfw
import glfw.GLFW as GLFW_CONSTANTS

import vulkan
import instance

class Engine:
    def __init__(self) -> None:
        self.debugMode = True

        self.width = 640
        self.height = 480

        if self.debugMode:
            print('Creating graphics engine')

        self.build_glfw_window()
        self.make_instance()

    def build_glfw_window(self):
        glfw.init()

        glfw.window_hint(GLFW_CONSTANTS.GLFW_CLIENT_API, GLFW_CONSTANTS.GLFW_NO_API)

        glfw.window_hint(GLFW_CONSTANTS.GLFW_RESIZABLE, GLFW_CONSTANTS.GLFW_FALSE)

        self.window = glfw.create_window(self.width, self.height, 'Vulkan', None, None)

        if self.debugMode:
            if self.window is not None:
                print('Window created')
            else:
                print('Failed to create window')

    def make_instance(self):
        self.instance = instance.make_instance(self.debugMode, 'Foo')

    def close(self):
        if self.debugMode:
            print('Closing graphics engine')

        glfw.terminate()

if __name__ == '__main__':
    engine = Engine()
    engine.close()