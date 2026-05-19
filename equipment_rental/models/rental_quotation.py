# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RentalQuotation(models.Model):
    _name = 'rental.quotation'
    _description = 'Rental Quotation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_quotation desc, name desc'

    name = fields.Char(
        string='Quotation Reference',
        readonly=True,
        copy=False,
        default='New',
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
    )
    date_quotation = fields.Date(
        string='Quotation Date',
        default=fields.Date.today,
        required=True,
    )
    date_valid = fields.Date(string='Valid Until')
    site_id = fields.Many2one('rental.site', string='Project Site')
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
        required=True,
    )
    line_ids = fields.One2many('rental.quotation.line', 'quotation_id', string='Quotation Lines')
    notes = fields.Text(string='Terms & Notes')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('approved', 'Approved'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    amount_total = fields.Monetary(
        string='Total Amount',
        currency_field='currency_id',
        compute='_compute_amount_total',
        store=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
    )
    contract_count = fields.Integer(string='Contracts', compute='_compute_contract_count')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rental.quotation') or 'New'
        return super().create(vals_list)

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('subtotal'))

    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = self.env['rental.contract'].search_count(
                [('quotation_id', '=', rec.id)]
            )

    def action_send(self):
        self.write({'state': 'sent'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_create_contract(self):
        self.ensure_one()
        contract = self.env['rental.contract'].create({
            'quotation_id': self.id,
            'customer_id': self.customer_id.id,
            'site_id': self.site_id.id if self.site_id else False,
            'currency_id': self.currency_id.id,
            'notes': self.notes,
            'date_start': fields.Date.today(),
            'line_ids': [
                (0, 0, {
                    'equipment_id': line.equipment_id.id,
                    'description': line.description,
                    'rental_basis': line.rental_basis,
                    'date_from': line.date_from,
                    'date_to': line.date_to,
                    'qty': line.qty,
                    'unit_price': line.unit_price,
                    'operator_id': line.operator_id.id if line.operator_id else False,
                })
                for line in self.line_ids
            ],
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contract',
            'res_model': 'rental.contract',
            'view_mode': 'form',
            'res_id': contract.id,
        }

    def action_view_contracts(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contracts',
            'res_model': 'rental.contract',
            'view_mode': 'list,form',
            'domain': [('quotation_id', '=', self.id)],
        }
