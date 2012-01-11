==============
Dashboard Mods
==============

Dashboard Mods is a set of ``DashboardModule``\ s for 
`django-admin-tools <http://pypi.python.org/pypi/django-admin-tools/>`_\ .

Changes
=======

**0.2** Updated to support Django Admin Tools 0.4.0

Installation
============

Using PIP::

	pip install dashboardmods
	
or download the app `here <http://pypi.python.org/pypi/dashboardmods/>`_ ::

	python setup.py install


Add **dashboardmods** to your settings **INSTALLED_APPS**::

    INSTALLED_APPS = (
        ...
        'dashboardmods',
        ...
    )


MemcacheDashboardModule
=======================

Displays a bar graph of memory usage, hit/miss ratio and uptime for each memcache server configured in Django's settings.

To enable, simply add::

	from dashboardmods import get_memcache_dash_modules

at the top of the page and in the ``__init__`` method add::

	self.children.extend(get_memcache_dash_modules())

If no memcache servers are configured, nothing happens.

VarnishDashboardModule
======================

Displays a bar graph of memory usage and hit/miss ratios for each Varnish server configured in ``VARNISH_MANAGEMENT_ADDRS``\ . It uses 
`python-varnish <http://pypi.python.org/pypi/django-varnish/>`_ for communication. See its docs for more information on setup and installation of ``python-varnish``\ .

To enable, simply add::

	from dashboardmods import get_varnish_dash_modules

at the top of the page and in the ``__init__`` method add::

	self.children.extend(get_varnish_dash_modules())

If no Varnish servers are configured, nothing happens.

RSSDashboardModule
==================

This is a model that allows the dynamic input of RSS feeds to appear as a ``DashboardModule``\ .

To enable, add ``dashboardmods`` to your ``INSTALLED_APPS`` and ``./manage.py syncdb``\ . 

Then add::

	from dashboardmods import get_rss_dash_modules

at the top of the page and in the ``__init__`` method add::

	self.children.extend(get_rss_dash_modules())

If no ``RSSDashboardModule`` records are entered, nothing happens. As soon as one is entered, the ``DashboardModule`` is immediately available.
