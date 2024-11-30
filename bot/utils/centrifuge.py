import json
import zlib
from typing import Any, Dict
from zlib import decompress

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

from bot.utils import client_pb2


class ProtobufCodec:
    def encode_commands(self, commands):
        """Encode multiple command messages"""
        output = bytearray()
        for command in commands:
            proto_command = client_pb2.Command()
            for field, value in command.items():
                if isinstance(value, dict):
                    nested_field = getattr(proto_command, field)
                    for nested_key, nested_value in value.items():
                        setattr(nested_field, nested_key, nested_value)
                else:
                    setattr(proto_command, field, value)

            command_bytes = proto_command.SerializeToString()
            _EncodeVarint(output.extend, len(command_bytes))
            output.extend(command_bytes)

        return bytes(output)

    def decode_replies(self, buffer):
        """Decode multiple reply messages"""
        replies = []
        n = 0
        length = len(buffer)

        while n < length:
            msg_len, new_pos = _DecodeVarint32(buffer, n)
            n = new_pos
            msg_buf = buffer[n : n + msg_len]
            n += msg_len
            reply = client_pb2.Reply()
            reply.ParseFromString(msg_buf)
            replies.append(reply)

        return replies


def decode_message(binary_message) -> Dict[str, Any] | bytes | None:
    """Decode centrifuge-protobuf message"""
    codec = ProtobufCodec()

    replies = codec.decode_replies(binary_message)

    for reply in replies:
        if reply.push and reply.push.pub and reply.push.pub.data:
            if reply.push.channel == "event:message":
                decoded_data = reply.push.pub.data.decode()
                protobuf_message = {
                    "channel": reply.push.channel,
                    "data": json.loads(decoded_data),
                }
                return protobuf_message
            else:
                uncompressed_data = decompress(reply.push.pub.data, -zlib.MAX_WBITS)
                decoded_data = json.loads(uncompressed_data.decode())
                protobuf_message = {
                    "channel": reply.push.channel,
                    "data": decoded_data,
                }
                return protobuf_message
        elif reply.connect and reply.connect.data:
            return reply.connect.data


def encode_commands(commands_to_encode) -> bytes:
    """Encode multiple commands to centrifuge-protobuf"""
    codec = ProtobufCodec()
    encoded_commands = codec.encode_commands(commands_to_encode)
    return encoded_commands
