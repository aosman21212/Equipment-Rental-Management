# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class RentalOperator(models.Model):
    _name = 'rental.operator'
    _description = 'Rental Operator'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Operator Name', required=True, tracking=True)
    code = fields.Char(string='Operator Code', readonly=True, copy=False, default='New')
    role = fields.Selection(
        selection=[
            ('operator', 'Operator'),
            ('helper', 'Helper'),
            ('rigger', 'Rigger'),
            ('signalman', 'Signalman'),
        ],
        string='Role',
        default='operator',
    )
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    employee_id = fields.Many2one('hr.employee', string='Employee Record')
    license_number = fields.Char(string='License Number')
    license_expiry = fields.Date(string='License Expiry')
    license_expired = fields.Boolean(
        string='License Expired',
        compute='_compute_license_expired',
        store=True,
    )
    image = fields.Binary(string='Photo', attachment=True)
    active = fields.Boolean(string='Active', default=True)
    competency_ids = fields.One2many(
        'rental.operator.competency', 'operator_id', string='Competencies'
    )
    assignment_count = fields.Integer(
        string='Assignments', compute='_compute_assignment_count'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rental.operator') or 'New'
        return super().create(vals_list)

    @api.depends('license_expiry')
    def _compute_license_expired(self):
        today = date.today()
        for rec in self:
            if rec.license_expiry:
                rec.license_expired = rec.license_expiry < today
            else:
                rec.license_expired = False

    def _compute_assignment_count(self):
        for rec in self:
            rec.assignment_count = self.env['rental.contract.line'].search_count(
                [('operator_id', '=', rec.id)]
            )

    def action_view_assignments(self):
        lines = self.env['rental.contract.line'].search([('operator_id', '=', self.id)])
        contract_ids = lines.mapped('contract_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignments',
            'res_model': 'rental.contract',
            'view_mode': 'list,form',
            'domain': [('id', 'in', contract_ids)],
        }
