# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import random

from trytond.i18n import gettext
from trytond.model import ModelSQL, ModelView, Unique, fields
from trytond.modules.production_work.exceptions import PickerError
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval


class WorkCenterSharedParent(ModelSQL, ModelView):
    'Work Center Shared Parent'
    __name__ = 'production.work.center-shared.parent'

    work_center = fields.Many2One(
        'production.work.center', 'Work Center', required=True,
        ondelete='CASCADE')
    parent = fields.Many2One(
        'production.work.center', 'Shared with Work Center', required=True,
        ondelete='CASCADE',
        domain=[
            ('id', '!=', Eval('work_center', -1)),
            ('company', '=', Eval('company', -1)),
            ('warehouse', '=', Eval('warehouse', -1)),
            ],
        depends=['work_center', 'company', 'warehouse'])
    company = fields.Function(
        fields.Many2One('company.company', 'Company'),
        'on_change_with_company')
    warehouse = fields.Function(
        fields.Many2One('stock.location', 'Warehouse'),
        'on_change_with_warehouse')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        table = cls.__table__()
        cls._sql_constraints += [
            ('work_center_parent_uniq',
                Unique(table, table.work_center, table.parent),
                'The shared relation must be unique.'),
            ]

    @fields.depends('work_center', '_parent_work_center.company')
    def on_change_with_company(self, name=None):
        if self.work_center and self.work_center.company:
            return self.work_center.company.id

    @fields.depends('work_center', '_parent_work_center.warehouse')
    def on_change_with_warehouse(self, name=None):
        if self.work_center and self.work_center.warehouse:
            return self.work_center.warehouse.id


class WorkCenter(metaclass=PoolMeta):
    __name__ = 'production.work.center'

    shared_parents = fields.Many2Many(
        'production.work.center-shared.parent', 'work_center', 'parent',
        'Shared with Work Centers',
        domain=[
            ('id', '!=', Eval('id', -1)),
            ('company', '=', Eval('company', -1)),
            ('warehouse', '=', Eval('warehouse', -1)),
            ],
        depends=['id', 'company', 'warehouse'])

    @classmethod
    def get_picker(cls):
        """Return a picker that also considers shared work centers."""
        cache = {}

        def picker(parent, category):
            key = (parent.id, category.id)
            if key not in cache:
                work_centers = cls.search([
                        ('category', '=', category.id),
                        ['OR',
                            ('parent', 'child_of', [parent.id]),
                            ('shared_parents', 'in', [parent.id]),
                            ],
                        ])
                if not work_centers:
                    raise PickerError(
                        gettext('production_work.msg_missing_work_center',
                            category=category.rec_name,
                            parent=parent.rec_name))
                cache[key] = work_centers
            return random.choice(cache[key])

        return picker


class RoutingStep(metaclass=PoolMeta):
    __name__ = 'production.routing.step'

    def get_work(self, production, work_center_picker):
        WorkCenter = Pool().get('production.work.center')
        return super().get_work(production, WorkCenter.get_picker())
