from odoo import models,fields,api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class Offer(models.Model):
    _name='estate.property.offer'
    _description='Estate property offer description'
    _order="price desc"

    price = fields.Float()
    status = fields.Selection(selection=[('accepted','Accepted'),('refused','Refused')],copy=False,readonly=True)
    partner_id = fields.Many2one("res.partner",required=True)
    property_id = fields.Many2one("estate.property",required=True, readonly=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one(related="property_id.property_type_id")
    
    @api.depends("validity")
    def _compute_date_deadline(self):
        for it in self:
            it.date_deadline = fields.Date.today() + relativedelta(days=it.validity)

    @api.depends("date_deadline")
    def _inverse_date_deadline(self):
        for it in self:
            it.validity=(it.date_deadline-fields.Date.today()).days

    def action_accept(self):
        if(self.property_id.status=='sold'):
            raise UserError("An offer is already accepted!!")
        self.status='accepted'
        self.property_id.buyer_id=self.partner_id
        self.property_id.selling_price=self.price
        self.property_id.status='sold'
        for it in self.property_id.offer_ids:
            if(it.status!='accepted'): it.status='refused'
        return True
    
    def action_refuse(self):
        if(self.status=='accepted'):
            self.property_id.buyer_id=None
            self.property_id.selling_price=0.0
            self.property_id.status='offer_received'
            for it in self.property_id.offer_ids:
                if(it.status=='accepted'): it.status='refused'
        self.status="refused"
        return True

    @api.model
    def create(self, vals):
        if vals.get("property_id") and vals.get("price"):
            prop = self.env['estate.property'].browse(vals['property_id'])
            if prop.best_offer>vals.get("price"):
                raise UserError("The created offer cannot be lower than any existing offer!")  
        return super().create(vals)
 
    _sql_constraints=[('check_price', 'CHECK(price>0)', 'The offered price must be positive.')]
