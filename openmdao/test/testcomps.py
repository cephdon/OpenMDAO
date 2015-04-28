""" Some simple test components. """

from openmdao.core.component import Component


class SimpleComp(Component):
    """ The simplest component you can imagine. """

    def __init__(self):
        super(SimpleComp, self).__init__()

        # Inputs
        self.add_param('x', 3.0)

        # Outputs
        self.add_unknown('y', 5.5)

    def solve_nonlinear(self, params, unknowns, resids):
        """ Doesn't do much. """

        unknowns['y'] = 2.0*parameters['x']