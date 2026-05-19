# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class RentalWorkshopJob(models.Model):
    _name = 'rental.workshop.job'
    _description = 'Workshop Job'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'start_date desc, name desc'

    name = fields.Char(
        string='Job Reference',
        readonly=True,
        copy=False,
        default='New',
    )
    equipment_id = fields.Many2one(
        'rental.equipment',
        string='Equipment',
        required=True,
        tracking=True,
    )
    job_type = fields.Selection(
        selection=[
            ('corrective', 'Corrective'),
            ('preventive', 'Preventive'),
            ('from_inspection', 'From Inspection'),
            ('breakdown', 'From Breakdown'),
        ],
        string='Job Type',
        default='corrective',
    )
    inspection_id = fields.Many2one('rental.inspection', string='Related Inspection')
    breakdown_id = fields.Many2one('rental.breakdown', string='Related Breakdown')
    description = fields.Text(string='Job Description', required=True)
    assigned_to = fields.Char(string='Assigned To')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    downtime_hours = fields.Float(
        string='Downtime (hrs)',
        compute='_compute_downtime_hours',
        store=True,
    )
    repair_type = fields.Selection(
        selection=[
            ('internal', 'Internal'),
            ('external', 'External'),
        ],
        string='Repair Type',
        default='internal',
    )
    vendor_id = fields.Many2one('res.partner', string='External Vendor')
    cost = fields.Monetary(string='Labour / Job Cost', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    parts_ids = fields.One2many('rental.workshop.parts', 'job_id', string='Parts Used')
    notes = fields.Text(string='Notes')
    total_parts_cost = fields.Monetary(
        string='Total Parts Cost',
        currency_field='currency_id',
        compute='_compute_total_parts_cost',
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rental.workshop.job') or 'New'
        return super().create(vals_list)

    @api.depends('start_date', 'end_date')
    def _compute_downtime_hours(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                delta = rec.end_date - rec.start_date
                rec.downtime_hours = delta.days * 24.0
            else:
                rec.downtime_hours = 0.0

    @api.depends('parts_ids.subtotal')
    def _compute_total_parts_cost(self):
        for rec in self:
            rec.total_parts_cost = sum(rec.parts_ids.mapped('subtotal'))

    def action_start(self):
        self.write({'state': 'in_progress'})
        for job in self:
            job.equipment_id.write({'status': 'workshop'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class RentalWorkshopParts(models.Model):
    _name = 'rental.workshop.parts'
    _description = 'Workshop Job Parts'
    _rec_name = 'name'
    _order = 'id'

    job_id = fields.Many2one(
        'rental.workshop.job',
        string='Workshop Job',
        required=True,
        ondelete='cascade',
        index=True,
    )
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Part / Description', required=True)
    qty = fields.Float(string='Quantity', default=1, digits=(10, 3))
    unit_cost = fields.Monetary(string='Unit Cost', currency_field='currency_id')
    subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='job_id.currency_id',
        store=True,
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.unit_cost = self.product_id.standard_price

    @api.depends('qty', 'unit_cost')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.unit_cost
