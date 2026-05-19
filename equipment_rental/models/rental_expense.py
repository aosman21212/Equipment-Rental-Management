# -*- coding: utf-8 -*-
from odoo import models, fields


class RentalExpense(models.Model):
    _name = 'rental.expense'
    _description = 'Rental Field Expense'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date desc'

    name = fields.Char(string='Expense Description', required=True)
    equipment_id = fields.Many2one('rental.equipment', string='Equipment')
    contract_id = fields.Many2one('rental.contract', string='Contract')
    operator_id = fields.Many2one('rental.operator', string='Operator')
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    expense_type = fields.Selection(
        selection=[
            ('fuel', 'Fuel'),
            ('toll', 'Toll'),
            ('parking', 'Parking'),
            ('transport', 'Transport'),
            ('accommodation', 'Accommodation'),
            ('meals', 'Meals'),
            ('consumables', 'Consumables'),
            ('minor_repair', 'Minor Repair'),
            ('permit', 'Permit'),
            ('other', 'Other'),
        ],
        string='Expense Type',
        default='other',
    )
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    responsibility = fields.Selection(
        selection=[
            ('customer', 'Customer'),
            ('company', 'Company'),
        ],
        string='Charged To',
        default='company',
    )
    reference = fields.Char(string='Reference / Receipt No.')
    notes = fields.Char(string='Notes')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_reset(self):
        self.write({'state': 'draft'})
