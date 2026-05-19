# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta, date


class RentalMaintenance(models.Model):
    _name = 'rental.maintenance'
    _description = 'Preventive Maintenance Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'next_due_date asc'

    name = fields.Char(
        string='Maintenance Reference',
        readonly=True,
        copy=False,
        default='New',
    )
    equipment_id = fields.Many2one(
        'rental.equipment',
        string='Equipment',
        required=True,
        index=True,
    )
    maintenance_type = fields.Char(string='Maintenance Type', help='e.g. Oil Change, Air Filter')
    cycle_hours = fields.Float(string='Cycle (Hours)', help='Repeat every N engine hours')
    last_done_date = fields.Date(string='Last Done Date')
    last_done_hours = fields.Float(string='Last Done Hours')
    next_due_date = fields.Date(
        string='Next Due Date',
        compute='_compute_next_due',
        store=True,
    )
    next_due_hours = fields.Float(
        string='Next Due Hours',
        compute='_compute_next_due',
        store=True,
    )
    state = fields.Selection(
        selection=[
            ('ok', 'OK'),
            ('due', 'Due'),
            ('overdue', 'Overdue'),
        ],
        string='Status',
        compute='_compute_state',
        store=True,
    )
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rental.maintenance') or 'New'
        return super().create(vals_list)

    @api.depends('last_done_date', 'last_done_hours', 'cycle_hours')
    def _compute_next_due(self):
        for rec in self:
            if rec.last_done_date and rec.cycle_hours:
                # Approximate: assume 8 hrs/day
                days = int(rec.cycle_hours / 8)
                rec.next_due_date = rec.last_done_date + timedelta(days=days)
            else:
                rec.next_due_date = False
            rec.next_due_hours = (rec.last_done_hours or 0.0) + (rec.cycle_hours or 0.0)

    @api.depends('next_due_date', 'next_due_hours', 'equipment_id.hour_meter')
    def _compute_state(self):
        today = date.today()
        for rec in self:
            current_hours = rec.equipment_id.hour_meter if rec.equipment_id else 0.0
            hours_overdue = rec.next_due_hours and current_hours > rec.next_due_hours
            date_overdue = rec.next_due_date and rec.next_due_date < today
            date_due = rec.next_due_date and rec.next_due_date <= (
                today + timedelta(days=7)
            ) and rec.next_due_date >= today
            if hours_overdue or date_overdue:
                rec.state = 'overdue'
            elif date_due:
                rec.state = 'due'
            else:
                rec.state = 'ok'
