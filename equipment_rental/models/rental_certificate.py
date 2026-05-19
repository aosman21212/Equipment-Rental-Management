# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class RentalCertificate(models.Model):
    _name = 'rental.certificate'
    _description = 'Equipment Certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'expiry_date asc'

    name = fields.Char(string='Certificate Name', required=True)
    equipment_id = fields.Many2one(
        'rental.equipment',
        string='Equipment',
        required=True,
        index=True,
    )
    inspection_id = fields.Many2one('rental.inspection', string='Related Inspection')
    certificate_type = fields.Char(string='Certificate Type')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date', required=True)
    issuing_authority = fields.Char(string='Issuing Authority')
    sticker_color = fields.Selection(
        selection=[
            ('green', 'Green'),
            ('yellow', 'Yellow'),
            ('red', 'Red'),
        ],
        string='Status Color',
        compute='_compute_sticker_color',
        store=True,
    )
    expired = fields.Boolean(
        string='Expired',
        compute='_compute_expired',
        store=True,
    )
    notes = fields.Text(string='Notes')

    @api.depends('expiry_date')
    def _compute_sticker_color(self):
        today = date.today()
        for rec in self:
            if not rec.expiry_date:
                rec.sticker_color = 'green'
                continue
            days_remaining = (rec.expiry_date - today).days
            if days_remaining < 0:
                rec.sticker_color = 'red'
            elif days_remaining <= 60:
                rec.sticker_color = 'yellow'
            else:
                rec.sticker_color = 'green'

    @api.depends('expiry_date')
    def _compute_expired(self):
        today = date.today()
        for rec in self:
            if rec.expiry_date:
                rec.expired = rec.expiry_date < today
            else:
                rec.expired = False
