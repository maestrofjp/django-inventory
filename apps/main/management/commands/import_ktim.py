# -*- encoding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from main.conf import settings

import optparse
import logging
from main import mysql_suck as M

def custom_options(parser):
    M.MyS_Connector.add_mysql_options(parser)
    pgroup = optparse.OptionGroup(parser, "Iteration options")
    pgroup.add_option('--limit', type=int, help="Limit of forms to import"),
    pgroup.add_option('--dry-run', action="store_true", default=False,
                help="Don't change anything")
    pgroup.add_option('--slice', type=int,
                help="Slice of records to process at a time"),


class Command(BaseCommand):
    args = '<table ...>'
    help = 'Imports table from old Ktim. database'
    _myc = None
    _tables = []

    def create_parser(self, prog_name, subcommand):
        parser = super(Command, self).create_parser(prog_name, subcommand)
        custom_options(parser)
        return parser

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.DEBUG)
        self._init_tables()

        for d in settings.defaults:
            if options.get(d, None) is None:
                options[d] = settings.defaults[d]

        if not self._myc.connect(options, load=True):
            self.stderr.write("Cannot connect to MySQL!\n")
            return
        self.stderr.write("Connected. Start of sync\n")

        self._myc.run_all( args or ['KT_01_ANADOXOI',
                'KT_03_EIDOS',
                'KT_08_KATASKEYASTHS',
                'KT_05_PROIONTA',
                'KT_11_MANAGERS',
                'KT_16_ANATH_ARXH',
                'KT_18_ERGA',
                'KT_06_YPOERGA',
                'MONADES',
                ], **options)
        self._myc.close(save=True)
        return

    def _init_tables(self):
        self._myc = myc = M.MyS_Connector()
        
        anadoxoi = M.Table_Suck('KT_01_ANADOXOI', 'procurements.Delegate', myc)
        anadoxoi += M.IDmap_Column('ANADOXOS_ID')
        anadoxoi += M.Str_Column('ANADOXOS_DESCR', 'name')
        anadoxoi += M.Str_Column('WEB', 'web')
        anadoxoi_addr = M.Contain_Column('common.Address', 'partner')
        anadoxoi += anadoxoi_addr
        anadoxoi_addr += M.Str_Column('CONTACT_PERSON', 'name')
        anadoxoi_addr += M.Str_Column('TELEPHONE', 'phone1')
        anadoxoi_addr += M.Str_Column('CONTACT_TEL', 'phone2')

        # TODO KT_02_BUNDLES

        product_cat = M.Table_Suck('KT_03_EIDOS', 'products.ItemCategory', myc)
        product_cat += M.IDmap_Column('EIDOS_ID')
        product_cat += M.Str_Column('EIDOS_DESCR', 'name')
        # product_cat += M.Bool_Column('IS_BUNDLE', 'is_bundle')
        #product_cat += M.Static_Ref_Column(dict(parent_id=False),
        #        'parent_id', 'products.ItemCategory') TODO


        products = M.Table_Suck('KT_05_PROIONTA', 'product.ItemTemplate', myc)
        products += M.IDmap_Column('PROION_ID')
        products += M.Str_Column('PROION_DESCR', 'description')
        products += M.Ref_Column('KATASK_ID', 'manufacturer', 'KT_08_KATASKEYASTHS')
        products += M.Ref_Column('EIDOS_ID', 'category', 'KT_03_EIDOS')
        # products += M.Static_Column('product', 'type')

        # KT_08_KATASKEYASTHS
        katask = M.Table_Suck('KT_08_KATASKEYASTHS', 'products.Manufacturer', myc)
        katask += M.IDmap_Column('KATASK_ID')
        katask += M.Str_Column('KATASK_DESCR', 'name')
        katask += M.Str_Column('WEB', 'web')

        # KT_11_MANAGERS
        managers = M.Table_Suck('KT_11_MANAGERS', 'company.Department', myc)
        managers += M.IDmap_Column('MANAGER_ID')
        managers += M.Str_Column('SHORT_DESCRIPTION', 'name')
        managers += M.Static_Ref_Column(dict(name=u'ΠΔΕ'), 'dept_type_id', 'company.DepartmentType')
        
        # All rest of columns are not set in old db, anyway...
        #managers += M.Str_Column('WEB', 'website')
        #managers += M.Str_Column('DESCRIPTION', 'description')
        #managers_addr = M.M2O_Column('address_id', 'res.partner.address')
        #managers += managers_addr
        #managers_addr += M.Str_Column_Required('CONTACT_PERSON', 'name')
        #managers_addr += M.Str_Column('TELEPHONE', 'phone')
        #managers_addr += M.Str_Column('CONTACT_TEL', 'mobile')

        #TODO KT_14_ONTOTHTES

        # KT_16_ANATH_ARXH
        anath = M.Table_Suck('KT_16_ANATH_ARXH', 'company.Department', myc)
        anath += M.IDmap_Column('ANATHETOUSA_ARXH')
        anath += M.Str_Column('ARXH_DESCR', 'name')
        anath += M.Static_Ref_Column(dict(name=u'Αναθέτουσα αρχή'), 'dept_type_id', 'company.DepartmentType')
        
        #anath += M.Str_Column('WEB', 'website')
        #anath_addr = M.Contain_Column('common.Address', 'address')
        #anath += anath_addr
        #anath_addr += M.Str_Column('CONTACT_PERSON', 'name')
        #anath_addr += M.Str_Column('TELEPHONE', 'phone')
        #anath_addr += M.Str_Column('CONTACT_TEL', 'mobile')
        #anath += M.Static_Ref2M_Column([('id.ref', '=', 'ktimatologio.partner_cat_anath')],
        #        'category_id', 'res.partner.category')


        # KT_18_ERGA
        erga = M.Table_Suck('KT_18_ERGA', 'procurements.Project', myc)
        erga += M.IDmap_Column('ERGO_ID')
        erga += M.Str_Column('ERGO_DESCR', 'description')
        erga += M.Str_Column('ERGO_SHORT_DESCR', 'name')

        # KT_06_YPOERGA
        ypoerga = M.Table_Suck('KT_06_YPOERGA', 'procurements.Contract', myc)
        ypoerga += M.IDmap_Column('YPOERGO_ID')
        ypoerga += M.Str_Column('YPOERGO_DESCR', 'description')
        ypoerga += M.Str_Column('YPOERGO_SHORT_DESCR', 'name')
        ypoerga += M.Date_Column('DATE_SIGN', 'date_start')
        ypoerga += M.Date_Column('END_DATE', 'end_date')
        ypoerga += M.Str_Column('DIARKEIA_EGYHSHS', 'warranty_dur')
        ypoerga += M.Str_Column('XRONOS_APOKRISHS', 'service_response')
        ypoerga += M.Str_Column('XRONOS_APOKATASTASHS', 'repair_time')
        ypoerga += M.Str_Column('FILE_NAME', 'kp_filename')
        #ypoerga += M.Str_Column('TYPE_OF_ANATHETOUSA', 'kp_type')
        # FIXME: they should set "partner" from the subclass'es partner
        ypoerga += M.Ref_NN_Column('ANATH_FOREAS_ID', 'partner', 'KT_11_MANAGERS')
        ypoerga += M.Ref_NN_Column('ANATH_OTHER_ID', 'partner', 'KT_16_ANATH_ARXH')
        ypoerga += M.Ref_Column('ERGO_ID', 'parent_id', 'KT_18_ERGA')
        ypoerga += M.Ref_Column('ANADOXOS_ID', 'delegate', 'KT_01_ANADOXOI')

        #TODO KT_07_KTHMATOLOGIO

        # MONADES
        monades = M.Table_Suck('MONADES', 'company.Department', myc)
        monades += M.IDmap_Column('GLUC')
        monades += M.Str_Column('GLUC', 'code')
        monades += M.Str_Column('YPEPTH_ID', 'code2')
        monades += M.Str_Column('ONOMASIA', 'name')
        monades += M.StrLookup_Column('TYPOS_ONOMA', 'dept_type_id', 'company.DepartmentType')
        monades += M.Str_Column('DNSH_ONOMA', 'section_name')
        monades += M.Str_Column('OTA_ONOMA', 'ota_name')
        monades += M.Str_Column('NOM_ONOMA', 'nom_name')
        # TODO monades += M.XXX_Column('MANAGER_ID', '??') # foreas
        monades += M.Enum2Bool_Column('KATARGHSH', 'deprecate')
        monades += M.Ref_Column('SYGXONEYSH_GLUC', 'merge_id', 'MONADES')

        self._tables += [ anadoxoi, product_cat, products, katask, anath,
                managers, erga, ypoerga, monades ]

#eof
