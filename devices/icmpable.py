from icmplib import async_ping

from misc import memoize

from .device import Device, DeviceState


async def ping_address(address: str) -> bool:
    host = await async_ping(address,
                            count=1,
                            timeout=10,
                            privileged=True)
    return host.is_alive


class ICMPable(Device):
    def __init__(self,
                 *args,
                 ping_interval: float = 30,
                 should_icmp: bool = True,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.should_icmp = should_icmp
        self.intervals = { 'ping_interval': ping_interval }
        self.update_methods.append(('send_icmp', self.send_icmp))

    @memoize('ping_interval')
    async def send_icmp(self):
        if self.should_icmp:
            ip = getattr(self, 'primary_ip')
            if ip is not None:
                address = ip['address'].split('/')[0]
                await self.set_is_online(DeviceState.ON if await ping_address(address) else DeviceState.OFF)
            else:
                return False
    
    async def fetch(self):
        await super().fetch()
