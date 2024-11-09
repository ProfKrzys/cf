import datetime
from typing import TYPE_CHECKING, Dict, Union

if TYPE_CHECKING:
    from patchright._impl._browser_context import BrowserContext


class Clock:

    def __init__(self, browser_context: "BrowserContext") -> None:
        self._browser_context = browser_context
        self._loop = browser_context._loop
        self._dispatcher_fiber = browser_context._dispatcher_fiber

    async def install(self, time: Union[float, str, datetime.datetime] = None) -> None:
        await self._browser_context.install_inject_route()
        await self._browser_context._channel.send(
            "clockInstall", parse_time(time) if time is not None else {}
        )

    async def fast_forward(self, ticks: Union[int, str]) -> None:
        await self._browser_context._channel.send(
            "clockFastForward", parse_ticks(ticks)
        )

    async def pause_at(self, time: Union[float, str, datetime.datetime]) -> None:
        await self._browser_context._channel.send("clockPauseAt", parse_time(time))

    async def resume(self) -> None:
        await self._browser_context._channel.send("clockResume")

    async def run_for(self, ticks: Union[int, str]) -> None:
        await self._browser_context._channel.send("clockRunFor", parse_ticks(ticks))

    async def set_fixed_time(self, time: Union[float, str, datetime.datetime]) -> None:
        await self._browser_context._channel.send("clockSetFixedTime", parse_time(time))

    async def set_system_time(self, time: Union[float, str, datetime.datetime]) -> None:
        await self._browser_context._channel.send(
            "clockSetSystemTime", parse_time(time)
        )


def parse_time(
    time: Union[float, str, datetime.datetime]
) -> Dict[str, Union[int, str]]:
    if isinstance(time, (float, int)):
        return {"timeNumber": int(time * 1000)}
    if isinstance(time, str):
        return {"timeString": time}
    return {"timeNumber": int(time.timestamp() * 1000)}


def parse_ticks(ticks: Union[int, str]) -> Dict[str, Union[int, str]]:
    if isinstance(ticks, int):
        return {"ticksNumber": ticks}
    return {"ticksString": ticks}