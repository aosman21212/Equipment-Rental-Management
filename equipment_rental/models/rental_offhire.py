# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RentalOffhire(models.Model):
    _name = 'rental.offhire'
    _description = 'Rental Off-Hire / Return'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'return_date desc, name desc'

    name = fields.Char(
        string='Off-Hire Reference',
        readonly=True,
        copy=False,
        default='New',
    )
    dispatch_id = fields.Many2one('rental.dispatch', string='Dispatch Order')
    contract_id = fields.Many2one(
        'rental.contract',
        string='Contract',
        related='dispatch_id.contract_id',
        store=True,
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='dispatch_id.customer_id',
        store=True,
    )
    return_date = fields.Date(string='Return Date', default=fields.Date.today, required=True)
    equipment_ids = fields.Many2many(
        'rental.equipment',
        'rental_offhire_equipment_rel',
        'offhire_id',
        'equipment_id',
        string='Equipment Returned',
    )
    condition = fields.Selection(
        selection=[
            ('good', 'Good'),
            ('minor_damage', 'Minor Damage'),
            ('major_damage', 'Major Damage'),
        ],
        string='Overall Condition',
        default='good',
    )
    damage_notes = fields.Text(string='Damage Description')
    missing_accessories = fields.Text(string='Missing Accessories')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rental.offhire') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        for eq in self.equipment_ids:
            eq.write({'status': 'available', 'site_id': False})
        if self.dispatch_id:
            self.dispatch_id.write({'state': 'returned'})
