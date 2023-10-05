import struct, os, argparse

def main():
    parser = argparse.ArgumentParser(description='Convert SGM to OBJ format')
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('output_file', nargs='?', type=str, help='path to output file')
    parser.add_argument('--texture', type=str, help='name of texture file if there is only one texture')
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    if args.output_file is None:
        output_file = f'{os.path.splitext(args.input_file)[0]}.obj'
    else:
        output_file = args.output_file
    texture = args.texture

    data = read_sgm(input_file)
    write_obj(data[0], data[1], output_file, texture)

def read_sgm(filename):
    with open(filename, "rb") as file:
        version = struct.unpack('<L B', file.read(5))
        print(version)

        num_materials = struct.unpack('<B', file.read(1))[0]
        materials = []
        for _ in range(num_materials):
            material_id = struct.unpack('<B', file.read(1))[0]
            uv_count = struct.unpack('<B', file.read(1))[0]
            uv_data = []
            for _ in range(uv_count):
                image_count = struct.unpack('<B', file.read(1))[0]
                images = []
                for _ in range(image_count):
                    usage_hint = struct.unpack('<B', file.read(1))[0]
                    texname_len = struct.unpack('<H', file.read(2))[0] - 1
                    texname = struct.unpack(f'<{texname_len}s', file.read(texname_len))[0].decode("utf_8")
                    file.seek(1, 1) # skip null terminator
                    images.append((texname, usage_hint))
                uv_data.append(images)
            color_count = struct.unpack('<B', file.read(1))[0]
            colors = []
            for _ in range(color_count):
                color_id = struct.unpack('<B', file.read(1))[0]
                color = struct.unpack('<ffff', file.read(16))
                colors.append((color, color_id))
            materials.append({
                'material_id': material_id,
                'uv_data': uv_data,
                'colors': colors
            })

        num_meshes = struct.unpack('<B', file.read(1))[0]
        meshes = [] 
        index_offset = 0 # for multiple meshes
        for _ in range(num_meshes):
            vertices = []
            indices = []
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

            index_offset += len(vertices)
            meshes.append({"mesh_id": mesh_id, "material_id": material_id, "vertices": vertices, "indices": indices})
            
    return [meshes, materials]

def write_obj(meshes, materials, filename, texturename):
    mtl_filename = f"{os.path.splitext(filename)[0]}.mtl"

    with open(mtl_filename, 'w') as mtl_file:
        for i,m in enumerate(materials):
            material_id = m["material_id"]
            mtl_file.write(f"newmtl {material_id}\n")
            color = m["colors"][0]
            r, g, b, a = color[0]
            mtl_file.write(f"Kd {r} {g} {b}\n")
            mtl_file.write(f"d {a}\n")
            if len(meshes[i]["vertices"][0][2]) > 0:
                if texturename is None:
                    for uv_images in m["uv_data"]:
                        for texname, _ in uv_images:
                            mtl_file.write(f"map_Kd {texname}\n")
                else:
                    mtl_file.write(f"map_Kd {texturename}\n")

    with open(filename, 'w') as f:
        f.write(f'mtllib {os.path.basename(mtl_filename)}\n')
        for (i,m) in enumerate(meshes):
            print(f"Working on mesh {i}")
            f.write(f"o {m['mesh_id']}\n")
            f.write(f'usemtl {m["material_id"]}\n')
            vertices = m["vertices"]
            indices = m["indices"]
            for v in vertices:
                f.write(f'v {v[0][0]} {v[0][1]} {v[0][2]}\n')
                f.write(f'vn {v[1][0]} {v[1][1]} {v[1][2]}\n')
                if v[2] is None or len(v[2]) == 0:
                    print(f"no uv: {v}")
                    f.write(f'vt 0 0\n')
                else:
                    f.write(f'vt {v[2][0][0]} {1-v[2][0][1]}\n')
            for i in range(0, len(indices), 3):
                if len(m["vertices"][0][2]) > 0:
                    f.write(f'f {indices[i] + 1}/{indices[i] + 1}/{indices[i] + 1} {indices[i + 1] + 1}/{indices[i + 1] + 1}/{indices[i + 1] + 1} {indices[i + 2] + 1}/{indices[i + 2] + 1}/{indices[i + 2] + 1}\n')
                else:
                    f.write(f'f {indices[i] + 1}//{indices[i] + 1} {indices[i + 1] + 1}//{indices[i + 1] + 1} {indices[i + 2] + 1}//{indices[i + 2] + 1}\n')

if __name__ == '__main__':
    main()