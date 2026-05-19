# -*- coding: utf-8 -*-
from odoo import models, fields


class RentalEquipmentMeterLog(models.Model):
    _name = 'rental.equipment.meter.log'
    _description = 'Equipment Meter Log'
    _rec_name = 'equipment_id'
    _order = 'date desc'

    equipment_id = fields.Many2one(
        'rental.equipment',
        string='Equipment',
        required=True,
        ondelete='cascade',
        index=True,
    )
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    hour_meter = fields.Float(string='Hour Meter (hrs)', digits=(10, 1))
    odometer = fields.Float(string='Odometer (km)', digits=(10, 1))
    logged_by = fields.Many2one('res.users', string='Logged By', default=lambda self: self.env.user)
    notes = fields.Char(string='Notes')
