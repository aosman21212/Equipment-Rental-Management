# -*- coding: utf-8 -*-
from odoo import models, fields


class RentalEquipmentCategory(models.Model):
    _name = 'rental.equipment.category'
    _description = 'Equipment Category'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True)
    parent_id = fields.Many2one(
        'rental.equipment.category',
        string='Parent Category',
        ondelete='restrict',
        index=True,
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('rental.equipment.category', 'parent_id', string='Subcategories')
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    equipment_count = fields.Integer(string='Equipment Count', compute='_compute_equipment_count')

    def _compute_equipment_count(self):
        for rec in self:
            rec.equipment_count = self.env['rental.equipment'].search_count(
                [('category_id', '=', rec.id)]
            )
