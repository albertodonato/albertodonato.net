====================
Open source projects
====================

:slug: projects
:nav_title: Projects
:index: 1


I maintain a few open source personal projects, with different levels of
activity.

All of them are available on my `GitHub profile`_, below are the main ones.


----------------
query-exporter__
----------------

Prometheus exporter that allows ingesting results from SQL query as
metrics.

Supports multiple database engines at the same time (via ``SQLAlchemy``),
scheduled and parametric queries.

Built on top of ``prometheus-aioexporter``.


------------------------
prometheus-aioexporter__
------------------------

Simple and opinionated ``asyncio``-based Python library to build Prometheus
exporters.

It provides a boilerplate-free way base class for the exporter script, metrics
declaration and http/https handling, just add the logic for updating metrics.


.. __: https://github.com/albertodonato/query-exporter
.. __: https://github.com/albertodonato/prometheus-aioexporter
.. _`GitHub profile`: https://github.com/albertodonato
