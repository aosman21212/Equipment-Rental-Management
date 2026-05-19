# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RentalBreakdown(models.Model):
    _name = 'rental.breakdown'
    _description = 'Equipment Breakdown'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'reported_date desc, name desc'

    name = fields.Char(
        string='Breakdown Reference',
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
    reported_date = fields.Date(
        string='Reported Date',
        default=fields.Date.today,
        required=True,
    )
    reported_by = fields.Char(string='Reported By')
    description = fields.Text(string='Breakdown Description', required=True)
    severity = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        string='Severity',
        default='medium',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('open', 'Open'),
            ('in_progress', 'In Progress'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed'),
        ],
        string='Status',
        default='open',
        required=True,
        tracking=True,
    )
    workshop_job_id = fields.Many2one('rental.workshop.job', string='Workshop Job')
    resolution_notes = fields.Text(string='Resolution Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rental.breakdown') or 'New'
        return super().create(vals_list)

    def action_start_repair(self):
        self.write({'state': 'in_progress'})

    def action_resolve(self):
        self.write({'state': 'resolved'})

    def action_close(self):
        self.write({'state': 'closed'})

    def action_create_workshop_job(self):
        self.ensure_one()
        job = self.env['rental.workshop.job'].create({
            'equipment_id': self.equipment_id.id,
            'job_type': 'breakdown',
            'breakdown_id': self.id,
            'description': self.description,
        })
        self.workshop_job_id = job.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Workshop Job',
            'res_model': 'rental.workshop.job',
            'view_mode': 'form',
            'res_id': job.id,
        }
