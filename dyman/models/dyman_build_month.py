from odoo import api, fields, models

class BuildMonth(models.Model):
    _name = "dyman.build.month"
    _description = "Build month"
    _sql_constraints = [('unique_year_month', 'unique(year, month)', 'Month already exists')]

    name = fields.Char(string='Name', compute="_get_name", store=True)
    year = fields.Many2one("dyman.build.year", string="Year", required=True, ondelete="cascade")
    month = fields.Selection(selection=[('01', 'January'),('02', 'February'),('03', 'March'),('04', 'April'),('05', 'May'),('06', 'June'),('07', 'July'),('08', 'August'),('09', 'September'),('10', 'October'),('11', 'November'),('12', 'December')], string="Month", required=True)
    status = fields.Selection(selection=[('open', 'Open'),('closed', 'Closed')], string="Status", default="open")

    @api.depends('year', 'month')
    def _get_name(self):
        for record in self:
            record.name = record._create_name()

    def _create_name(self):
        name = ""
        if self.year:
            if self.month:
                name = str(self.year.name) + "-" + self.month
        return name