# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RentalContractLine(models.Model):
    _name = 'rental.contract.line'
    _description = 'Rental Contract Line'
    _rec_name = 'equipment_id'
    _order = 'id'

    contract_id = fields.Many2one(
        'rental.contract',
        string='Contract',
        required=True,
        ondelete='cascade',
        index=True,
    )
    equipment_id = fields.Many2one(
        'rental.equipment',
        string='Equipment',
        required=True,
    )
    description = fields.Char(string='Description')
    rental_basis = fields.Selection(
        selection=[
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        string='Rental Basis',
        default='daily',
    )
    date_from = fields.Datetime(string='From')
    date_to = fields.Datetime(string='To')
    qty = fields.Float(string='Quantity / Duration', default=1, digits=(10, 2))
    unit_price = fields.Monetary(string='Unit Price', currency_field='currency_id')
    subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='contract_id.currency_id',
        store=True,
    )
    operator_id = fields.Many2one('rental.operator', string='Operator')

    @api.depends('qty', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.unit_price
