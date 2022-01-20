from datetime import datetime, date, timedelta
import locale
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import UserError
from datetime import timedelta, date, datetime
from io import BytesIO
import xlwt, base64
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from operator import itemgetter
import os 
from odoo import http
import requests

class Ventasreport(models.Model):
    _name = 'wizard.sitef'
    _description = 'Sitef Funciones Generales'

    sitef_restApi = fields.Char(default="http://localhost:5000") 
    tipo_funcion = fields.Selection([
        ('anulacion', 'Anulación'),       
        ('cierre', 'Cierre'),
        ('admin', 'Operaciones Administrativas')
    ], default='admin')

    ##
    
    def getSitefScript(self):
        #sitef_restApi='http://localhost:5000'
          
        url=f'{sitef_restApi}/sitef.js'
        try:
            rs=requests.get(url)
            sitef_script=rs.text+f'; return getSitef("{self.sitef_restApi}",$);'
            return sitef_script
        except:
            return None
            
    #sitef_script=fields.Char(default=lambda self: self.getSitefScript())
