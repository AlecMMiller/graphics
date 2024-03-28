def read_shader_src(filename):
    with open(filename, 'rb') as f:
        code = f.read()

    return code
