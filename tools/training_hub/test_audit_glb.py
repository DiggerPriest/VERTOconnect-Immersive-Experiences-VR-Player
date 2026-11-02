"""Malformed export regression tests; no Blender or third-party modules needed."""
import json
import math
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from audit_glb import audit


def glb(doc, binary=b''):
    doc=dict(doc)
    if binary and 'buffers' not in doc:doc['buffers']=[{'byteLength':len(binary)}]
    encoded=json.dumps(doc).encode();encoded+=b' '*(-len(encoded)%4)
    chunks=struct.pack('<II',len(encoded),0x4e4f534a)+encoded
    if binary:
        binary+=b'\0'*(-len(binary)%4)
        chunks+=struct.pack('<II',len(binary),0x004e4942)+binary
    return struct.pack('<4sII',b'glTF',2,len(chunks)+12)+chunks


def accessor_doc(count=2, component=5126, **overrides):
    accessor={'bufferView':0,'componentType':component,'type':'SCALAR','count':count}
    accessor.update(overrides)
    return {'asset':{'version':'2.0'},'bufferViews':[{'buffer':0,'byteLength':8}], 'accessors':[accessor]}


def png(width,height):
    def chunk(tag,payload):
        return struct.pack('>I',len(payload))+tag+payload+struct.pack('>I',zlib.crc32(tag+payload))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0'*(height*(1+width*4))))+chunk(b'IEND',b'')


class AuditTests(unittest.TestCase):
    def run_audit(self,data):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fixture.glb';path.write_bytes(data)
            return audit(path)

    def rejects(self,data,message):
        with self.assertRaisesRegex(ValueError,message):self.run_audit(data)

    def test_minimal_valid_glb(self):
        self.assertTrue(self.run_audit(glb({'asset':{'version':'2.0'}}))['finite_data'])

    def test_truncated_header(self):self.rejects(b'glTF','Truncated GLB header')
    def test_wrong_declared_length(self):self.rejects(glb({})+b'x','Invalid GLB header')
    def test_wrong_magic(self):self.rejects(b'bad!'+glb({})[4:],'Invalid GLB header')
    def test_truncated_chunk_header(self):
        self.rejects(struct.pack('<4sII',b'glTF',2,16)+b'xxxx','Truncated GLB chunk header')
    def test_truncated_chunk_payload(self):
        self.rejects(struct.pack('<4sIIII',b'glTF',2,24,12,0x4e4f534a)+b'{}  ','Truncated or unaligned')
    def test_bad_json(self):
        self.rejects(struct.pack('<4sIIII',b'glTF',2,24,4,0x4e4f534a)+b'nope','Invalid glTF JSON')
    def test_nonfinite_transform(self):self.rejects(glb({'nodes':[{'scale':[math.inf,1,1]}]}),'Non-finite JSON')
    def test_nonfinite_vertex(self):
        for number in [math.inf,-math.inf,math.nan]:
            with self.subTest(number=number):self.rejects(glb(accessor_doc(),struct.pack('<ff',0,number)),'Non-finite data')
    def test_accessor_overrun(self):self.rejects(glb(accessor_doc(count=3),b'\0'*8),'Accessor exceeds')
    def test_integer_accessor_overrun(self):self.rejects(glb(accessor_doc(count=3,component=5125),b'\0'*8),'Accessor exceeds')
    def test_negative_offset(self):self.rejects(glb(accessor_doc(byteOffset=-4),b'\0'*8),'Invalid accessor offset')
    def test_negative_count(self):self.rejects(glb(accessor_doc(count=-1),b'\0'*8),'Invalid accessor count')
    def test_bad_view_reference(self):self.rejects(glb(accessor_doc(bufferView=1),b'\0'*8),'index out of bounds')
    def test_view_exceeds_buffer(self):
        doc=accessor_doc();doc['bufferViews'][0]['byteLength']=12
        self.rejects(glb(doc,b'\0'*8),'Buffer view exceeds')
    def test_invalid_stride(self):
        doc=accessor_doc();doc['bufferViews'][0]['byteStride']=2
        self.rejects(glb(doc,b'\0'*8),'Invalid accessor stride')
    def test_valid_animation(self):
        doc=accessor_doc();doc['animations']=[{'name':'Loop','samplers':[{'input':0}],'channels':[]}]
        self.assertEqual(self.run_audit(glb(doc,struct.pack('<ff',0,20)))['animations'][0]['end_seconds'],20)
    def test_invalid_animation_times(self):
        for times in [(1,1),(2,1),(-1,2)]:
            with self.subTest(times=times):
                doc=accessor_doc();doc['animations']=[{'samplers':[{'input':0}],'channels':[]}]
                self.rejects(glb(doc,struct.pack('<ff',*times)),'Animation timestamps')
    def test_empty_animation_times(self):
        doc=accessor_doc(count=0);doc['animations']=[{'samplers':[{'input':0}],'channels':[]}]
        self.rejects(glb(doc,b'\0'*8),'Animation timestamps')
    def test_integer_animation_times(self):
        doc=accessor_doc(component=5125);doc['animations']=[{'samplers':[{'input':0}],'channels':[]}]
        self.rejects(glb(doc,b'\0'*8),'float scalars')
    def test_png_memory_unique_images_not_texture_references(self):
        binary=png(4,2)
        doc={'bufferViews':[{'buffer':0,'byteLength':len(binary)}],
             'images':[{'bufferView':0,'mimeType':'image/png'}],
             'textures':[{'source':0},{'source':0}]}
        result=self.run_audit(glb(doc,binary))
        self.assertEqual((result['images'][0]['width'],result['images'][0]['height']),(4,2))
        estimate=result['image_memory_estimate']
        self.assertEqual(estimate['total_pixels'],8)
        self.assertEqual(estimate['rgba8_base_bytes'],32)
        self.assertEqual(estimate['rgba8_full_mip_chain_bytes'],44) # 4x2 + 2x1 + 1x1
        self.assertTrue(estimate['complete'])
    def test_external_image_not_silently_estimated(self):
        result=self.run_audit(glb({'images':[{'uri':'texture.png'}]}))
        self.assertFalse(result['image_memory_estimate']['complete'])
    def test_bad_png_header(self):
        binary=b'not png!'+b'\0'*40
        self.rejects(glb({'bufferViews':[{'byteLength':len(binary)}],'images':[{'bufferView':0,'mimeType':'image/png'}]},binary),'Malformed embedded PNG')


if __name__=='__main__':unittest.main()
