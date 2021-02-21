import socket

from ._stream_async import AsyncSocketStream
from ._proto_socks4 import (
    ConnectRequest,
    ConnectResponse
)


class Socks4Proto:
    def __init__(self, stream: AsyncSocketStream,
                 dest_host, dest_port, user_id=None,
                 rdns=None):

        if rdns is None:
            rdns = False

        self._dest_host = dest_host
        self._dest_port = dest_port

        self._user_id = user_id
        self._rdns = rdns

        self._stream = stream

    async def negotiate(self):
        await self._socks_connect()

    async def _socks_connect(self):
        req = ConnectRequest(
            host=self._dest_host,
            port=self._dest_port,
            user_id=self._user_id,
            rdns=self._rdns
        )

        if req.need_resolve:
            _, addr = await self._stream.resolver.resolve(
                req.host,
                family=socket.AF_INET
            )
            req.set_resolved_host(addr)

        await self._stream.write_all(bytes(req))

        data = await self._stream.read_exact(8)

        res = ConnectResponse(data[:2])
        res.validate()
