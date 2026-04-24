# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.modules.company.tests import CompanyTestMixin
from trytond.tests.test_tryton import ModuleTestCase


class ProductionSharedWorkCenterTestCase(CompanyTestMixin, ModuleTestCase):
    'Test Production Shared Work Center module'
    module = 'production_shared_work_center'


del ModuleTestCase
