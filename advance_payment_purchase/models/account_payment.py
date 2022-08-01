# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    is_advance_pay = fields.Boolean(string='Is Advance Payment')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order',
                                        domain="[('partner_id', '=', partner_id)]")
    advance_amount = fields.Float(string='Advance Amount', compute='_compute_purchase_order_id')

    @api.depends('purchase_order_id')
    def _compute_purchase_order_id(self):
        records = self.env['account.payment'].search(
            ['&', ('state', '=', 'posted'), ('is_advance_pay', '=', True),
             ('purchase_order_id', '=', self.purchase_order_id.id)])
        total = 0
        for rec in records:
            total += rec.amount
        ad_amount = self.purchase_order_id.advance_amount - total
        self.advance_amount = ad_amount

    def check_amount(self):
        records = self.env['account.payment'].search(
            ['&', ('state', '=', 'posted'), ('is_advance_pay', '=', True),
             ('purchase_order_id', '=', self.purchase_order_id.id)])
        total = 0
        for rec in records:
            total += rec.amount
        ad_amount = self.purchase_order_id.advance_amount - total
        self.advance_amount = ad_amount
        total += self.amount
        if total > self.purchase_order_id.advance_amount:
            raise UserError('Advance has already been paid')
        print(total)

    def button_approved(self):
        print('action post')
        if self.purchase_order_id:
            self.check_amount()
        records = self.env['account.payment'].search(
            ['&', ('state', '=', 'posted'), ('is_advance_pay', '=', True),
             ('purchase_order_id', '=', self.purchase_order_id.id)])
        total = 0
        for rec in records:
            total += rec.amount
        ad_amount = self.purchase_order_id.advance_amount - total
        self.advance_amount = ad_amount
        total += self.amount
        if total == self.purchase_order_id.advance_amount:
            self.purchase_order_id.payment_state = 'paid'
            print('paid')
        if total < self.purchase_order_id.advance_amount:
            self.purchase_order_id.payment_state = 'partial'
            print('partial')
        self.write({
            'state': 'posted'
        })
        for payment in self:
            # if payment.payment_invoice_ids:
            #     if payment.amount < sum(payment.payment_invoice_ids.mapped('reconcile_amount')):
            #         raise UserError(_("stop the function."))
            print('=====payment method_id====',payment.payment_method_id)
            for line_id in payment.payment_invoice_ids:
                if not line_id.reconcile_amount:
                    continue
                if line_id.amount_total <= line_id.reconcile_amount:
                    self.ensure_one()
                    if payment.payment_type == 'inbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0 and line.credit == line_id.reconcile_amount and line.branch_id.id == line_id.branch_id.id)
                        lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.reconcile()
                    elif payment.payment_type == 'outbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.debit > 0 and line.debit == line_id.reconcile_amount and line.branch_id.id == line_id.branch_id.id)
                        lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.reconcile()
                else:
                    self.ensure_one()
                    if payment.payment_type == 'inbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0 and line.credit == line_id.reconcile_amount and line.branch_id.id == line_id.branch_id.id)
                        lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.with_context(amount=line_id.reconcile_amount).reconcile()
                    elif payment.payment_type == 'outbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.debit > 0 and line.debit == line_id.reconcile_amount and line.branch_id.id == line_id.branch_id.id)
                        lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.with_context(amount=line_id.reconcile_amount).reconcile()
        self.move_id._post(soft=False)

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.journal_id.payment_debit_account_id or not self.journal_id.payment_credit_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
                self.journal_id.display_name))

        # Compute amounts.
        write_off_amount = write_off_line_vals.get('amount', 0.0)

        if self.payment_type == 'inbound':
            # Receive money.
            counterpart_amount = -self.amount
            write_off_amount *= -1
        elif self.payment_type == 'outbound':
            # Send money.
            counterpart_amount = self.amount
        else:
            counterpart_amount = 0.0
            write_off_amount = 0.0

        balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id, self.date)
        counterpart_amount_currency = counterpart_amount
        write_off_balance = self.currency_id._convert(write_off_amount, self.company_id.currency_id, self.company_id, self.date)
        write_off_amount_currency = write_off_amount
        currency_id = self.currency_id.id

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else: # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )
        line_vals_list = []
        if self.is_multi_branch == 'yes' and self.payment_type == 'outbound':
            print('hello')
            line_vals_list = [
                # Liquidity line.
                {
                    'name': liquidity_line_name or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': -counterpart_amount_currency,
                    'currency_id': currency_id,
                    'debit': balance < 0.0 and -balance or 0.0,
                    'credit': balance > 0.0 and balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id,
                    'branch_id': self.branch_id.id,
                    'analytic_tag_ids': self.branch_id.analytical_tag_id.ids,
                },
            ]
            # Receivable / Payable.
            for p_line in self.payment_invoice_ids:
                line_vals_list.append({
                    'name': self.payment_reference or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': p_line.reconcile_amount or 0.0,
                    'currency_id': currency_id,
                    'debit': p_line.reconcile_amount or 0.0,
                    'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.destination_account_id.id,
                    'branch_id': p_line.branch_id.id,
                    'analytic_tag_ids': p_line.branch_id.analytical_tag_id.ids,
                })

            if write_off_balance:
                # Write-off line.
                line_vals_list.append({
                    'name': write_off_line_vals.get('name') or default_line_name,
                    'amount_currency': -write_off_amount_currency,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': write_off_line_vals.get('account_id'),
                })
            return line_vals_list
        elif self.is_multi_branch == 'yes' and self.payment_type == 'inbound':
            line_vals_list = [
                # Liquidity line.
                {
                    'name': liquidity_line_name or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': -counterpart_amount_currency,
                    'currency_id': currency_id,
                    'debit': balance < 0.0 and -balance or 0.0,
                    'credit': balance > 0.0 and balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id,
                    'branch_id': self.branch_id.id,
                    'analytic_tag_ids': self.branch_id.analytical_tag_id.ids,
                },
                # Receivable / Payable.
                # {
                #     'name': self.payment_reference or default_line_name,
                #     'date_maturity': self.date,
                #     'amount_currency': counterpart_amount_currency + write_off_amount_currency if currency_id else 0.0,
                #     'currency_id': currency_id,
                #     'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                #     'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                #     'partner_id': self.partner_id.id,
                #     'account_id': self.destination_account_id.id,
                # },
            ]
            for p_line in self.payment_invoice_ids:
                line_vals_list.append({
                    'name': self.payment_reference or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': p_line.reconcile_amount or 0.0,
                    'currency_id': currency_id,
                    'debit': 0.0,
                    'credit': p_line.reconcile_amount or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.destination_account_id.id,
                    'branch_id': p_line.branch_id.id,
                    'analytic_tag_ids': p_line.branch_id.analytical_tag_id.ids,
                })
            print(line_vals_list)
            if write_off_balance:
                # Write-off line.
                line_vals_list.append({
                    'name': write_off_line_vals.get('name') or default_line_name,
                    'amount_currency': -write_off_amount_currency,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': write_off_line_vals.get('account_id'),
                })
            return line_vals_list
        else:
            line_vals_list = [
                # Liquidity line.
                {
                    'name': liquidity_line_name or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': -counterpart_amount_currency,
                    'currency_id': currency_id,
                    'debit': balance < 0.0 and -balance or 0.0,
                    'credit': balance > 0.0 and balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id,
                },
                # Receivable / Payable.
                {
                    'name': self.payment_reference or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': counterpart_amount_currency + write_off_amount_currency if currency_id else 0.0,
                    'currency_id': currency_id,
                    'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                    'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.destination_account_id.id,
                },
            ]
            if write_off_balance:
                # Write-off line.
                line_vals_list.append({
                    'name': write_off_line_vals.get('name') or default_line_name,
                    'amount_currency': -write_off_amount_currency,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': write_off_line_vals.get('account_id'),
                })
            return line_vals_list
    #
    # def _synchronize_to_moves(self, changed_fields):
    #     ''' Update the account.move regarding the modified account.payment.
    #     :param changed_fields: A list containing all modified fields on account.payment.
    #     '''
    #     if self._context.get('skip_account_move_synchronization'):
    #         return
    #
    #     if not any(field_name in changed_fields for field_name in (
    #         'date', 'amount', 'payment_type', 'partner_type', 'payment_reference', 'is_internal_transfer',
    #         'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id',
    #     )):
    #         return
    #
    #     for pay in self.with_context(skip_account_move_synchronization=True):
    #         liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
    #
    #         # Make sure to preserve the write-off amount.
    #         # This allows to create a new payment with custom 'line_ids'.
    #
    #         if writeoff_lines:
    #             writeoff_amount = sum(writeoff_lines.mapped('amount_currency'))
    #             counterpart_amount = counterpart_lines['amount_currency']
    #             if writeoff_amount > 0.0 and counterpart_amount > 0.0:
    #                 sign = 1
    #             else:
    #                 sign = -1
    #
    #             write_off_line_vals = {
    #                 'name': writeoff_lines[0].name,
    #                 'amount': writeoff_amount * sign,
    #                 'account_id': writeoff_lines[0].account_id.id,
    #             }
    #         else:
    #             write_off_line_vals = {}
    #
    #         line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
    #
    #         line_ids_commands = [
    #             (1, liquidity_lines.id, line_vals_list[0]),
    #             (1, counterpart_lines.id, line_vals_list[1]),
    #         ]
    #
    #         for line in writeoff_lines:
    #             line_ids_commands.append((2, line.id))
    #
    #         if writeoff_lines:
    #             line_ids_commands.append((0, 0, line_vals_list[2]))
    #
    #         # Update the existing journal items.
    #         # If dealing with multiple write-off lines, they are dropped and a new one is generated.
    #
    #         pay.move_id.write({
    #             'partner_id': pay.partner_id.id,
    #             'currency_id': pay.currency_id.id,
    #             'partner_bank_id': pay.partner_bank_id.id,
    #             'line_ids': line_ids_commands,
    #         })


    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                # if len(liquidity_lines) != 1 or len(counterpart_lines) != 1:
                #     raise UserError(_(
                #         "The journal entry %s reached an invalid state relative to its payment.\n"
                #         "To be consistent, the journal entry must always contains:\n"
                #         "- one journal item involving the outstanding payment/receipts account.\n"
                #         "- one journal item involving a receivable/payable account.\n"
                #         "- optional journal items, all sharing the same account.\n\n"
                #     ) % move.display_name)

                if writeoff_lines and len(writeoff_lines.account_id) != 1:
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, all the write-off journal items must share the same account."
                    ) % move.display_name)

                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same currency."
                    ) % move.display_name)

                if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same partner."
                    ) % move.display_name)

                if counterpart_lines.account_id.user_type_id.type == 'receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'payment_type': 'inbound' if liquidity_amount > 0.0 else 'outbound',
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))

