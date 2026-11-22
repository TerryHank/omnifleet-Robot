"""One authoritative grid, transferred without resampling its cells."""
import base64, hashlib, zlib, struct
from rclpy.qos import QoSProfile, DurabilityPolicy
from rclpy.serialization import serialize_message, deserialize_message
from nav_msgs.msg import OccupancyGrid

QOS=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL)

def encode_grid(message):
    message.header.frame_id='fleet_map'
    raw=serialize_message(message)
    if len(raw)>16_000_000:raise ValueError('shared map exceeds 16 MB')
    p=message.info.origin.position;q=message.info.origin.orientation
    geometry=struct.pack('<fII7d',message.info.resolution,message.info.width,message.info.height,p.x,p.y,p.z,q.x,q.y,q.z,q.w)
    return {'sha256':hashlib.sha256(geometry+message.data.tobytes()).hexdigest(),
            'cdr_zlib':base64.b64encode(zlib.compress(raw,3)).decode(),
            'width':message.info.width,'height':message.info.height,'resolution':message.info.resolution,'frame_id':'fleet_map'}

def decode_grid(payload):
    decoder=zlib.decompressobj();raw=decoder.decompress(base64.b64decode(payload['cdr_zlib'],validate=True),16_000_001)
    if len(raw)>16_000_000 or not decoder.eof:raise ValueError('invalid or oversized shared map')
    message=deserialize_message(raw,OccupancyGrid)
    if message.header.frame_id!='fleet_map' or message.info.width*message.info.height!=len(message.data):raise ValueError('invalid grid geometry')
    if encode_grid(message)['sha256']!=payload['sha256']:raise ValueError('shared map checksum mismatch')
    return message
