# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class RentalOperatorCompetency(models.Model):
    _name = 'rental.operator.competency'
    _description = 'Operator Competency / Certification'
    _rec_name = 'name'
    _order = 'name'

    operator_id = fields.Many2one(
        'rental.operator',
        string='Operator',
        required=True,
        ondelete='cascade',
        index=True,
    )
    name = fields.Char(string='Competency / Skill', required=True)
    certificate_number = fields.Char(string='Certificate Number')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    expired = fields.Boolean(
        string='Expired',
        compute='_compute_expired',
        store=True,
    )
    issuing_body = fields.Char(string='Issuing Body / Authority')

    @api.depends('expiry_date')
    def _compute_expired(self):
        today = date.today()
        for rec in self:
            if rec.expiry_date:
                rec.expired = rec.expiry_date < today
            else:
                rec.expired = False
