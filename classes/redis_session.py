import datetime
import pickle
import threading

# external modules
import cherrypy
import cherrypy.lib.sessions
import redis


class WhdbxRedisSession(cherrypy.lib.sessions.Session):

    locks = {}

    def __init__(self, id=None, **kwargs):
        """
        Called by internals of CherryPy
        :param id:
        :param kwargs: Redis backend supports the following parameters:
            'host' - where redis server runs, optional (localhost)
            'port' - port to connect to, optional (6379)
            'db' - Redis database number, optional (0)
        """
        self.redis_db = 0
        self.redis_host = 'localhost'
        self.redis_port = 6379
        # get params from kwargs
        if 'redis_host' in kwargs:
            self.redis_host = kwargs['redis_host']
        if 'redis_port' in kwargs:
            self.redis_port = kwargs['redis_port']
        if 'redis_db' in kwargs:
            self.redis_db = kwargs['redis_db']

        self._redis = redis.StrictRedis(self.redis_host, self.redis_port, self.redis_db)
        self.SESSION_PREFIX = 'cpsession_'

        cherrypy.lib.sessions.Session.__init__(self, id=id, **kwargs)

    @classmethod
    def setup(cls, **kwargs):
        """
        This should only be called once per process; this will be done
        automatically when using sessions.init (as the built-in Tool does).
        """
        for k, v in kwargs.items():
            setattr(cls, k, v)

    def clean_up(self):
        """Clean up expired sessions."""
        # actually, it needs to do nothing, because Redis removes old data automatically.
        pass

    def _exists(self):
        return self._redis.exists(self.SESSION_PREFIX + str(self.id))

    def _load(self):
        # return value is assigned to _data member in a base class
        val = self._redis.get(self.SESSION_PREFIX + str(self.id))
        if val is not None:
            return pickle.loads(val)  # should return a tuple of (data, expiration_time)
        return None

    def _save(self, expiration_time: datetime.datetime):
        """
        Saves session in DB
        :param expiration_time: literally it is datetime.now() + datetime.timedelta(seconds=session.timeout * 60)
        :return: None
        """
        expires_in_timedelta = expiration_time - datetime.datetime.now()
        expires_in_seconds = int(expires_in_timedelta.total_seconds())
        # cherrypy session base classs stores all info in _data member
        to_save = (self._data, expiration_time)  # save as tuple, as required by base class
        val = pickle.dumps(to_save)
        # Save pickled value in Redis, together with its expiration time
        # 'ex' sets an expire flag on key for ex seconds.
        self._redis.set(self.SESSION_PREFIX + str(self.id), val, ex=expires_in_seconds)

    def _delete(self):
        self._redis.delete(self.SESSION_PREFIX + str(self.id))

    def acquire_lock(self):
        """Acquire an exclusive lock on the currently-loaded session data."""
        self.locks.setdefault(self.id, threading.RLock()).acquire()
        self.locked = True

    def release_lock(self):
        """Release the lock on the currently-loaded session data."""
        self.locks[self.id].release()
        self.locked = False

    def __len__(self):
        """Return the number of active sessions."""
        saved_session_names = self._redis.keys(self.SESSION_PREFIX + '*')
        return len(saved_session_names)
