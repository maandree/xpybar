# -*- python -*-

# A xpybar configuration example that demonstrates how you can
# write a configuration that lets you change the clock between
# local time and UTC using the keyboard.

# This example requires the package python-posix_ipc, and the
# example command requires the package cmdipc.

# Caveat: This example is only written to support local displays.
# If the host part of $DISPLAY contains a dot, this example will
# not work as expected.

# Caveat: The IPC objects are not cleaned up on exit.
# After exiting you may want to run
#     cmdipc -PQrk "/~${USER}.xpybar.$(echo "${DISPLAY}" | cut -d . -f 1)"

# To switch between UTC and localtime run the command
#     cmdipc -PQk "/~${USER}.xpybar.$(echo "${DISPLAY}" | cut -d . -f 1)" send -- clock
# You may want to add an executable file in your ~/.local/bin
# (which should you include in your $PATH) containing the code
#     #!/bin/sh
#     exec cmdipc -PQk "/~${USER}.xpybar.$(echo "${DISPLAY}" | cut -d . -f 1)" send -- clock
# You can then add a hotkey to xbindkeys running that command.

import time
import threading

from plugins.clock import Clock


OUTPUT, HEIGHT, YPOS, TOP = 0, 12, 24, True


local_clock = Clock(format = '%Y-(%m)%b-%d %T, %a w%V, %Z', utc = False, sync_to = Clock.SECONDS)
utc_clock   = Clock(format = '%Y-(%m)%b-%d %T, %a w%V, %Z', utc = True)

my_clock = local_clock


def mqueue_wait():
    import posix_ipc
    global my_clock
    qkey = '/~%s.xpybar.%s' % (os.environ['USER'], os.environ['DISPLAY'].split('.')[0])
    q = posix_ipc.MessageQueue(qkey, posix_ipc.O_CREAT, 0o600, 8, 128)
    while True:
        message = q.receive(None)[0].decode('utf-8', 'replace')
        if message == 'clock':
            my_clock = utc_clock if (my_clock is not utc_clock) else local_clock
            bar.invalidate() # Optional, just to force redrawing before the next second


start_ = start
def start():
    start_()
    async(mqueue_wait)
    async(lambda : local_clock.continuous_sync(lambda : bar.invalidate()))


def redraw():
    text = '%s' % my_clock.read()
    bar.clear()
    bar.draw_coloured_text(0, 10, 0, 2, text)

