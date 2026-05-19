# -*- coding: utf-8 -*-
from odoo import models, fields


class RentalSite(models.Model):
    _name = 'rental.site'
    _description = 'Rental Site / Project Location'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Site Name', required=True)
    code = fields.Char(string='Code')
    address = fields.Text(string='Address')
    partner_id = fields.Many2one('res.partner', string='Client / Project Owner')
    active = fields.Boolean(string='Active', default=True)
    notes = fields.Text(string='Notes')
