# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RentalDispatch(models.Model):
    _name = 'rental.dispatch'
    _description = 'Rental Dispatch Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'dispatch_date desc, name desc'

    name = fields.Char(
        string='Dispatch Reference',
        readonly=True,
        copy=False,
        default='New',
    )
    contract_id = fields.Many2one(
        'rental.contract',
        string='Contract',
        required=True,
        tracking=True,
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='contract_id.customer_id',
        store=True,
    )
    site_id = fields.Many2one(
        'rental.site',
        string='Site',
        related='contract_id.site_id',
        store=True,
    )
    dispatch_date = fields.Date(string='Dispatch Date', default=fields.Date.today, required=True)
    equipment_ids = fields.Many2many(
        'rental.equipment',
        'rental_dispatch_equipment_rel',
        'dispatch_id',
        'equipment_id',
        string='Equipment',
    )
    driver_name = fields.Char(string='Driver Name')
    vehicle_plate = fields.Char(string='Transport Vehicle Plate')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('dispatched', 'Dispatched'),
            ('on_site', 'On Site'),
            ('returned', 'Returned'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    notes = fields.Text(string='Notes')
    offhire_count = fields.Integer(string='Off-Hire Returns', compute='_compute_offhire_count')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rental.dispatch') or 'New'
        return super().create(vals_list)

    def _compute_offhire_count(self):
        for rec in self:
            rec.offhire_count = self.env['rental.offhire'].search_count(
                [('dispatch_id', '=', rec.id)]
            )

    def action_dispatch(self):
        self.write({'state': 'dispatched'})
        for eq in self.equipment_ids:
            eq.write({'status': 'in_transit'})

    def action_confirm_on_site(self):
        self.write({'state': 'on_site'})
        for eq in self.equipment_ids:
            if self.site_id:
                eq.write({'status': 'on_rent', 'site_id': self.site_id.id})
            else:
                eq.write({'status': 'on_rent'})

    def action_create_offhire(self):
        self.ensure_one()
        offhire = self.env['rental.offhire'].create({
            'dispatch_id': self.id,
            'equipment_ids': [(6, 0, self.equipment_ids.ids)],
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Off-Hire Return',
            'res_model': 'rental.offhire',
            'view_mode': 'form',
            'res_id': offhire.id,
        }

    def action_view_offhires(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Off-Hire Returns',
            'res_model': 'rental.offhire',
            'view_mode': 'list,form',
            'domain': [('dispatch_id', '=', self.id)],
        }
