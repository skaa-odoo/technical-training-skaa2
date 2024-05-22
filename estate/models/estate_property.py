from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_compare, float_is_zero

class estate_property(models.Model):
    _name = "estate.property"
    _description = "Real Estate Properties!"
    _order = "id desc"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    availability_date = fields.Date(default=fields.Date.today()+relativedelta(months=3), copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, default=None, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string = 'Orientation',
        selection=[('north','North'), ('south','South') , ('east','East'), ('west','West')],
        help='Choose the Direction.')
    active = fields.Boolean(default=False)
    status = fields.Selection(
        string='Select',
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')],
        default="new",
        required=True)
    property_type_id = fields.Many2one('estate.property.type', string="Type")
    salesperson_id = fields.Many2one('res.users', string="Salesperson", default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    
    property_tag_ids = fields.Many2many('estate.property.tag', string="Tag")
    
    offer_ids = fields.One2many("estate.property.offer", "property_id")

    total_area = fields.Integer(compute="_compute_total_area")

    set_unsold = fields.Boolean(default=False)

    @api.onchange("set_unsold")
    def __onchange_set_unsold(self):
        if (self.set_unsold==True):
            if(self.offer_ids): self.status="offer_received"
            else:   self.status="new"

    @api.onchange("offer_ids")
    def __onchange_offer_ids_set_state(self):
        if self.offer_ids:  self.status="offer_received"
        else:   self.status="new"
    
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        self.total_area=self.living_area + self.garden_area

    best_offer = fields.Float(compute="_compute_best_offer")

    @api.depends("offer_ids.price")
    def _compute_best_offer(self):
        self.best_offer=max(self.offer_ids.mapped("price")) if self.offer_ids else 0.0

    @api.onchange("garden")
    def __onchange_garden(self):
            if(self.garden==True):
                self.garden_area=10
                self.garden_orientation='north'
            else:
                self.garden_area=0
                self.garden_orientation=None

    def action_sold(self):
        if self.status=="cancelled":
            raise UserError("Cancelled properties cannot be sold!")
        self.status='sold'
        return True

    def action_cancel(self):
        if self.status=="sold":
            raise UserError("Sold properties cannot be cancelled!")
        self.status='cancelled'
        return True
    
    _sql_constraints = [('check_expected_price', 'CHECK(expected_price>0)', 'The expected price should be positive.'), 
                        ('check_selling_price', 'CHECK(selling_price>=0)', 'The selling price should be positive.')]

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        if(not float_is_zero(self.selling_price, precision_rounding=0.01) and float_compare(self.selling_price, 0.9*self.expected_price, precision_rounding=0.01)==-1):
            raise ValidationError("Selling Price cannot be less than 90% of the Expected Price")
        
    @api.ondelete(at_uninstall=False)
    def unlink_on_valid_state(self):
        if not (self.status=="new" or self.status=="cancelled"):
            raise UserError("A property can only be deleted in a new or a cancelled state!")
        return True
