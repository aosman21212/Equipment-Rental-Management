# -*- coding: utf-8 -*-
from odoo import models, fields


class RentalUsageLog(models.Model):
    _name = 'rental.usage.log'
    _description = 'Equipment Usage Log'
    _rec_name = 'equipment_id'
    _order = 'date desc'

    equipment_id = fields.Many2one(
        'rental.equipment',
        string='Equipment',
        required=True,
        index=True,
    )
    contract_id = fields.Many2one('rental.contract', string='Contract')
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    hours_worked = fields.Float(string='Hours Worked', digits=(10, 2))
    start_reading = fields.Float(string='Start Meter Reading', digits=(10, 1))
    end_reading = fields.Float(string='End Meter Reading', digits=(10, 1))
    operator_id = fields.Many2one('rental.operator', string='Operator')
    site_id = fields.Many2one('rental.site', string='Site')
    notes = fields.Char(string='Notes')
