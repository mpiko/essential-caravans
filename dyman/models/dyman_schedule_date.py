from odoo import fields, models, api


class ScheduleDate(models.Model):
    _name = 'dyman.schedule.date'
    _description = "Schedule Wizard"

    name = fields.Char(string="Name", compute="_get_name", store=True)
    date = fields.Date(string="Date")
    schedule_id = fields.Many2one("dyman.schedule", string="Schedule")

    @api.depends("date")
    def _get_name(self):
        for record in self:
            if record.date:
                record.name = f'{record.date: %b %d, %Y}'
            else:
                record.name = "Unscheduled"