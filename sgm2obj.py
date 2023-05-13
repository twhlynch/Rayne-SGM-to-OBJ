import struct, os, argparse

def main():
    parser = argparse.ArgumentParser(description='Convert SGM to OBJ format')
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('output_file', nargs='?', type=str, help='path to output file')
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    if args.output_file is None:
        output_file = f'{os.path.splitext(args.input_file)[0]}.obj'
    else:
        output_file = args.output_file

    data = read_sgm(input_file)
    write_obj(data[0], data[1], output_file)

def read_sgm(filename):
    with open(filename, "rb") as file:
        # Read the file format version number
        version = struct.unpack('<L B', file.read(5))
        print(version)
        # Read materials
        num_materials = struct.unpack('<B', file.read(1))[0]
        for _ in range(num_materials):
            material_id = struct.unpack('<B', file.read(1))[0]
            uv_count = struct.unpack('<B', file.read(1))[0]
            for _ in range(uv_count):
                image_count = struct.unpack('<B', file.read(1))[0]
                for _ in range(image_count):
                    usage_hint = struct.unpack('<B', file.read(1))[0]
                    texname_len = struct.unpack('<H', file.read(2))[0] - 1
                    texname = struct.unpack(f'<{texname_len}s', file.read(texname_len))[0].decode("utf_8")
                    file.seek(1, 1) # skip null terminator
            color_count = struct.unpack('<B', file.read(1))[0]
            for _ in range(color_count):
                color_id = struct.unpack('<B', file.read(1))[0]
                color = struct.unpack('<ffff', file.read(16))
        
        # Read meshes
        num_meshes = struct.unpack('<B', file.read(1))[0]
        vertices = []
        indices = [] 
        index_offset = 0 # for multiple meshes
        for _ in range(num_meshes):
            mesh_id = struct.unpack('<B', file.read(1))[0]
            material_id = struct.unpack('<B', file.read(1))[0]
            vertex_count = struct.unpack('<I', file.read(4))[0]
            uv_count = struct.unpack('<B', file.read(1))[0]
            texdata_count = struct.unpack('<B', file.read(1))[0]
            has_tangents = struct.unpack('<B', file.read(1))[0]
            has_bones = struct.unpack('<B', file.read(1))[0]
            for _ in range(vertex_count):
                position = struct.unpack('<fff', file.read(12))
                normal = struct.unpack('<fff', file.read(12))
                uvs = []
                for _ in range(uv_count):
                    uv = struct.unpack('<ff', file.read(8))
                    uvs.append(uv)
                color = None
                if texdata_count == 4:
                    color = struct.unpack('<ffff', file.read(16))
                tangent = None
                if has_tangents:
                    tangent = struct.unpack('<ffff', file.read(16))
                weights = None
                bones = None
                if has_bones:
                    weights = struct.unpack('<ffff', file.read(16))
                    bones = struct.unpack('<ffff', file.read(16))
                vertices.append((position, normal, uvs, color, tangent, weights, bones))
            index_count = struct.unpack('<I', file.read(4))[0]
            index_size = struct.unpack('<B', file.read(1))[0]
            for _ in range(index_count):
                if index_size == 4:
                    index = struct.unpack('<I', file.read(4))[0]
                else:
                    index = struct.unpack('<H', file.read(2))[0]
                indices.append(index + index_offset)
            index_offset = len(vertices)
    return [vertices, indices]

def write_obj(vertices, indices, filename):
    with open(filename, 'w') as f:
        for v in vertices:
            f.write(f'v {v[0][0]} {v[0][1]} {v[0][2]}\n')
            f.write(f'vn {v[1][0]} {v[1][1]} {v[1][2]}\n')
        for i in range(0, len(indices), 3):
            f.write(f'f {indices[i] + 1}//{indices[i] + 1} {indices[i + 1] + 1}//{indices[i + 1] + 1} {indices[i + 2] + 1}//{indices[i + 2] + 1}\n')

if __name__ == '__main__':
    main()