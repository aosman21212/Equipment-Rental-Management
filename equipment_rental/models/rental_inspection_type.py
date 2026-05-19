# -*- coding: utf-8 -*-
from odoo import models, fields


class RentalInspectionType(models.Model):
    _name = 'rental.inspection.type'
    _description = 'Inspection Type'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Inspection Type', required=True)
    category = fields.Selection(
        selection=[
            ('internal', 'Internal'),
            ('third_party', 'Third Party'),
        ],
        string='Category',
        default='internal',
    )
    cycle_days = fields.Integer(string='Inspection Cycle (Days)', default=90)
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')
