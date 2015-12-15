Rossion
=======

Rossion is a fast and simple session module for tornado app. It is distributed
as a single file module and has dependencies on JUST `pylibmc <http://sendapatch.se/projects/pylibmc/index.html>`_.

Simple usage
------------

Here is a simple session supported example Tornado based web app for Rossion.

.. code-block:: python

    import tornado.ioloop
    import tornado.web
    import rossion.SessionMixin
    import pylibmc

    class MainHandler(tornado.web.RequestHandler, rossion.SessionMixin):
        def get_current_user(self):
            return self.session.get('user')

        def get(self):
            self.write("Hello, %s" % (self.current_user))

        def post(self):
            self.session['user'] = "Gromash"
            self.finish()

    def make_app():
        return tornado.web.Application([
            (r"/", MainHandler),
        ], engine="memcached", storage=self.__mc())

    def __mc(self):
        return pylibmc.Client([127.0.0.1:11211], binary=True,
                behaviors={'no_block': True, 'tcp_nodelay': True,
                'ketama': True})

    if __name__ == "__main__":
        app = make_app()
        app.listen(8888)
        tornado.ioloop.IOLoop.current().start()

Or use ``engine='memory', storage={}`` instead of memcached backend session.

Download and install
--------------------

Install the latest stable release with ``pip install rossion`` or download
`rossion.py` into your project directory with `pylibmc` preinstalled.
