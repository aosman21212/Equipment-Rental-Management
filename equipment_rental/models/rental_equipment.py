# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RentalEquipment(models.Model):
    _name = 'rental.equipment'
    _description = 'Rental Equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Equipment Name', required=True, tracking=True)
    code = fields.Char(
        string='Equipment Code',
        readonly=True,
        copy=False,
        default='New',
    )
    category_id = fields.Many2one(
        'rental.equipment.category',
        string='Category',
        required=True,
        tracking=True,
    )
    make = fields.Char(string='Make / Manufacturer')
    model_name = fields.Char(string='Model')
    year = fields.Integer(string='Year of Manufacture')
    serial_number = fields.Char(string='Serial Number')
    plate_number = fields.Char(string='Plate / Registration Number')
    status = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('reserved', 'Reserved'),
            ('on_rent', 'On Rent'),
            ('in_transit', 'In Transit'),
            ('workshop', 'In Workshop'),
            ('inspection_hold', 'Inspection Hold'),
            ('decommissioned', 'Decommissioned'),
        ],
        string='Status',
        default='available',
        required=True,
        tracking=True,
    )
    site_id = fields.Many2one('rental.site', string='Current Site')
    hour_meter = fields.Float(string='Hour Meter (hrs)', digits=(10, 1))
    odometer = fields.Float(string='Odometer (km)', digits=(10, 1))
    daily_rate = fields.Monetary(string='Daily Rate', currency_field='currency_id')
    weekly_rate = fields.Monetary(string='Weekly Rate', currency_field='currency_id')
    monthly_rate = fields.Monetary(string='Monthly Rate', currency_field='currency_id')
    hourly_rate = fields.Monetary(string='Hourly Rate', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    image = fields.Binary(string='Image', attachment=True)
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)

    component_ids = fields.One2many(
        'rental.equipment.component', 'equipment_id', string='Components'
    )
    meter_log_ids = fields.One2many(
        'rental.equipment.meter.log', 'equipment_id', string='Meter Logs'
    )

    # Smart button counts
    quotation_count = fields.Integer(string='Quotations', compute='_compute_quotation_count')
    contract_count = fields.Integer(string='Contracts', compute='_compute_contract_count')
    inspection_count = fields.Integer(string='Inspections', compute='_compute_inspection_count')
    workshop_count = fields.Integer(string='Workshop Jobs', compute='_compute_workshop_count')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rental.equipment') or 'New'
        return super().create(vals_list)

    def _compute_quotation_count(self):
        for rec in self:
            rec.quotation_count = self.env['rental.quotation.line'].search_count(
                [('equipment_id', '=', rec.id)]
            )

    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = self.env['rental.contract.line'].search_count(
                [('equipment_id', '=', rec.id)]
            )

    def _compute_inspection_count(self):
        for rec in self:
            rec.inspection_count = self.env['rental.inspection'].search_count(
                [('equipment_id', '=', rec.id)]
            )

    def _compute_workshop_count(self):
        for rec in self:
            rec.workshop_count = self.env['rental.workshop.job'].search_count(
                [('equipment_id', '=', rec.id)]
            )

    def action_set_available(self):
        self.write({'status': 'available'})

    def action_set_workshop(self):
        self.write({'status': 'workshop'})

    def action_set_inspection_hold(self):
        self.write({'status': 'inspection_hold'})

    def action_set_decommissioned(self):
        self.write({'status': 'decommissioned'})

    def action_view_quotations(self):
        lines = self.env['rental.quotation.line'].search([('equipment_id', '=', self.id)])
        quotation_ids = lines.mapped('quotation_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotations',
            'res_model': 'rental.quotation',
            'view_mode': 'list,form',
            'domain': [('id', 'in', quotation_ids)],
        }

    def action_view_contracts(self):
        lines = self.env['rental.contract.line'].search([('equipment_id', '=', self.id)])
        contract_ids = lines.mapped('contract_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contracts',
            'res_model': 'rental.contract',
            'view_mode': 'list,form',
            'domain': [('id', 'in', contract_ids)],
        }

    def action_view_inspections(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inspections',
            'res_model': 'rental.inspection',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
        }

    def action_view_workshop(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Workshop Jobs',
            'res_model': 'rental.workshop.job',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
        }
