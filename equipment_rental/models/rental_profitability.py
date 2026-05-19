# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RentalProfitability(models.Model):
    _name = 'rental.profitability'
    _description = 'Equipment Rental Profitability'
    _rec_name = 'equipment_id'
    _order = 'period_start desc'

    equipment_id = fields.Many2one(
        'rental.equipment',
        string='Equipment',
        required=True,
        index=True,
    )
    contract_id = fields.Many2one('rental.contract', string='Contract')
    period_start = fields.Date(string='Period Start')
    period_end = fields.Date(string='Period End')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    revenue = fields.Monetary(
        string='Revenue',
        currency_field='currency_id',
        compute='_compute_financials',
        store=True,
    )
    fuel_cost = fields.Monetary(
        string='Fuel Cost',
        currency_field='currency_id',
        compute='_compute_financials',
        store=True,
    )
    repair_cost = fields.Monetary(
        string='Repair Cost',
        currency_field='currency_id',
        compute='_compute_financials',
        store=True,
    )
    expense_cost = fields.Monetary(
        string='Other Expenses',
        currency_field='currency_id',
        compute='_compute_financials',
        store=True,
    )
    total_cost = fields.Monetary(
        string='Total Cost',
        currency_field='currency_id',
        compute='_compute_financials',
        store=True,
    )
    profit = fields.Monetary(
        string='Profit',
        currency_field='currency_id',
        compute='_compute_financials',
        store=True,
    )
    margin_pct = fields.Float(
        string='Margin %',
        compute='_compute_financials',
        store=True,
        digits=(5, 2),
    )

    @api.depends(
        'equipment_id', 'contract_id', 'period_start', 'period_end'
    )
    def _compute_financials(self):
        for rec in self:
            domain_eq = [('equipment_id', '=', rec.equipment_id.id)]
            domain_ct = [('contract_id', '=', rec.contract_id.id)] if rec.contract_id else []

            # Revenue from contract lines
            if rec.contract_id:
                lines = self.env['rental.contract.line'].search(
                    [('contract_id', '=', rec.contract_id.id),
                     ('equipment_id', '=', rec.equipment_id.id)]
                )
            else:
                lines = self.env['rental.contract.line'].search(domain_eq)
            rec.revenue = sum(lines.mapped('subtotal'))

            # Fuel costs
            fuel_domain = domain_eq[:]
            if rec.contract_id:
                fuel_domain += [('contract_id', '=', rec.contract_id.id)]
            if rec.period_start:
                fuel_domain += [('date', '>=', rec.period_start)]
            if rec.period_end:
                fuel_domain += [('date', '<=', rec.period_end)]
            fuels = self.env['rental.fuel.log'].search(fuel_domain)
            rec.fuel_cost = sum(fuels.mapped('total_cost'))

            # Repair costs
            jobs = self.env['rental.workshop.job'].search(domain_eq)
            rec.repair_cost = sum(jobs.mapped('cost')) + sum(
                jobs.mapped('total_parts_cost')
            )

            # Other expenses
            exp_domain = domain_eq[:]
            if rec.contract_id:
                exp_domain += [('contract_id', '=', rec.contract_id.id)]
            expenses = self.env['rental.expense'].search(exp_domain)
            rec.expense_cost = sum(expenses.mapped('amount'))

            rec.total_cost = rec.fuel_cost + rec.repair_cost + rec.expense_cost
            rec.profit = rec.revenue - rec.total_cost
            if rec.revenue:
                rec.margin_pct = (rec.profit / rec.revenue) * 100
            else:
                rec.margin_pct = 0.0

    def action_recompute(self):
        self._compute_financials()
