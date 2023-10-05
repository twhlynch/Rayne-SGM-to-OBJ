import * as THREE from "three";

class SGMLoader extends THREE.Loader {
    constructor(manager) {
        super(manager);
    }

    load(url, onLoad, onProgress, onError) {
        const loader = new THREE.FileLoader(this.manager);
        loader.setPath(this.path);
        loader.setResponseType("arraybuffer");

        loader.load(url, (data) => {
            onLoad(this.parse(data));
        }, onProgress, onError);
    }

    parse(data) {
        console.log(data);
        const meshes = [];
        const materials = [];

        const version = new DataView(data, 0, 5).getUint32(0, true);
        console.log("Version:", version);

        const numMaterials = new DataView(data, 5, 1).getUint8(0);
        let offset = 6;
        console.log("NumMaterials:", numMaterials)
        for (let i = 0; i < numMaterials; i++) {
            const materialId = new DataView(data, offset, 1).getUint8(0);
            console.log("MaterialId:", materialId)
            const uvCount = new DataView(data, offset + 1, 1).getUint8(0);
            console.log("UVCount:", uvCount)
            const uvData = [];

            for (let j = 0; j < uvCount; j++) {
                const imageCount = new DataView(data, offset + 2, 1).getUint8(0);
                const images = [];

                for (let k = 0; k < imageCount; k++) {
                    const usageHint = new DataView(data, offset + 3, 1).getUint8(0);
                    const texnameLen = new DataView(data, offset + 4, 2).getUint16(0) - 1;
                    const texname = new TextDecoder().decode(
                        new Uint8Array(data.slice(offset + 6, offset + 6 + texnameLen))
                    );
                    offset += texnameLen + 6; // skip null terminator

                    images.push({texname, usageHint});
                }

                uvData.push(images);
            }

            const colorCount = new DataView(data, offset, 1).getUint8(0);
            const colors = [];

            for (let j = 0; j < colorCount; j++) {
                const colorId = new DataView(data, offset + 1, 1).getUint8(0);
                const color = [
                    new DataView(data, offset + 2, 4).getFloat32(0),
                    new DataView(data, offset + 6, 4).getFloat32(0),
                    new DataView(data, offset + 10, 4).getFloat32(0),
                    new DataView(data, offset + 14, 4).getFloat32(0)
                ];
                colors.push({colorId, color});

                offset += 18;
            }

            materials.push({materialId, uvData, colors});
        }

        const numMeshes = new DataView(data, offset, 1).getUint8(0);
        console.log("NumMeshes:", numMeshes);
        offset += 1;

        for (let i = 0; i < numMeshes; i++) {
            const vertices = [];
            const indices = [];
            const meshId = new DataView(data, offset, 1).getUint8(0);
            const materialId = new DataView(data, offset + 1, 1).getUint8(0);
            const vertexCount = new DataView(data, offset + 2, 4).getUint32(0);
            const uvCount = new DataView(data, offset + 6, 1).getUint8(0);
            const texdataCount = new DataView(data, offset + 7, 1).getUint8(0);
            const hasTangents = new DataView(data, offset + 8, 1).getUint8(0) === 1;
            const hasBones = new DataView(data, offset + 9, 1).getUint8(0) === 1;

            offset += 10;

            for (let j = 0; j < vertexCount; j++) {
                const position = [
                    new DataView(data, offset, 4).getFloat32(0),
                    new DataView(data, offset + 4, 4).getFloat32(0),
                    new DataView(data, offset + 8, 4).getFloat32(0)
                ];

                const normal = [
                    new DataView(data, offset + 12, 4).getFloat32(0),
                    new DataView(data, offset + 16, 4).getFloat32(0),
                    new DataView(data, offset + 20, 4).getFloat32(0)
                ];

                const uvs = [];

                for (let k = 0; k < uvCount; k++) {
                    const uv = [
                        new DataView(data, offset + 24 + k * 8, 4).getFloat32(0),
                        new DataView(data, offset + 28 + k * 8, 4).getFloat32(0)
                    ];
                    uvs.push(uv);
                }

                let color = null;

                if (texdataCount === 4) {
                    color = [
                        new DataView(data, offset + 24 + uvCount * 8, 4).getFloat32(0),
                        new DataView(data, offset + 28 + uvCount * 8, 4).getFloat32(0),
                        new DataView(data, offset + 32 + uvCount * 8, 4).getFloat32(0),
                        new DataView(data, offset + 36 + uvCount * 8, 4).getFloat32(0)
                    ];
                }

                let tangent = null;

                if (hasTangents) {
                    tangent = [
                        new DataView(data, offset + 24 + uvCount * 8 + ( color ? 16 : 0 ), 4).getFloat32(0),
                        new DataView(data, offset + 28 + uvCount * 8 + ( color ? 16 : 0 ), 4).getFloat32(0),
                        new DataView(data, offset + 32 + uvCount * 8 + ( color ? 16 : 0 ), 4).getFloat32(0),
                        new DataView(data, offset + 36 + uvCount * 8 + ( color ? 16 : 0 ), 4).getFloat32(0)
                    ];
                }

                let weights = null;
                let bones = null;

                if (hasBones) {
                    weights = [
                        new DataView(data, offset + 24 + uvCount * 8 + ( color ? 16 : 0 ) + ( hasTangents ? 16 : 0 ), 4).getFloat32(0),
                        new DataView(data, offset + 28 + uvCount * 8 + ( color ? 16 : 0 ) + ( hasTangents ? 16 : 0 ), 4).getFloat32(0),
                        new DataView(data, offset + 32 + uvCount * 8 + ( color ? 16 : 0 ) + ( hasTangents ? 16 : 0 ), 4).getFloat32(0),
                        new DataView(data, offset + 36 + uvCount * 8 + ( color ? 16 : 0 ) + ( hasTangents ? 16 : 0 ), 4).getFloat32(0)
                    ];

                    bones = [
                        new DataView(data, offset + 40 + uvCount * 8 + ( color ? 16 : 0 ) + ( hasTangents ? 16 : 0 ), 4).getFloat32(0),
                        new DataView(data, offset + 44 + uvCount * 8 + ( color ? 16 : 0 ) + ( hasTangents ? 16 : 0 ), 4).getFloat32(0),
                        new DataView(data, offset + 48 + uvCount * 8 + ( color ? 16 : 0 ) + ( hasTangents ? 16 : 0 ), 4).getFloat32(0),
                        new DataView(data, offset + 52 + uvCount * 8 + ( color ? 16 : 0 ) + ( hasTangents ? 16 : 0 ), 4).getFloat32(0)
                    ];
                }

                vertices.push({
                    position,
                    normal,
                    uvs,
                    color,
                    tangent,
                    weights,
                    bones
                });

                offset += 56 + uvCount * 8 + ( color ? 16 : 0 ) + ( hasTangents ? 16 : 0 ) + ( hasBones ? 32 : 0 );
            }

            const indexCount = new DataView(data, offset, 4).getUint32(0);
            offset += 4;

            const indexSize = new DataView(data, offset, 1).getUint8(0);
            offset += 1;

            for (let j = 0; j < indexCount; j++) {
                let index;

                if (indexSize === 4) {
                    index = new DataView(data, offset, 4).getUint32(0);
                    offset += 4;
                } else {
                    index = new DataView(data, offset, 2).getUint16(0);
                    offset += 2;
                }

                indices.push(index);
            }

            meshes.push({meshId, materialId, vertices, indices});
        }

        const threeMaterials = materials.map((materialData) => {
            const colorInfo = materialData.colors[0];
            const color = colorInfo.color || [1, 1, 1]; // Default to white
            const opacity = colorInfo.opacity || 1;

            const material = new THREE.MeshStandardMaterial({
                color: new THREE.Color(color[0], color[1], color[2]),
                opacity: opacity,
                transparent: opacity < 1.0
            });

            return material;
        });

        const threeMeshes = meshes.map((meshData) => {
            const geometry = new THREE.BufferGeometry();
            const vertices = [];
            const indices = [];

            meshData.vertices.forEach((v) => {
                vertices.push(v.position[0], v.position[1], v.position[2]);
            });

            meshData.indices.forEach((index) => {
                indices.push(index);
            });

            geometry.setAttribute( "position", new THREE.BufferAttribute(new Float32Array(vertices), 3) );
            geometry.setIndex(indices);

            const material = threeMaterials.find((mat, index) => meshData.materialId === index);

            const mesh = new THREE.Mesh(geometry, material);
            mesh.name = meshData.meshId;

            return mesh;
        });

        return threeMeshes;
    }
}

export {
    SGMLoader
};
