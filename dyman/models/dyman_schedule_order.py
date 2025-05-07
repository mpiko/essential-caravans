from odoo import fields, models
import datetime

class ScheduleOrder(models.Model):
    _name = 'dyman.schedule.order'
    _description = "Schedule Wizard"

    name = fields.Char(related="order_id.name", string="Name")
    schedule_id = fields.Many2one("dyman.schedule", string="Schedule")
    order_id = fields.Many2one("dyman.order", string="order")
    schedule_date_online_id = fields.Many2one("dyman.schedule.date", string="Scheduled on-line date", group_expand='_group_expand_dates')
    schedule_date_online_date = fields.Date(related="schedule_date_online_id.date", store=True)
    
    def _group_expand_dates(self, states, domain, order):

        return self.env['dyman.schedule.date'].search([])