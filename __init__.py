# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from trytond.pool import Pool

from . import production


def register():
    Pool.register(
        production.WorkCenterSharedParent,
        production.WorkCenter,
        production.RoutingStep,
        module='production_shared_work_center', type_='model')
