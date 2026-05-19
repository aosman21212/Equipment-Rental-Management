# -*- coding: utf-8 -*-
from odoo import models, fields


class RentalEquipmentComponent(models.Model):
    _name = 'rental.equipment.component'
    _description = 'Equipment Component'
    _rec_name = 'name'
    _order = 'name'

    equipment_id = fields.Many2one(
        'rental.equipment',
        string='Equipment',
        required=True,
        ondelete='cascade',
        index=True,
    )
    name = fields.Char(string='Component Name', required=True)
    serial_number = fields.Char(string='Serial Number')
    condition = fields.Selection(
        selection=[
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        string='Condition',
        default='good',
    )
    notes = fields.Text(string='Notes')
