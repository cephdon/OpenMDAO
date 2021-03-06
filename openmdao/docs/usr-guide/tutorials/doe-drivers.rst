.. _OpenMDAO-DoE_Drivers:

===========
DoE Drivers
===========

This tutorial shows you how to use the OptimizedLatinHypercubeDriver to run a design of experiments (DoE).
The Latin Hypercube (LHC) method of randomization generates samples across an entire range of desired design variables.
The Optimized Latin Hypercube (OLHC) is an improvment on the LHC method in which samples generated by the LHC are adjusted to ensure an expansive distribution.

Below is an example using the component from the :ref:`paraboloid_tutorial`.
::

    from openmdao.api import IndepVarComp, Group, Problem, ScipyOptimizer, ExecComp, DumpRecorder
    from openmdao.test.paraboloid import Paraboloid

    from openmdao.drivers.latinhypercube_driver import LatinHypercubeDriver, OptimizedLatinHypercubeDriver

    top = Problem()
    root = top.root = Group()

    root.add('p1', IndepVarComp('x', 50.0), promotes=['*'])
    root.add('p2', IndepVarComp('y', 50.0), promotes=['*'])
    root.add('comp', Paraboloid(), promotes=['*'])

    top.driver = OptimizedLatinHypercubeDriver(num_samples=4, seed=0, population=20, generations=4, norm_method=2)
    top.driver.add_desvar('x', lower=-50.0, upper=50.0)
    top.driver.add_desvar('y', lower=-50.0, upper=50.0)

    top.driver.add_objective('f_xy')

    recorder = DumpRecorder('paraboloid')
    recorder.options['record_params'] = True
    recorder.options['record_unknowns'] = False
    recorder.options['record_resids'] = False
    top.driver.add_recorder(recorder)

    top.setup()
    top.run()

    top.cleanup()


Here we will explain the code statements that pertain to using an Optimized Latin Hypercube (OLHC).
::

    from openmdao.drivers.latinhypercube_driver import LatinHypercubeDriver, OptimizedLatinHypercubeDriver

In order to setup a model to utilize the OLHC, we need to import these specific drivers. The 'optimized' version is a subclass of the LatinHypercubeDriver.
::

    root.add('p1', IndepVarComp('x', 50.0), promotes=['*'])
    root.add('p2', IndepVarComp('y', 50.0), promotes=['*'])
    root.add('comp', Paraboloid(), promotes=['*'])

By promoting the variables x and y to the group level, no *connect* statement is needed for the paraboloid component to receive these as input variables.  Similarly, when we define the OLHC design variables, we can simply call the same *x* and *y* without any additional code.

The next three lines will initialize and add design variables to the OLHC.
::

    top.driver = OptimizedLatinHypercubeDriver(num_samples=4, seed=0, population=20, generations=4, norm_method=2)
    top.driver.add_desvar('x', lower=-50.0, upper=50.0)
    top.driver.add_desvar('y', lower=-50.0, upper=50.0)

The first line initializes the driver. The 'num_samples' argument determines how many samples each design variable will cycle through. By default, the 'seed' argument itself is a random value. However, by choosing a seed value, we can easily duplicate a sample set for a repeatable testing environment.

The next two lines define the ranges of the design variables on which the OLHC will operate.

Now we are ready to record data. The four intervals of [-50, 50) are: [-50,-25), [-25,0), [0,25), [25,50).  The LHC will ensure there is an *x* and *y* value in each interval.

The recorded output is shown below. It's been filtered to show only the generated input values.
::

    Timestamp: 1446745425.935
    Iteration Coordinate: Driver/0
    Params:
      comp.x: -34.5655676503
      comp.y: -37.7665306197
    Timestamp: 1446745425.936
    Iteration Coordinate: Driver/0
    Params:
      comp.x: 47.7779475273
      comp.y: 14.7245403548
    Timestamp: 1446745425.936
    Iteration Coordinate: Driver/0
    Params:
      comp.x: -7.77803623101
      comp.y: 34.1373674836
    Timestamp: 1446745425.936
    Iteration Coordinate: Driver/0
    Params:
      comp.x: 1.49637359158
      comp.y: -14.9422886231

As you can see, there is an 'x' and 'y' value in each interval. The OLHC was able to set up 3 of the 4 input combinations to be in different intervals from each other, ensuring better coverage of the parameter space.
