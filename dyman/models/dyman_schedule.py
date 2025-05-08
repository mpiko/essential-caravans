from odoo import api, fields, models
from odoo.exceptions import ValidationError
import datetime

class Schedule(models.Model):
    _name = 'dyman.schedule'
    _description = "Schedule Wizard"

    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    schedule_order_ids = fields.One2many("dyman.schedule.order", "schedule_id", string="Orders")

    @api.onchange('date_from', 'date_to')
    def _validate_dates(self):

        if self.date_from and self.date_to:
            if self.date_to < self.date_from:
                raise ValidationError("To date must be after from date" )

    def _create_schedule_dates(self):
        self.env['dyman.schedule.date'].search([]).unlink()
        vals = {
                'schedule_id': self.id
                }
        self.env['dyman.schedule.date'].create(vals)       

        date = self.date_from
        while date <= self.date_to:
            if date.weekday() < 5:
                vals = {
                        'date': date,
                        'schedule_id': self.id
                        }
                self.env['dyman.schedule.date'].create(vals)
            date += datetime.timedelta(days=1)

    def action_view_orders(self):
    
        self._create_schedule_dates()
        self.env['dyman.schedule.order'].search([]).unlink()

        for order in self.env['dyman.order'].search(['|',('schedule_date_online','=',False),'&',('schedule_date_online','>=',self.date_from),('schedule_date_online','<=',self.date_to)]):
            
            date = self.env['dyman.schedule.date'].search([('schedule_id','=',self.id),('date','=',order.schedule_date_online)])
            vals = {
                    'schedule_id': self.id,
                    'order_id': order.id,
                    'schedule_date_online_id': date[0].id
                    }
            self.env['dyman.schedule.order'].create(vals)
        return {
                'name': 'Schedule order',
                'view_mode': 'kanban',
                'view_id': self.env.ref('dyman.dyman_schedule_order_kanban').id,
                'res_model': 'dyman.schedule.order',
                'type': 'ir.actions.act_window'
                }