"""Audit GLB structure, geometry, animation and embedded PNG texture estimates.

Counts are asset totals, not headset frame time or visible draw calls. RGBA memory
estimates are decoded precompression sizes, not measured GPU/VRAM consumption.
"""
import argparse
import json
import math
import struct
from pathlib import Path


def audit(path):
    data = Path(path).read_bytes()
    if len(data) < 12:
        raise ValueError('Truncated GLB header')
    magic, version, length = struct.unpack_from('<4sII', data)
    if magic != b'glTF' or version != 2 or length != len(data):
        raise ValueError('Invalid GLB header')
    offset, doc, binary = 12, None, None
    while offset < length:
        if length-offset < 8:
            raise ValueError('Truncated GLB chunk header')
        size, kind = struct.unpack_from('<II', data, offset)
        offset += 8
        if size % 4 or size > length-offset:
            raise ValueError('Truncated or unaligned GLB chunk')
        chunk = data[offset:offset+size]
        if kind == 0x4e4f534a:
            if doc is not None or offset != 20:
                raise ValueError('JSON must be the first and only JSON chunk')
            try:
                doc = json.loads(chunk)
            except (ValueError, UnicodeError) as exc:
                raise ValueError('Invalid glTF JSON') from exc
        elif kind == 0x004e4942:
            if binary is not None:
                raise ValueError('Duplicate binary chunk')
            binary = chunk
        offset += size
    if not isinstance(doc, dict):
        raise ValueError('Missing glTF JSON object')
    binary = binary or b''

    def finite_json(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('Non-finite JSON transform')
        if isinstance(value, dict):
            for item in value.values():
                finite_json(item)
        if isinstance(value, list):
            for item in value:
                finite_json(item)
    finite_json(doc)

    def integer(value, label):
        if type(value) is not int or value < 0:
            raise ValueError(f'Invalid {label}')
        return value

    def indexed(name, index):
        integer(index, name+' index')
        entries = doc.get(name, [])
        if index >= len(entries):
            raise ValueError(f'{name} index out of bounds')
        return entries[index]

    buffers = doc.get('buffers', [])
    if len(buffers)>1 or any('uri' in b for b in buffers):
        raise ValueError('External buffers cannot be audited')
    declared = integer(buffers[0]['byteLength'], 'buffer length') if buffers else 0
    if declared > len(binary) or len(binary)-declared > 3:
        raise ValueError('Binary buffer length mismatch')

    def view_bytes(index):
        view = indexed('bufferViews', index)
        if view.get('buffer', 0) != 0 or not buffers:
            raise ValueError('Invalid buffer view buffer')
        start = integer(view.get('byteOffset', 0), 'view offset')
        size = integer(view['byteLength'], 'view length')
        if start+size > declared:
            raise ValueError('Buffer view exceeds binary buffer')
        return view, binary[start:start+size]

    for index in range(len(doc.get('bufferViews', []))):
        view_bytes(index)
    widths = {'SCALAR':1, 'VEC2':2, 'VEC3':3, 'VEC4':4, 'MAT2':4, 'MAT3':9, 'MAT4':16}
    formats = {5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}

    def values(index):
        accessor = indexed('accessors', index)
        if 'sparse' in accessor or 'bufferView' not in accessor:
            raise ValueError('Sparse or implicit accessor needs explicit audit support')
        view, payload = view_bytes(accessor['bufferView'])
        component = accessor.get('componentType')
        kind = accessor.get('type')
        if component not in formats or kind not in widths:
            raise ValueError('Invalid accessor type')
        # Small-component matrix column padding requires a different decoder.
        if kind.startswith('MAT') and struct.calcsize(formats[component]) < 4:
            raise ValueError('Packed matrix accessor needs explicit audit support')
        fmt = '<'+formats[component]*widths[kind]
        element = struct.calcsize(fmt)
        stride = integer(view.get('byteStride', element), 'accessor stride')
        start = integer(accessor.get('byteOffset',0), 'accessor offset')
        count = integer(accessor['count'], 'accessor count')
        if stride < element or stride % struct.calcsize(formats[component]):
            raise ValueError('Invalid accessor stride')
        end = start+(count-1)*stride+element if count else start
        if end > len(payload):
            raise ValueError('Accessor exceeds buffer view')
        for i in range(count):
            yield struct.unpack_from(fmt, payload, start+i*stride)

    for i,a in enumerate(doc.get('accessors',[])):
        # Validate bounds of integer indices too, not only float vertex data.
        for sample in values(i):
            if not all(math.isfinite(v) for v in sample):
                raise ValueError(f'Non-finite data in accessor {i}')
    triangles = primitives = 0
    for mesh in doc.get('meshes',[]):
        for p in mesh['primitives']:
            primitives += 1
            if p.get('mode',4) == 4:
                accessor = p.get('indices',p['attributes']['POSITION'])
                triangles += indexed('accessors',accessor)['count']//3
    clips=[]
    for animation in doc.get('animations',[]):
        end=0
        for sampler in animation['samplers']:
            accessor=indexed('accessors',sampler['input'])
            if accessor['type']!='SCALAR' or accessor['componentType']!=5126:
                raise ValueError('Animation times must be float scalars')
            times=[v[0] for v in values(sampler['input'])]
            if not times or times[0]<0 or any(b<=a for a,b in zip(times,times[1:])):
                raise ValueError('Animation timestamps must be nonempty, nonnegative and strictly increasing')
            end=max(end,times[-1])
        clips.append({'name':animation.get('name',''), 'end_seconds':round(end,3),
                      'channels':len(animation['channels'])})

    images=[]
    total_pixels=base_bytes=mipped_bytes=0
    for index,item in enumerate(doc.get('images',[])):
        info={'index':index,'name':item.get('name',''),'mime_type':item.get('mimeType','')}
        if 'bufferView' not in item or item.get('mimeType')!='image/png':
            info['estimate_unavailable']='Only embedded PNG dimensions are audited'
            images.append(info)
            continue
        _,png=view_bytes(item['bufferView'])
        if len(png)<33 or png[:8]!=b'\x89PNG\r\n\x1a\n' or png[8:16]!=b'\x00\x00\x00\rIHDR':
            raise ValueError('Malformed embedded PNG header')
        width,height=struct.unpack_from('>II',png,16)
        if not width or not height or width>2147483647 or height>2147483647:
            raise ValueError('Invalid PNG dimensions')
        pixels=width*height
        mip_pixels=0
        w,h=width,height
        while True:
            mip_pixels+=w*h
            if w==1 and h==1:break
            w,h=max(1,w//2),max(1,h//2)
        info.update(width=width,height=height,pixels=pixels,
                    decoded_rgba8_base_bytes=pixels*4,
                    decoded_rgba8_full_mip_chain_bytes=mip_pixels*4)
        total_pixels+=pixels;base_bytes+=pixels*4;mipped_bytes+=mip_pixels*4
        images.append(info)
    return {'path':str(path),'bytes':len(data),'triangles':triangles,
            'mesh_primitives':primitives,'materials':len(doc.get('materials',[])),
            'textures':len(doc.get('textures',[])), 'images':images,
            'image_memory_estimate':{'basis':'Unique embedded PNG images decoded to RGBA8, precompression; not measured GPU memory. Mips estimated down to 1x1.',
                'complete':all('estimate_unavailable' not in image for image in images),
                'total_pixels':total_pixels,'rgba8_base_bytes':base_bytes,
                'rgba8_full_mip_chain_bytes':mipped_bytes},
            'skins':len(doc.get('skins',[])),'animations':clips,'finite_data':True}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('paths',nargs='+')
    args=p.parse_args()
    print(json.dumps([audit(path) for path in args.paths],indent=2))
