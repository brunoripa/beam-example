import pickle
from google.appengine.ext import ndb


class ShardedCacheKey(object):
    """
    Cache wrapper to shard memcache requests across multiple keys.

    :param name: The key name
    :param shards: The number of shards to distribute keys over.
    """

    # Global state to store cycle counter, means you don't have to
    # worry about keeping `ShardedCacheKey` instances around.
    COUNTERS = defaultdict(lambda: -1)

    def __init__(self, name, shards=5):
        self.shards = shards
        self.name = name

    @classmethod
    def _reset(cls):
        """
        Reset method for tests.
        """
        cls.COUNTERS = defaultdict(lambda: -1)

    def next(self):
        """
        get the next counter
        """
        c = self.__class__.COUNTERS
        i = c[self.name] = (c[self.name] + 1) % self.shards
        return i

    def format(self, *args, **kwargs):
        return self.__class__(self.name.format(*args, **kwargs),
                              shards=self.shards)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_key(self, i=None):
        """
        Get the key name. Optionally takes the iteration we want
        the key for.
        """
        if i is None:
            i = self.next()
        return "%s:%s" % (self.name, i)

    @ndb.tasklet
    def set_async(self, value, time=0, min_compress_len=0,
                  namespace=None, context=None):
        """
        Sets the value of all shards.

        :param value: The value to set
        :param time: The age to persist the value
        :param namespace: Optional namespace
        :param context: A :py:`ndb.Context` instance.
        """
        context = context or ndb.get_context()
        yield [
            context.memcache_set(self.get_key(i),
                                 value,
                                 time,
                                 min_compress_len,
                                 namespace)
            for i in range(self.shards)]
        raise ndb.Return(None)

    def set(self, *args, **kwargs):
        """
        Synchronous version of :py:`set_async`.
        """
        return self.set_async(*args, **kwargs).get_result()

    def get_async(self, i=None, namespace=None, context=None):
        """
        Gets the value from cache.

        :param i: The shard to fetch the value from. A random one will be used
            if not provided.
        :param namespace: An optional namespace.
        :param context: A :py:`ndb.Context` instance.
        """
        context = context or ndb.get_context()
        k = self.get_key(i)
        return context.memcache_get(k, namespace=namespace)

    def get(self, *args, **kwargs):
        """
        Synchronous version of :py:`get_async`
        """
        return self.get_async(*args, **kwargs).get_result()

    @ndb.tasklet
    def delete_async(self, namespace=None, context=None):
        context = context or ndb.get_context()

        result = yield [context.memcache_delete(self.get_key(i))
                        for i in range(self.shards)]

        raise ndb.Return(all(result))


class DistributedCacheKey(object):
    """
    Distributes large cache items across multiple keys if necessary.
    """
    CHUNK_SIZE = 950000

    def __init__(self, key, context=None):
        self.ctx = context or ndb.get_context()
        self.client = memcache.Client()
        self.key = key

    def set_async(self, value, time=0):
        data = pickle.dumps(value)
        if len(data) >= self.CHUNK_SIZE:
            return self._set_multi(data, time)
        else:
            return self._set_single(data, time)

    def _set_multi(self, data, time):
        keys = []
        parts = []
        while data:
            chunk, data = data[:self.CHUNK_SIZE], data[self.CHUNK_SIZE:]

            # Generate some randomish keys. Should help prevent hotkeys
            keys.append("%s|%s" % (randint(0, 100000), self.key))
            parts.append(chunk)

        parts.append(('MULTI', keys[:]))
        keys.append(self.key)

        return self.client.set_multi_async(dict(zip(keys, parts)), time)

    def _set_single(self, data, time):
        return self.ctx.memcache_set(self.key, data, time)

    @ndb.tasklet
    def get_async(self):
        value = yield self.ctx.memcache_get(self.key)
        if isinstance(value, tuple) and value[0] == 'MULTI':
            value = yield self._get_multi(value[1])
        if value is not None:
            value = pickle.loads(value)
        raise ndb.Return(value)

    @ndb.tasklet
    def _get_multi(self, keys):
        values = yield self.client.get_multi_async(keys)

        comb = ''
        for k in keys:
            val = values.get(k, None)
            if val is None:
                raise ndb.Return(None)
            comb += val
        raise ndb.Return(comb)