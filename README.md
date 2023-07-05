# Rayne-SGM-to-OBJ
SGM to OBJ converter for Rayne SGM files

Made by reversing the SGM Exporter from [uberpixel/SGM-file-format](https://github.com/uberpixel/SGM-file-format)

## Command Line

`python sgm2obj.py [-h] input_file.sgm [output_file.obj]`

If no output file is provided, it will use the input file name and replace the extension with .obj and .mtl

## Blender Importer

The Plugin for 2.8x and higher can be found in `BlenderImport2_8x\io_import_sgm.py`<br>
I took the easy way out rather than importing the model myself, it converts to .obj/.mtl using the same functions and uses the built in .obj importer.<br>
This means there will be .obj and .mtl files left in the same directory as the imported .smg model.

# Info

## ~~Not converted~~
- Animations Excluded
- Only reads first color
- Doesn't use texture

## SGM Specification

<pre><code>############################################################
#Structure of exported mesh files (.sgm)
############################################################
#magic number - uint32 - 352658064
#version - uint8 - 3
#number of materials - uint8
#material id - uint8
#	number of uv sets - uint8
#		number of textures - uint8
#			texture type hint - uint8
#			filename length - uint16
#			filename - char*filename length
#	number of colors - uint8
#		color type hint - uint8
#		color rgba - float32*4
#
#number of meshs - uint8
#mesh id - uint8
#	used materials id - uint8
#	number of vertices - uint32
#	texcoord count - uint8
#	color channel count - uint8 usually 0 or 4
#	has tangents - uint8 0 if not, 1 otherwise
#	has bones - uint8 0 if not, 1 otherwise
#	interleaved vertex data - float32
#		- position, normal, uvN, color, tangents, weights, bone indices
#
#	number of indices - uint32
#	index size - uint8, usually 2 or 4 bytes
#	indices - index size
#
#<del>has animation - uint8 0 if not, 1 otherwise</del>
#	<del>animfilename length - uint16</del>
#	<del>animfilename - char*animfilename length</del>
</code></pre>

# Credit

- [Slin](https://github.com/Slin) for the original SGM Exporter and pointing out the fix for having multiple meshes.