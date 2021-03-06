"""functions useful for debugging openmdao"""
from __future__ import print_function

from six import itervalues

import os
import sys
from itertools import chain
from pprint import pformat
from functools import wraps
from resource import getrusage, RUSAGE_SELF, RUSAGE_CHILDREN
from six import itervalues

import numpy

from openmdao.util.type_util import real_types

def dump_meta(system, nest=0, out_stream=sys.stdout):
    """
    Dumps the system tree with associated metadata for the params and unknowns
    `VecWrappers`.

    Args
    ----
    system : `System`
        The node in the `System` tree where dumping begins.

    nest : int, optional
        Starting nesting level.  Defaults to 0.

    out_stream : file-like, optional
        Where output is written.  Defaults to sys.stdout.

    """
    klass = system.__class__.__name__

    commsz = system.comm.size if hasattr(system.comm, 'size') else 0

    margin = ' '*nest
    if system.is_active():
        out_stream.write("%s %s '%s'    req: %s  usize:%d  psize:%d  commsize:%d\n" %
                         (margin,
                          klass,
                          system.name,
                          system.get_req_procs(),
                          system.unknowns.vec.size,
                          system.params.vec.size,
                          commsz))

        margin = ' '*(nest+6)
        out_stream.write("%sunknowns:\n" % margin)
        for v, meta in system.unknowns.items():
            out_stream.write("%s%s: " % (margin, v))
            out_stream.write(pformat(meta, indent=nest+9).replace("{","{\n",1))
            out_stream.write('\n')

        out_stream.write("%sparams:\n" % margin)
        for v, meta in system.params.items():
            out_stream.write("%s%s: " % (margin, v))
            out_stream.write(pformat(meta, indent=nest+9).replace("{","{\n",1))
            out_stream.write('\n')
    else:
        out_stream.write("%s %s '%s'   (inactive)\n" %
                         (margin, klass, system.name))

    nest += 3
    for sub in itervalues(system._subsystems):
        dump_meta(sub, nest, out_stream=out_stream)

    out_stream.flush()

class dec_if(object):
    """Conditional decorator.  If cond is True, the given decorator
    will be applied.
    """
    def __init__(self, dec, cond):
        self.dec = dec
        self.cond = cond

    def __call__(self, func):
        if self.cond:
            return self.dec(func)
        return func

def max_mem_usage():
    """
    Returns
    -------
    The max memory used by this process and its children, in MB.
    """
    denom = 1024.
    if sys.platform == 'darwin':
        denom *= denom
    total = getrusage(RUSAGE_SELF).ru_maxrss / denom
    total += getrusage(RUSAGE_CHILDREN).ru_maxrss / denom
    return total

try:
    import psutil

    def mem_usage(msg='', out=sys.stdout):
        """
        Returns
        -------
        The current memory used by this process (and it's children?), in MB.
        """
        denom = 1024. * 1024.
        p = psutil.Process(os.getpid())
        mem = p.memory_info().rss / denom
        if msg:
            print(msg,"%6.3f MB" % mem, file=out)
        return mem

    def diff_mem(fn):
        """
        This gives the difference in memory before and after the
        decorated function is called. Requires psutil to be installed.
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            startmem = mem_usage()
            ret = fn(*args, **kwargs)
            maxmem = mem_usage()
            diff = maxmem - startmem
            if diff > 0.0:
                if args and hasattr(args[0], 'pathname'):
                    name = args[0].pathname
                else:
                    name = ''
                print(name,"%s added %5.3f MB (total: %6.3f)" % (fn.__name__, diff, maxmem))
            return ret
        return wrapper

except ImportError:
    pass

def num_systems(root):
    """
    Return the total number of systems in the tree starting at the given
    root.
    """
    return len([s for s in root.subsystems(recurse=True, include_self=True)])

def max_tree_depth(root):
    """
    Return the max depth of the tree starting from root.
    """
    return max(len(s.pathname.split('.'))
                   for s in root.subsystems(recurse=True))

def _f2mb(fsize):
    """Returns the size of an array of floats (double precision)
    in MB.
    """
    return fsize * 8 / 1024 / 1024

def stats(problem):
    """
    Print various stats about the Problem.
    """
    root = problem.root

    print("Num systems:", num_systems(root))
    print("Max tree depth:", max_tree_depth(root))

    print("\nMax mem usage: %s MB" % max_mem_usage())
    print("Current mem usage: %s MB" % mem_usage())
