from admin_tools.dashboard.models import DashboardModule
from django.conf import settings

def format_bytes(bytes):
    """
    Format a bytes value into something more readable
    """
    bytes = float(bytes)
    if bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fGB' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fMB' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fKB' % kilobytes
    else:
        size = '%.2fB' % bytes
    return size

def format_seconds(s):
    """
    Format a seconds value into a human-readable form
    """
    years, s = divmod(s, 31556952)
    min, s = divmod(s, 60)
    h, min = divmod(min, 60)
    d, h = divmod(h, 24)
    return '%sy, %sd, %sh, %sm, %ss' % (years, d, h, min, s)


def format_graph(label, count, total, percent):
    """
    Creates an <li> element that becomes a percentage bar graph. Meant to be
    included within a <ul class="chartlist"></ul> element.
    """
    template = """<li><span class="label">%(label)s</span><span class="count">%(percent)s%%</span><span class="index" style="width: %(percent)s%%">(%(percent)s%%)</li>"""
    
    return template % {'label': label, 'count': count, 'total': total, 'percent': percent}


class MemcachedDashboardModule(DashboardModule):
    """
    Show some basic statistics for a memcache server
    """
    def __init__(self, server, stats, *args, **kwargs):
        super(MemcachedDashboardModule, self).__init__(*args, **kwargs)
        
        self.title = "Memcached Stats (%s v%s)" % (server.split(':')[0], stats['version'])
        
        bytes_used = format_bytes(int(stats['bytes']))
        bytes_available = format_bytes(int(stats['limit_maxbytes']))
        storage_pct = int((float(stats['bytes'])/float(stats['limit_maxbytes']))*100)
        
        misses = int(stats['get_misses'])
        total_requests = int(stats['cmd_get'])
        miss_pct = int((float(misses)/total_requests)*100)
        
        uptime = format_seconds(int(stats['uptime']))
        
        storage = {
            'label': 'Memory Usage',
            'count': bytes_used,
            'total': bytes_available,
            'percent': storage_pct,
        }
        miss_ratio = {
            'label': 'Cache Misses',
            'count': misses,
            'total': total_requests,
            'percent': miss_pct,
        }
        code = ['<ul class="chartlist">']
        code.append(format_graph(**storage))
        code.append(format_graph(**miss_ratio))
        code.append('</ul>')
        self.children.append("".join(code))
        self.children.append('<li><span class="label">Uptime: %s</span></li>' % uptime)
        self.template = "dashboard/modules/memcache.html"


class VarnishDashboardModule(DashboardModule):
    """
    Shows some basic stats of a varnish server
    """
    def __init__(self, server, stats, *args, **kwargs):
        super(VarnishDashboardModule, self).__init__(*args, **kwargs)
        
        self.title = "Varnish Stats (%s)" % server.split(":")[0]
        
        misses = stats['cache_misses']
        total_requests = stats['cache_hits'] + misses
        miss_pct = int((float(misses)/total_requests)*100)
        
        bytes_used = format_bytes(stats['bytes_allocated'])
        bytes_available = format_bytes(stats['bytes_free'])
        storage_pct = int((float(stats['bytes_allocated'])/stats['bytes_free'])*100)
        
        storage = {
            'label': 'Memory Usage',
            'count': bytes_used,
            'total': bytes_available,
            'percent': storage_pct,
        }
        miss_ratio = {
            'label': 'Cache Misses',
            'count': misses,
            'total': total_requests,
            'percent': miss_pct,
        }
        code = ['<ul class="chartlist">']
        code.append(format_graph(**storage))
        code.append(format_graph(**miss_ratio))
        code.append('</ul>')
        self.children.append("".join(code))
        self.template = "dashboard/modules/memcache.html"


def get_memcache_dash_modules():
    """
    Based on the settings in Django, attempt to create a MemcacheDashboardModule
    for every memcache server. 
    
    Returns a list of modules, or an empty list.
    
    In the __init__ method of your custom dashboard add: 
    
    self.children.extend(get_memcache_dash_modules())
    
    Note it says extend not append.
    """
    from django.core.cache import cache
    try:
        import memcache
        if not isinstance(cache._cache, memcache.Client):
            return []
        
        cache_stats = cache._cache.get_stats()
        server_modules = []
        for server, stats in cache_stats:
            server_modules.append(MemcachedDashboardModule(server, stats))
        return server_modules
    except (ImportError, AttributeError), e:
        return []

def get_varnish_dash_modules():
    """
    Using python-varnish and the Django settings, attempt to create a 
    VarnishDashboardModule for every varnish server. 
    
    Returns a list of modules, or an empty list.
    
    In the __init__ method of your custom dashboard add: 
    
    self.children.extend(get_varnish_dash_modules())
    
    Note it says extend not append.
    """
    from varnish import VarnishManager
    from django.conf import settings
    server_modules = []
    
    for server in getattr(settings,'VARNISH_MANAGEMENT_ADDRS', ()):
        try:
            manager = VarnishManager((server,))
            stats = manager.run('stats')[0][0]
            server_modules.append(VarnishDashboardModule(server, stats))
        except Exception,e:
            continue
    return server_modules

def get_rss_dash_modules():
    """
    Convert all RSSDashboarModule objects into FeedDashboardModules.
    
    Returns a list of modules, or an empty list.
    
    In the __init__ method of your custom dashboard add: 
    
    self.children.extend(get_rss_dash_modules())
    
    Note it says extend not append.
    """
    from models import RSSDashboardModule
    from admin_tools.dashboard.models import FeedDashboardModule
    modules = []
    for feed in RSSDashboardModule.objects.all():
        modules.append(FeedDashboardModule(title=feed.title, feed_url=feed.feed, limit=feed.limit))
    return modules