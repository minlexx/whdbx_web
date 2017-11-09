import cherrypy
import cherrypy.lib.sessions

import redis


class WhdbxRedisSession(cherrypy.lib.sessions.Session):
    def __init__(self, id=None, **kwargs):
        """
        Called by internals of CherryPy
        :param id:
        :param kwargs: Redis backend supports the following parameters:
            'host' - where redis server runs, optional (localhost)
            'port' - port to connect to, optional (6379)
            'db' - Redis database number, optional (0)
        """
        # The 'db' arg is required for redis sessions.
        self.redis_db = 0
        self.redis_host = 'localhost'
        self.redis_port = 6379
        if 'host' in kwargs:
            self.redis_host = kwargs['host']
        if 'port' in kwargs:
            self.redis_port = kwargs['port']
        if 'db' in kwargs:
            self.redis_db = kwargs['db']

        cherrypy.lib.sessions.Session.__init__(self, id=id, **kwargs)

        self._redis = redis.StrictRedis(self.redis_host, self.redis_port, self.redis_db)

