# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta


class RentalQuotationLine(models.Model):
    _name = 'rental.quotation.line'
    _description = 'Rental Quotation Line'
    _rec_name = 'equipment_id'
    _order = 'id'

    quotation_id = fields.Many2one(
        'rental.quotation',
        string='Quotation',
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
    )
    date_from = fields.Datetime(string='From')
    date_to = fields.Datetime(string='To')
    qty = fields.Float(
        string='Quantity / Duration',
        default=1,
        digits=(10, 2),
    )
    unit_price = fields.Monetary(string='Unit Price', currency_field='currency_id')
    subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='quotation_id.currency_id',
        store=True,
    )
    operator_required = fields.Boolean(string='Operator Required')
    operator_id = fields.Many2one('rental.operator', string='Operator')

    @api.onchange('equipment_id', 'rental_basis', 'quotation_id')
    def _onchange_equipment_rate(self):
        if self.equipment_id:
            basis = self.rental_basis or (self.quotation_id and self.quotation_id.rental_basis) or 'daily'
            rate_map = {
                'hourly': self.equipment_id.hourly_rate,
                'daily': self.equipment_id.daily_rate,
                'weekly': self.equipment_id.weekly_rate,
                'monthly': self.equipment_id.monthly_rate,
                'yearly': self.equipment_id.monthly_rate * 12,
            }
            self.unit_price = rate_map.get(basis, 0.0)
            if not self.description:
                self.description = self.equipment_id.name

    @api.depends('qty', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.unit_price
