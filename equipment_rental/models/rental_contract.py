# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RentalContract(models.Model):
    _name = 'rental.contract'
    _description = 'Rental Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_start desc, name desc'

    name = fields.Char(
        string='Contract Reference',
        readonly=True,
        copy=False,
        default='New',
    )
    quotation_id = fields.Many2one('rental.quotation', string='Source Quotation')
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
    )
    site_id = fields.Many2one('rental.site', string='Project Site')
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date')
    line_ids = fields.One2many('rental.contract.line', 'contract_id', string='Contract Lines')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('completed', 'Completed'),
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
    notes = fields.Text(string='Terms & Notes')
    dispatch_count = fields.Integer(string='Dispatches', compute='_compute_dispatch_count')
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rental.contract') or 'New'
        return super().create(vals_list)

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('subtotal'))

    def _compute_dispatch_count(self):
        for rec in self:
            rec.dispatch_count = self.env['rental.dispatch'].search_count(
                [('contract_id', '=', rec.id)]
            )

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = self.env['account.move'].search_count([
                ('ref', 'like', rec.name),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
            ])

    def action_activate(self):
        self.write({'state': 'active'})
        # Set equipment status to on_rent
        for line in self.line_ids:
            if line.equipment_id:
                line.equipment_id.write({'status': 'on_rent'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_create_dispatch(self):
        self.ensure_one()
        dispatch = self.env['rental.dispatch'].create({
            'contract_id': self.id,
            'equipment_ids': [(6, 0, self.line_ids.mapped('equipment_id').ids)],
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dispatch Order',
            'res_model': 'rental.dispatch',
            'view_mode': 'form',
            'res_id': dispatch.id,
        }

    def action_create_invoice(self):
        self.ensure_one()
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'ref': self.name,
            'currency_id': self.currency_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': line.description or line.equipment_id.name,
                    'quantity': line.qty,
                    'price_unit': line.unit_price,
                })
                for line in self.line_ids
            ],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }

    def action_view_dispatches(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dispatch Orders',
            'res_model': 'rental.dispatch',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
        }

    def action_view_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [
                ('ref', 'like', self.name),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
            ],
        }
