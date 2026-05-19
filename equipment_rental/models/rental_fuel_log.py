# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RentalFuelLog(models.Model):
    _name = 'rental.fuel.log'
    _description = 'Equipment Fuel Log'
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
    liters = fields.Float(string='Liters', required=True, digits=(10, 2))
    cost_per_liter = fields.Monetary(string='Cost Per Liter', currency_field='currency_id')
    total_cost = fields.Monetary(
        string='Total Cost',
        currency_field='currency_id',
        compute='_compute_total_cost',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    meter_reading = fields.Float(string='Meter Reading', digits=(10, 1))
    filled_by = fields.Char(string='Filled By')
    notes = fields.Char(string='Notes')

    @api.depends('liters', 'cost_per_liter')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.liters * rec.cost_per_liter
