# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from num2words import num2words
from openerp.exceptions import ValidationError
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import dateutil.parser,timeago
from odoo.addons import decimal_precision as dp
# class funding_request_management(models.Model):
#     _name = 'funding_request_management.funding_request_management'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
class ResUsers(models.Model):
    _inherit = 'res.users'

    title = fields.Char('Title')
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    request_bill_id = fields.Many2one('funding_request_management.request',
        ondelete='set null')
    reference = fields.Char("Payment Voucher Ref")
class SubPayments(models.Model):
    _name = 'funding_request_management.sub_payments'
    @api.model
    def _default_description(self):
        for r in self:
            last_payment=r.request_id.sub_payment_line_ids.ids[-1] or False
            if last_payment:
                return self.env['funding_request_management.sub_payments'].search([('id','=',last_payment)],limit=1).description

    name = fields.Char(string="Payment Voucher.",required=True)
    date = fields.Date("Date",default=datetime.today())
    payee = fields.Char(string="Payee",required=True)
    description = fields.Char(string="description",required=True,default=_default_description)
    amount = fields.Float(string="Amount",required=True)
    amount_in_words = fields.Char(string="Amount in words",compute='_get_amount_in_words')
    request_id = fields.Many2one('funding_request_management.request',
        ondelete='cascade', required=True)
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ],default='cash', string="Payment",required=True)
    state  = fields.Selection([
        ('Submitted', 'Submitted'),
        ('Approved(Director)', 'Approved(Director)'),
        ('Approved(Manager)', 'Approved(Manager)'),
        ],default='Submitted', string="State",required=True)
    approve_manager_id = fields.Many2one('res.users', string="Approve By",domain=lambda self: [("groups_id", "=", self.env.ref( "funding_request_management.group_manager").id)])
    approve_director_id = fields.Many2one('res.users', string="Approved Director",domain=lambda self: [("groups_id", "=", self.env.ref( "funding_request_management.group_can_approve").id)])

    @api.multi
    def manager_approve(self):
        for r in self:
            if not r.approve_manager_id:
                self.write({'approve_manager_id':self.env.user.id,'state':'Approved(Manager)'})
            else:
                raise ValidationError('Payment Voucher is already approved by '+str(r.approve_manager_id.name))
    @api.multi
    def director_approve(self):
        for r in self:
            if not r.approve_director_id:
                self.write({'approve_director_id':self.env.user.id,'state':'Approved(Director)'})
            else:
                raise ValidationError('Payment Voucher is already approved by '+str(r.approve_director_id.name))

    @api.multi
    def director_disapprove(self):
        for r in self:
            if r.approve_director_id and r.approve_director_id.id != self.env.user.id:
                raise ValidationError('Only '+str(r.approve_director_id.name)+' can unapprove this request')
            else:
                self.write({'state':'Submitted','approve_director_id':False,'approve_manager_id':False})
    @api.multi
    def manager_disapprove(self):
        for r in self:
            if r.approve_manager_id and r.approve_manager_id.id != self.env.user.id:
                raise ValidationError('Only '+str(r.approve_manager_id.name)+' can unapprove this request')
            else:
                self.write({'state':'Approved(Director)','approve_manager_id':False})
    '''
    @api.model
    def create(self, vals):
        prefix          =   "PV"
        code            =   "funding_request_management.sub_payments"
        name            =   prefix+"_"+code
        implementation  =   "no_gap"
        padding  =   "3"
        dict            =   { "prefix":prefix,
        "code":code,
        "name":name,
        "active":True,
        "implementation":implementation,
        "padding":padding,
        "company_id":False
        }
        if self.env['ir.sequence'].search([('code','=',code)]).code == code:
            vals['name'] =  self.env['ir.sequence'].next_by_code('funding_request_management.sub_payments')
        else:
            new_seq = self.env['ir.sequence'].create(dict)
            vals['name']    =   self.env['ir.sequence'].next_by_code(code)
        result = super(SubPayments, self).create(vals)
        return result
    '''

    @api.depends('amount')
    def _get_amount_in_words(self):
        for r in self:
            r.amount_in_words= num2words(r.amount)
    @api.multi
    def _default_description(self):
        description = "heyy"
        return description
class Request(models.Model):
    _name = 'funding_request_management.request'
    _description = "FaceForm Request"
    _inherit = ['mail.thread']
    @api.depends('date_submitted')
    def count_days(self):
        DATETIME_FORMAT = "%Y-%m-%d"
        for r in self:
            date = datetime.today().strftime('%Y-%m-%d')
            date_submitted = fields.Datetime.from_string(r.date_submitted)
            today = fields.Datetime.from_string(date)
            difference = today - date_submitted
            days = timeago.format(dateutil.parser.parse(r.date_submitted).date(), datetime.today())
            r.days = days


    @api.model
    @api.depends('date_submitted')
    def _get_due_date(self):
        for r in self:
            r.due_date= dateutil.parser.parse(r.date_submitted).date() + relativedelta(months = 3)
    @api.model
    def _get_id_ref_num(self):
        for r in self:
            r.id_ref_num = str(r.id)
        #return dateutil.parser.parse(self.date_submitted).date() + timedelta(days=93)

            #return dateutil.parser.parse(r.date_submitted).date() + timedelta(days=93)
            #return dateutil.parser.parse(r.date_submitted).date() + relativedelta(months=+3)
    id_ref_num = fields.Char(compute=_get_id_ref_num)
    name = fields.Char(required=True,string="Refer")
    partner_id = fields.Many2one('res.partner', string="Partner",required=True)
    country = fields.Char(string="Country",default='NEZ-Office-SC(3920/006/101)')
    programme_code = fields.Char()
    projet_code = fields.Char()
    responsible = fields.Many2many('res.users', string="Responsible Officer(s)")
    approve_by = fields.Many2one('res.users', string="Approve By",domain=lambda self: [("groups_id", "=", self.env.ref( "funding_request_management.group_can_approve").id)],required=True)
    type_of_request  = fields.Selection([
        ('direct_cash_transfer', 'Direct Cash Transer (DCT)'),
        ('reimbursement', 'Reimbursement'),
        ('direct_payment', 'Direct Payment'),
        ('pre_authorization', 'Pre-Authorization'),
        ],default='direct_cash_transfer', string="Type of Request",required=True)
    request_type  = fields.Selection([
        ('faceform', 'FaceForm'),
        ('normal_request', 'Normal Request'),
        ('wfp_request', 'WFP Request'),
        ],default='faceform', string="Type",required=True)
    date_submitted = fields.Date(default=datetime.today())
    due_date = fields.Date(compute=_get_due_date, store=True)
    approved_date = fields.Date(string='Approved date')
    note = fields.Text(string="Notes")
    request_line_ids = fields.One2many(
        'funding_request_management.request.line', 'request_id', string="Request line")
    report_line_ids = fields.One2many(
        'funding_request_management.report.line', 'request_id', string="Report line")
    total_authorized_amount = fields.Float(
         compute='_get_total_report_amount', store=True)
    total_expenditure_amount = fields.Float(
         compute='_get_total_report_amount', store=True)
    @api.depends('report_line_ids')
    def _get_total_report_amount(self):
        for r in self:
            if not r.report_line_ids:
                r.total_authorized_amount = 0
                r.total_expenditure_amount = 0
            else:
                for report_line in r.report_line_ids:
                    r.total_authorized_amount = r.total_authorized_amount + report_line.authorized
                    r.total_expenditure_amount = r.total_expenditure_amount + report_line.expenditure

    sub_payment_line_ids = fields.One2many(
        'funding_request_management.sub_payments', 'request_id', string="Sub Payments")
    total_amount = fields.Float(
        string="Total", compute='_get_total_amount', store=True)
    total_tonnage = fields.Float(
        string="Total", compute='_get_total_tonnage', store=True)
    total_sub_payment = fields.Float(string="Sub payments Total", compute='_get_sub_payment_amount', store=True)
    invoice_id = fields.Many2one(
        'account.invoice',track_visibility='always')
    bill_ids = fields.One2many('account.invoice', 'request_bill_id',string='Bills',track_visibility='always')

    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.user.company_id.id)
    state  = fields.Selection([
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')]
        ,default='submitted', string="State",track_visibility='always')

    bills_count = fields.Integer(compute='_count_bills', string='Expenditure')
    residual = fields.Monetary(string="Authorized Amount Due", related='invoice_id.residual')
    paid = fields.Float(string="Expenditure(Bank)",compute='_compute_paid',default='0.0', store=True)
    received = fields.Float(string="Authorized(Bank)",compute='_compute_received',default='0.0', store=True)
    invoiced = fields.Boolean(string='Invoiced',default=False)
    request = fields.Boolean(string='The funding request shown above ...',default=False)
    report = fields.Boolean(string='The actual expenditures for the period ....',default=False)
    closing_state  = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
        ],default='open',compute='_get_closing_state',store=True)

    days=fields.Char(compute='count_days')
    balance = fields.Float(string="Balance",compute='_compute_balance',default='0.0', store=True)
    authorized_amount_period=fields.Char(string="Authorized Amount period")
    expediture_amount_period=fields.Char(string="Expenditure Amount period")
    request_amount_period=fields.Char(string="Request Amount period")





    '''
    @api.model
    def create(self, vals):
        prefix          =   "FF"
        code            =   "funding_request_management.request"
        name            =   prefix+"_"+code
        implementation  =   "no_gap"
        padding  =   "3"
        dict            =   { "prefix":prefix,
        "code":code,
        "name":name,
        "active":True,
        "implementation":implementation,
        "padding":padding,
        "company_id":False
        }
        if self.env['ir.sequence'].search([('code','=',code)]).code == code:
            vals['name'] =  self.env['ir.sequence'].next_by_code('funding_request_management.request')
        else:
            new_seq = self.env['ir.sequence'].create(dict)
            vals['name']    =   self.env['ir.sequence'].next_by_code(code)
        result = super(Request, self).create(vals)
        return result
    '''
    @api.multi
    def unlink(self):
        for r in self:
            if r.paid !=0 or r.received !=0 or r.total_sub_payment !=0:
                raise ValidationError('You can not delete a request while other objects reference it')

        return super(Request, self).unlink()

    @api.depends('request_line_ids')
    def _get_total_amount(self):
        for r in self:
            if not r.request_line_ids:
                r.total_amount = 0
            else:
                for request_line in r.request_line_ids:
                    r.total_amount = r.total_amount + request_line.request_amount

    @api.depends('request_line_ids')
    def _get_total_tonnage(self):
        for r in self:
            if not r.request_line_ids:
                r.total_tonnage = 0
            else:
                for request_line in r.request_line_ids:
                    r.total_tonnage = r.total_tonnage + request_line.tonnage
    @api.depends('sub_payment_line_ids')
    def _get_sub_payment_amount(self):
        for r in self:
            if not r.sub_payment_line_ids:
                r.total_sub_payment = 0
            else:
                for sub_payment_line in r.sub_payment_line_ids:
                    r.total_sub_payment = r.total_sub_payment + sub_payment_line.amount



    @api.depends('received','paid','total_sub_payment','total_amount','invoice_id','bill_ids')
    def _get_closing_state(self):
        for r in self:
            if  r.total_amount == r.total_sub_payment:
                r.closing_state = 'closed'
            else:
                r.closing_state = 'open'

    @api.onchange('received','paid','total_sub_payment','total_amount','invoice_id','bill_ids')
    def _onchange_for_closed_state(self):
        for r in self:
            if  r.total_amount == r.total_sub_payment:
                r.closing_state = 'closed'
            else:
                r.closing_state = 'open'
    @api.onchange('approve_by')
    def _onchange_approve_by(self):
        for r in self:
            if  r.create_uid and r.create_uid.id != self.env.user.id and r.approve_by:
                raise ValidationError('Only Mr.'+str(r.create_uid.name)+' is able to change this option')

    @api.depends('bill_ids','bill_ids.amount_total','bill_ids.invoice_line_ids.price_unit','bill_ids.state')
    def _compute_paid(self):
        for r in self:
            for invoice in r.bill_ids.filtered(lambda l: l.state not in ['cancel','draft']):
                r.paid=r.paid+invoice.amount_total
    @api.depends('invoice_id','invoice_id.residual','received','invoice_id.payment_ids')
    def _compute_received(self):
        for r in self:
            if r.invoice_id and r.invoice_id.state not in ['cancel','draft']:
                amount_total = r.invoice_id.amount_total
                residual = r.invoice_id.residual
                r.received=float(amount_total - residual)
            else:
                r.received= 0.0
    @api.depends('invoice_id','invoice_id.residual','received','invoice_id.payment_ids','paid')
    def _compute_balance(self):
        for r in self:
            r.balance = r.received - r.paid

    @api.multi
    def action_view_bill(self):
        invoices = self.mapped('bill_ids')
        action = self.env.ref('account.action_invoice_tree2').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_supplier_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    @api.multi
    def approve(self):
        for r in self:
            if r.approve_by.id != self.env.user.id:
                raise ValidationError('Only '+str(r.approve_by.name)+' can approve this request')
            else:
                self.write({'state':'approved','approved_date':datetime.today()})

    @api.multi
    def disapprove(self):
        for r in self:
            if r.approve_by.id != self.env.user.id:
                raise ValidationError('Only '+str(r.approve_by.name)+' can unapprove this request')
            else:
                self.write({'state':'submitted','approved_date':False})



    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_id')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    @api.multi
    def invoice_create(self):
        invoice=self.env['account.invoice']
        invoice_line=self.env['account.invoice.line']
        #company=self.env['res.company']._company_default_get('account.invoice')

        for column in self:
            origin=column.name
            company=column.company_id

        inserted_invoice=invoice.create({
        'origin':origin,
        'type': 'out_invoice',
        'partner_id':self.partner_id.id,
        'name':self.name,
        'account_id':self.env['res.partner'].search([('id','=',self.partner_id.id)]).property_account_receivable_id.id,
        'company_id':company.id,
        'currency_id':company.currency_id.id,
        })
        invoice_line=self.env['account.invoice.line']
        for column in self:
            for request_line in column.request_line_ids:
                invoice_line.create({
                'product_id':request_line.product_id.id,
                'name':str(request_line.description),
                'invoice_id':inserted_invoice.id,
                'price_unit':request_line.request_amount,
                'account_id':self.env['account.account'].search([('id','=',17)],limit=1).id,
                'quantity':1,
                })
        self.write({'invoice_id': inserted_invoice.id,'invoiced':True})

        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
        action['res_id'] = inserted_invoice.id
        return action
    @api.multi
    def bill_create(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]

        #override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice', 'default_request_bill_id': self.id}
        journal_domain = [
            ('type', '=', 'purchase'),
            ('company_id', '=', self.company_id.id),
            ('currency_id', '=', self.company_id.currency_id.id),
            ]
        '''

        ids=[]
        for column in self:
            for request_line in column.request_line_ids:
                invoice_line=self.env['account.invoice.line'].create({
                'product_id':request_line.product_id.id,
                'name':str(request_line.description),
                'price_unit':request_line.request_amount,
                'account_id':self.env['account.account'].search([('id','=',17)],limit=1).id,
                'quantity':1,
                })
                ids.append(invoice_line)

        result['context']['default_invoice_line_ids'] = [(0, False, ids)]
        '''


        default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
        if default_journal_id:
            result['context']['default_journal_id'] = default_journal_id.id
        res = self.env.ref('account.invoice_supplier_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        return result
    @api.multi
    def action_view_bill(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''

        invoices = self.mapped('bill_ids')
        action = self.env.ref('account.action_invoice_tree2').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_supplier_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.one
    def _count_bills(self):
        self.bills_count = len(self.bill_ids.ids)
class RequestLine(models.Model):
    _name = 'funding_request_management.request.line'
    description = fields.Char(string="Activity Description with Duration",required=True)
    product_id = fields.Many2one('product.product',string="Service",domain=[('type', '=', 'service')])
    request_id = fields.Many2one('funding_request_management.request',
        ondelete='cascade', required=True)
    code = fields.Char(string="Coding")
    tonnage = fields.Float(string="Tonnage Distributed", digits=dp.get_precision('Product Price'))
    rate = fields.Float(string="Rate Per Tone", digits=dp.get_precision('Product Price'))
    request_amount = fields.Float(string="Request amount",required=True, digits=dp.get_precision('Product Price'))

    hide = fields.Boolean(string='Hide', compute="_compute_hide",default=True)

    @api.depends('request_id.request_type')
    def _compute_hide(self):
        # simple logic, but you can do much more here
        for r in self:
            if r.request_id.request_type != 'wfp_request':
                r.hide = True
            else:
                r.hide = False

class AuhorizeWizard(models.TransientModel):
    _name = "funding_request_management.add_authorize_wizard"
    _description = "Bulk Payment Recieving"
    @api.model
    def _get_selected_requests(self):
        request_values = []
        requests=self.env['funding_request_management.request'].search([('id','in',self.env.context.get('active_ids'))])
        for request in requests:
            request_values.append(str(request.partner_id.name) + ' (' +str(request.total_amount)+ ')')
        return ' - '.join(request_values)
    name = fields.Text(default=_get_selected_requests)


    def cancel_authorization(self):
        requests=self.env['funding_request_management.request'].search([('id','in',self.env.context.get('active_ids'))])
        for request in requests:
            if request.invoice_id and request.invoice_id.state in ['paid','open','draft']:
                for payment in request.invoice_id.payment_ids:
                    if payment.state == 'posted':
                        payment.cancel()
                request.invoice_id.action_invoice_cancel()
    def print_report(self):
        requests=self.env['funding_request_management.request'].search([('id','in',self.env.context.get('active_ids'))])
        for request in requests:
            if not request.invoice_id:
                request.invoice_create()
class ExpenditureWizard(models.TransientModel):
    _name = "funding_request_management.expenditure_wizard"
    _description = "Bulk Expenditure"
    partner_id = fields.Many2one('res.partner', string="Partner")
    @api.model
    def _get_selected_requests(self):
        request_values = []
        requests=self.env['funding_request_management.request'].search([('id','in',self.env.context.get('active_ids'))])
        for request in requests:
            request_values.append(str(request.partner_id.name) + ' (' +str(request.total_amount)+ ')')
        return ' - '.join(request_values)
    name = fields.Text(default=_get_selected_requests)

    def cancel_expenditure(self):
        requests=self.env['funding_request_management.request'].search([('id','in',self.env.context.get('active_ids'))])
        for request in requests:
            for bill in request.bill_ids.filtered(lambda l: l.state not in ['cancel']):
                for payment in bill.payment_ids:
                    if payment.state == 'posted':
                        payment.cancel()
                bill.action_invoice_cancel()


    def print_report(self):
        if not self.partner_id:
            raise ValidationError('Partner Is required')

        requests=self.env['funding_request_management.request'].search([('id','in',self.env.context.get('active_ids'))])
        invoice=self.env['account.invoice']
        invoice_line=self.env['account.invoice.line']

        for request in requests:
            if not request.received <= request.paid:


                inserted_invoice=invoice.create({
                'type': 'in_invoice',
                'partner_id':self.partner_id.id,
                'name':request.name,
                'request_bill_id':request.id,
                'account_id':self.env['res.partner'].search([('id','=',self.partner_id.id)]).property_account_payable_id.id,
                'company_id':request.company_id.id,
                'currency_id':request.company_id.currency_id.id,
                })
                invoice_line=self.env['account.invoice.line']

                for request_line in request.request_line_ids:
                    invoice_line.create({
                    'product_id':request_line.product_id.id,
                    'name':str(request_line.description),
                    'invoice_id':inserted_invoice.id,
                    'price_unit':request_line.request_amount,
                    'account_id':self.env['account.account'].search([('id','=',19)],limit=1).id,
                    'quantity':1,
                    })
                inserted_invoice.action_invoice_open()
class PrintRequestReport(models.AbstractModel):
    _name = "report.funding_request_management.print_request_report"

    @api.model
    def get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        #request=docs.request
        to=data['to']
        sub=data['sub']
        body=data['body']
        footer=data['footer']
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'data':data
        }
        return docargs
class PrintFaceFormReport(models.AbstractModel):
    _name = "report.funding_request_management.print_faceform_report"

    @api.model
    def get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        #request=docs.request
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'data':data,
        }
        return docargs

        #for request in self.env.context.get('active_ids'):
            #requests=self.env['hitech_service.service'].search([('id','in',self.env.context.get('active_ids'))])
class PrintRequestWizard(models.TransientModel):
    _name = "funding_request_management.print.request.wizard"
    _description = "Print Request"
    @api.model
    def _get_to(self):
        request=self.env['funding_request_management.request'].search([('id','=',self.env.context.get('active_id'))],limit=1)
        return request.partner_id.name
    @api.model
    def _get_sub(self):
        request=self.env['funding_request_management.request'].search([('id','=',self.env.context.get('active_id'))],limit=1)
        request_line =self.env['funding_request_management.request.line'].search([('request_id','=',request.id)],limit=1)
        if request.request_type == 'wfp_request':
            return "Invoice for "
        else:
            return "Request for "+str(request_line.description)


    @api.model
    def _get_body(self):
        request=self.env['funding_request_management.request'].search([('id','=',self.env.context.get('active_id'))],limit=1)
        request_line =self.env['funding_request_management.request.line'].search([('request_id','=',request.id)],limit=1)
        if request.request_type == 'wfp_request':
            body="""
    Dear Sirs/Madams <br></br>
    We are here by requesting from {}, to release ......
    <br></br><br></br>
    The Funds will be transfered through Amal Bank (Garowe Branch) Account #1011687837.
            """.format(request.partner_id.name)

        else:
            body="""
    We are here by requesting from {}, {} which is an Amount of ${:,} ({}).<br></br>
    Please transfer this amount through our bank Account Dahabshiil Garowe GRWD000429.
            """.format(request.partner_id.name, request_line.description,request.total_amount,num2words(request.total_amount))



        return body
    to =fields.Char(default=_get_to)
    sub = fields.Char(default=_get_sub)
    body = fields.Text(default=_get_body)
    footer = fields.Char(default="Regards.")
    def print_request(self):
        request=self.env['funding_request_management.request'].search([('id','=',self.env.context.get('active_id'))],limit=1)
        data = {
        'to': self.to,
        'sub': self.sub,
        'body': self.body,
        'footer': self.footer,
        'request':request}
        return self.env.ref('funding_request_management.action_print_request_report').report_action(self, data=data, config=False)
class ReportLine(models.Model):
    _name = 'funding_request_management.report.line'
    description = fields.Char(string="Activity Description with Duration",required=True)
    authorized = fields.Float(string="Authorised Amount")
    expenditure = fields.Float(string="Actual Project Expenditure")
    request_id = fields.Many2one('funding_request_management.request',
        ondelete='cascade', required=True)

class ApprovalWizard(models.TransientModel):
    _name = "funding_request_management.manage_approval_wizard"
    _description = "Manage Approval"

    def manager_approve(self):
        sub_payments=self.env['funding_request_management.sub_payments'].search([('id','in',self.env.context.get('active_ids'))])
        for payment in sub_payments:
            payment.manager_approve()
    def manager_disapprove(self):
        sub_payments=self.env['funding_request_management.sub_payments'].search([('id','in',self.env.context.get('active_ids'))])
        for payment in sub_payments:
            payment.manager_disapprove()
    def director_approve(self):
        sub_payments=self.env['funding_request_management.sub_payments'].search([('id','in',self.env.context.get('active_ids'))])
        for payment in sub_payments:
            payment.director_approve()
    def director_disapprove(self):
        sub_payments=self.env['funding_request_management.sub_payments'].search([('id','in',self.env.context.get('active_ids'))])
        for payment in sub_payments:
            payment.director_disapprove()
