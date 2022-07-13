# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from odoo.tools import format_time
from pytz import timezone, UTC, utc
from datetime import timedelta
import datetime


# class SaleOrderInh(models.Model):
#     _inherit = "sale.order"
#
#     def action_auto_logout(self):
#         # print(request.env.user.last_activity_time)
#         now_utc_date = datetime.datetime.now()
#         now_dubai = now_utc_date.astimezone(timezone('Asia/Karachi'))
#         print(now_dubai.strftime('%H:%M:%S'))
#         t = now_dubai.strftime('%H:%M:%S')
#         # print(datetime.datetime.now())
#         # print(str(datetime.datetime.today().time()).split(':')[0])
#
#         time_1 = datetime.timedelta(hours=int(request.env.user.last_activity_time.split(' ')[0].split(':')[0]), minutes=int(request.env.user.last_activity_time.split(' ')[0].split(':')[1]), seconds=00)
#         time_2 = datetime.timedelta(hours=abs(int(t.split(':')[0])-12), minutes=int(t.split(':')[1]), seconds=0)
#         print(time_2 - time_1)
#         diff = time_2 - time_1
#         print(diff)
#         print(diff.seconds/60)
#         if diff.seconds/60 >= 3:
#             print('hell')
#         # t = self._compute_last_activity_t()
#         # print(t)
#         # request.session.logout()
