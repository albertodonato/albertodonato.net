=====================================
Twisted-like unit testing for asyncio
=====================================

:date: 2015-08-25
:category: development
:tags: asyncio, python, twisted, testing, unittest

Recently I've been porting some code for a personal project from Twisted_ to
the python3 builtin asyncio_ library. The change is not as drastic as it might
seem, since the two libraries share the same basic concepts (using just
different names, e.g. Future vs Deferred, loop vs reactor) and the asyncio
design is quite inspired by Twisted.

One thing I found is that adapting the code was actually easier and quicker
than changing unit tests.

Testing asynchronous code requires some setup, like managing the event loop,
creating callback chains to assert on results from asynchronous methods.
Twisted provides very nice facilities for this, which eliminate some of the
setup boilerplate and make test clearer to read and more concise.

Its ``trial`` test runner automatically manages setting up, starting and
stopping the reactor, and handles waiting for a ``Deferred`` when a test method
returns one.  This makes it possible to add callbacks to it, that assert on the
result of the asynchronous call. For example:

.. code:: python

  # Twisted
  def test_async_call(self):
      deferred = call_under_test()

      def check(result):
          self.assertEqual(result, 19)

      return deferred.addCallback(check)

will run the ``check`` callback when the deferred yields a result.
The same can be written more concisely using ``@inlineCallbacks``:

.. code:: python

  # Twisted
  @inlineCallbacks
  def test_async_call(self):
      result = yield call_under_test()
      self.assertEqual(result, 19)

which comes especially handy when multiple asynchronous calls are unused in a
single test (so you don't need to chain a lot of callbacks).

While moving my code to asyncio, I wanted to keep the same unit test style, but
unfortunately I didn't find much builtin support for it.  Looking at tests for
libraries using asyncio, I noticed most of them deal with the event loop
directly, running the method under test under it:

.. code:: python

  # asyncio
  def test_async_call(self):
      loop = asyncio.get_event_loop()
      result = loop.run_until_complete(call_under_test())
      self.assertEqual(result, 19)

That's fine if you're testing a single call, but it gets cumbersome when you
have multiple calls, possibly with depending on the result of the previous one,
or when an asynchronous function calls others. In this case there might not be
a single ``Future`` to wait for, and tests can easily become intricated.

Luckily, it wasn't to hard to implement a test behavior like the one provided
by Twisted with asyncio, so I created a LoopTestCase_ which provides an event
loop (derived from ``asyncio.test_utils.TestLoop``).  The testcase class
automatically wraps test methods so that if they return a ``Future`` or are
coroutines, the loop is run until until a result is returned.

In essence, the ``TestCase`` wraps the test method in its ``run()`` with a
method that run the original method, and makes the event loop wait for it if
it's asynchronous:

.. code:: python

  def run(self, result=None):
      test_method = getattr(self, self._testMethodName)
      setattr(self, self._testMethodName, self._wrap_async(test_method))
      return super().run(result=result)

  def _wrap_async(self, method):

      @wraps(method)
      def wrapper():
          result = method()
          if iscoroutine(result) or isinstance(result, Future):
             self.loop.run_until_complete(ensure_future(result, loop=self.loop))

      return wrapper


So the test case above simply becomes something like:

.. code:: python

  # asyncio
  def test_async_call(self):
      result = yield from call_under_test()
      self.assertEqual(result, 19)

Notice that there's no need to decorate the method as ``@coroutine`` (like with
Twisted's ``@inlineCallbacks``).


Controlling time
----------------

Both Twisted and asyncio provide methods scheduling function calls at a certain
time, or after a time delta. Testing code that use these functionalities
requires to be able to manipulate the event loop time manually, otherwise tests
would have to actually wait for time to pass, which could make them slow, and
possibly flaky.  Twisted provides ``twisted.internet.task.Clock`` which behaves
like the reactor, but provides an ``advance()`` method to move the time
forward.

.. code:: python

  # Twisted
  def test_call_later(self):
      calls = []
      clock = Clock()
      clock.callLater(5, calls.append, True)
      self.assertEqual(calls, [])
      clock.advance(5)
      self.assertEqual(calls, [True])

The ``asyncio.test_utils.TestLoop`` also provides an ``advance_time()`` method,
but this just moves the time forwards, so test code still needs to manually
schedule an event loop run to cause the scheduled function to be called.

To make this kind of test more concise, I enhanced the ``TestLoop`` used by
``LoopTestCase`` to do this automatically, via an ``advance()`` method.
The change is actually pretty simple:

.. code:: python

  def advance(self, advance):
      '''Advance the loop time and schedule a run.'''
      assert advance >= 0, 'Time advance must not be negative'
      self.advance_time(advance)
      self._run_once()

With this addition, the previous test looks pretty much the same with asyncio:

.. code:: python

  # asyncio
  def test_call_later(self):
      calls = []
      self.loop.call_later(5, calls.append, True)
      self.assertEqual(calls, [])
      self.loop.advance(5)
      self.assertEqual(calls, [True])


This becomes handier when dealing, for instance, with async code that is called
periodically, since in this case there isn't a single ``Future`` that can be waited for.

Let's consider, as an example, a class that executes a given function at periodic time intervals:

.. code:: python

  # asyncio
  def test_periodic(self):
      calls = []
      call = PeriodicCall(self.loop, calls.append, True)

      call.start(5)
      self.assertEqual(calls, [True])
      self.loop.advance(5)
      self.assertEqual(calls, [True, True])
      self.loop.advance(5)
      self.assertEqual(calls, [True, True, True])

``PeriodicCall`` (again from my ToolRack_ library) is basically a port of
Twisted's ``LoopingCall`` to asyncio. The ``start()`` method calls the function
and schedules the next execution after the specified time.


.. _Twisted: https://twistedmatrix.com/
.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _LoopTestCase: https://github.com/albertodonato/toolrack/blob/master/toolrack/testing/async.py
.. _ToolRack: https://github.com/albertodonato/toolrack
