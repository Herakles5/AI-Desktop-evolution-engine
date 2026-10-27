#!/usr/bin/env python3
"""
CosmOS VPN Protocol - 26-Byte Packet Engine
============================================
Basiert auf Tobias' nativer C++ Implementierung in MeinOS/cosmos_vpn_crypto.h.
Ermöglicht AION, die proprietären 26-Byte Handshake- und Daten-Header
von CosmOS direkt in Python zu packen, zu verifizieren und zu entschlüsseln.

Header-Layout (exakt 26 Bytes):
- magic_start: 2 Bytes (0x2A, 0xC0)
- payload_size: 2 Bytes (uint16_t, Little-Endian)
- reserved: 11 Bytes
- text_vpn: 3 Bytes ("VPN")
- frame_id: 4 Bytes (uint32_t, Stream-Cipher-Synchronisation)
- checksum: 2 Bytes (Payload Sum)
- magic_end: 2 Bytes (0xEE, 0xFF)
Gesamt: 2 + 2 + 11 + 3 + 4 + 2 + 2 = 26 Bytes!
"""

import struct
from typing import Tuple, Optional


class CosmosVpnPacket26:
    MAGIC_START = bytes([0x2A, 0xC0])
    MAGIC_END = bytes([0xEE, 0xFF])
    VPN_MAGIC_TEXT = b"VPN"
    HEADER_SIZE = 26

    @classmethod
    def pack_data_header(cls, payload_size: int, frame_id: int, payload_checksum: int) -> bytes:
        """Packt den 26-Byte CosmOS Daten-Header."""
        reserved = bytes(11)
        header = (
            cls.MAGIC_START +
            struct.pack("<H", payload_size) +
            reserved +
            cls.VPN_MAGIC_TEXT +
            struct.pack("<I", frame_id) +
            struct.pack("<H", payload_checksum) +
            cls.MAGIC_END
        )
        assert len(header) == cls.HEADER_SIZE, f"Header muss exakt 26 Bytes sein, ist aber {len(header)}"
        return header

    @classmethod
    def unpack_data_header(cls, data: bytes) -> Optional[dict]:
        """Validiert und entpackt einen 26-Byte Header."""
        if len(data) < cls.HEADER_SIZE:
            return None
        if data[0:2] != cls.MAGIC_START or data[24:26] != cls.MAGIC_END:
            return None
        if data[15:18] != cls.VPN_MAGIC_TEXT:
            return None

        payload_size = struct.unpack("<H", data[2:4])[0]
        frame_id = struct.unpack("<I", data[18:22])[0]
        checksum = struct.unpack("<H", data[22:24])[0]

        return {
            "valid_26byte_packet": True,
            "payload_size": payload_size,
            "frame_id": frame_id,
            "checksum": checksum
        }

    @classmethod
    def calculate_checksum(cls, payload: bytes) -> int:
        """Berechnet die 16-Bit Payload-Summe aus cosmos_vpn_crypto.h."""
        return sum(payload) & 0xFFFF


if __name__ == "__main__":
    test_payload = b"Aion Nexus P2P Mesh Signal"
    cs = CosmosVpnPacket26.calculate_checksum(test_payload)
    hdr = CosmosVpnPacket26.pack_data_header(len(test_payload), frame_id=1337, payload_checksum=cs)
    
    print(f"Header-Laenge: {len(hdr)} Bytes (Soll: 26)")
    print(f"Header-Hex: {hdr.hex()}")
    parsed = CosmosVpnPacket26.unpack_data_header(hdr)
    print("Geparst:", parsed)
