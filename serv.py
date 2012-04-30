#!/usr/bin/python

from flotype.bridge import Bridge

# XXX:
# - Don't send a computed chunk to the client that computed it.

class DRay(object):
    def __init__(self, pixels):
        self.tick = 0
        self.pixels = pixels
        self.workers = []
        self.nr_scheduled = 0
        self.nr_completed = 0

    def canvas_chunks(self, nr):
        frac = 1.0 / nr
        kdelta = frac * self.pixels
        for k in range(nr):
            k0 = k * kdelta
            kf = k0 + kdelta
            yield map(int, (k0, kf))

    def join(self, worker, chan_handler, callback):
        '''
        - worker(tick, k0, kf, on_done)
        Server asks a client to process a chunk.
        - chan_handler.update(tick, buffer, k0, kf)
        Client asks other clients to update their buffers.
        '''
        def join_callback(channel, name):
            self.workers.append(worker)
            callback(channel, name)

        bridge.join_channel('dray', chan_handler, join_callback)
        
    def get_chunk(self):
        if self.nr_completed < self.nr_scheduled or len(self.workers) == 0:
            print('get_chunk: Jobs remain outstanding.')
            return
        
        print('New tick.')

        self.tick += 1
        self.nr_scheduled = len(self.workers)
        self.nr_completed = 0
        work = self.canvas_chunks(self.nr_scheduled)

        def on_done():
            self.nr_completed += 1
            print('Status = %f%%' % (self.nr_completed / self.nr_scheduled))

        for (i, (k0, kf)) in enumerate(work):
            print((k0, kf))
            self.workers[i](self.tick, k0, kf, on_done)
        
        print('Ticked once.')

if __name__ == '__main__':
    dray = DRay(800 * 600)
    bridge = Bridge(api_key='abcdefgh')
    bridge.publish_service('dray', dray)
    bridge.connect()
