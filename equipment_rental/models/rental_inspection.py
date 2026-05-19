# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta


class RentalInspection(models.Model):
    _name = 'rental.inspection'
    _description = 'Equipment Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'scheduled_date desc, name desc'

    name = fields.Char(
        string='Inspection Reference',
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
    inspection_type_id = fields.Many2one(
        'rental.inspection.type',
        string='Inspection Type',
        required=True,
    )
    scheduled_date = fields.Date(string='Scheduled Date', required=True)
    completed_date = fields.Date(string='Completed Date')
    inspector_name = fields.Char(string='Inspector Name')
    result = fields.Selection(
        selection=[
            ('pass', 'Pass'),
            ('fail', 'Fail'),
            ('conditional', 'Conditional'),
        ],
        string='Result',
    )
    next_due_date = fields.Date(
        string='Next Due Date',
        compute='_compute_next_due_date',
        store=True,
    )
    state = fields.Selection(
        selection=[
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('overdue', 'Overdue'),
        ],
        string='Status',
        default='scheduled',
        required=True,
        tracking=True,
    )
    findings = fields.Text(string='Findings / Observations')
    notes = fields.Text(string='Notes')
    certificate_ids = fields.One2many(
        'rental.certificate', 'inspection_id', string='Certificates Issued',
        context="{'default_equipment_id': equipment_id}",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rental.inspection') or 'New'
        return super().create(vals_list)

    @api.depends('scheduled_date', 'inspection_type_id', 'inspection_type_id.cycle_days')
    def _compute_next_due_date(self):
        for rec in self:
            if rec.scheduled_date and rec.inspection_type_id and rec.inspection_type_id.cycle_days:
                rec.next_due_date = rec.scheduled_date + timedelta(
                    days=rec.inspection_type_id.cycle_days
                )
            else:
                rec.next_due_date = False

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.write({'state': 'completed', 'completed_date': fields.Date.today()})

    def action_mark_overdue(self):
        self.write({'state': 'overdue'})
