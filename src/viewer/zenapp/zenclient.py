# coding: utf-8
import sys, os, re

sys.path.insert(0, "C:\Users\Alex Sandro\Desktop\Django-1.4")
curdir = os.path.dirname(os.path.abspath(__file__))

pardir = os.path.dirname(curdir)
if not pardir in sys.path: sys.path.append( pardir )

packdir = os.path.join(pardir, "packets")
if not packdir in sys.path: sys.path.append( packdir )

# para executar o script, ele deve estar devidamente configurado.
if __name__ == "__main__":
    basedir = os.path.dirname( pardir )
    if not basedir in sys.path: sys.path.append( basedir )
    basename = os.path.basename( pardir )
    os.environ["DJANGO_SETTINGS_MODULE"] = basename + ".settings"
    
from viewer.main import shared
import zendesk, configobj

# --------------------------------------------------------------------------
def get(attrs, name):
    """ retorna o valor de 'name' não importando sua localização """
    elementFinded = None
    attrsType = type(attrs)

    if attrsType is dict:
        for key in attrs:
            value = attrs[ key ]
            if key == name:
                elementFinded = value
                break
            if type(value) is dict:
                elementFinded = get(value, name)
                if elementFinded: break
    else:
        for item in attrs:
            if type(item) is dict or type(item) is list:
                elementFinded = get(item, name)
                if elementFinded: break
    return elementFinded
# --------------------------------------------------------------------------
def custom_float(value):
    try: value = float(value)
    except: value = 0.0
    return value
# --------------------------------------------------------------------------
pattern = re.compile("(?:^\s+|\s+$)", re.U)
def custom_strip(value):
    try: value = value.decode("utf-8")
    except: pass
    try: value = pattern.sub("", value)
    except: pass
    try: value = value.encode("utf-8")
    except: pass
    return value

############################################################################
crendpath = os.path.join(pardir, "credentials", "cred.cfg")
cred_params = configobj.ConfigObj(crendpath)

class Zendesk(object):
    use_api_token = cred_params.as_bool("use_api_token")
    password = cred_params["password"]
    email = cred_params["email"]
    site = cred_params["url"]
    
    name = "ZENDESK"
    #----------------------------------------------------------------------
    def __init__(self, project_id, year=0, month=0, statistic=None):
        self.zen = zendesk.Zendesk(self.site, self.email, 
            self.password, use_api_token = self.use_api_token,
            client_args = {"disable_ssl_certificate_validation": True}
        )
        self.statistic = statistic
        self.organization = self.statistic.project.name
        self.ticket_statistics = []
        
        self.field_entries = "ticket_field_entries"
        self.estimadas_id = 20278226
        self.gastas_id = 20279012
        
        self.project_id = project_id
        self.month = month
        self.year = year
    
    def get_tickets(self):
        date = self.statistic.get_date()
        
        start = "%d-%02d-%02d"%(date.year, date.month, 1)
        finish = "%d-%02d-%02d"%(date.year, date.month, date.day)
        
        created = "created>%s created<%s"%(start, finish)
        organization = "organization:\"%s\""% self.organization
        query = "type:ticket %s %s"%(created, organization)
        print query
        return self.zen.search(query = query, page = 0)
    
    def submitter_handle(self, user_id):
        return self.zen.show_user(user_id=user_id)["email"]
    
    def organization_handle(self, organization_id):
        return get(self.zen.show_organization(organization_id=organization_id), "name")
    
    def hours_handle(self, hourlist):
        hours = {}
        for props in hourlist:
            if props.get('ticket_field_id',-1) == self.estimadas_id:
                v = props.get('value',0)
                hours["estimated_hours"] = custom_float( v )
            elif props.get('ticket_field_id',-1) == self.gastas_id:
                v = props.get('value',0)
                hours["spent_hours"] = custom_float( v )
            if hours.has_key("estimated_hours") and hours.has_key("spent_hours"):
                break # evita trabalho desnecessário.
        return hours
    
    def update_remainder(self):
        if self.statistic["total_hours"] > 0.0:
            remainder = self.statistic["total_hours"] - self.statistic["spent"]
            self.statistic["remainder"] = remainder
            
    def get_statistc_data(self, detail_view=False):
        for ticket in self.get_tickets():
            self.update_statistic( ticket )
        self.update_remainder()
        if detail_view:
            data = self.ticket_statistics
        else:
            data = self.statistic.get_data()
        return data
    
    def update_statistic(self, ticket):
        ticket_created_at = ticket["created_at"]
        
        # ignora tickets anteriores a data do plano anual
        created_dt = shared.convertToDatetime( ticket_created_at )
        start_dt = self.statistic.yearlyPlanStartDate
        
        if (created_dt.date() - start_dt).days < 0: return
        
        fields = get(ticket, self.field_entries)
        hours = self.hours_handle( fields )
        
        estimated = int(hours.get("estimated_hours",0.0))
        spent = int(hours.get("spent_hours",0.0))
        self.statistic["estimated"] += estimated
        self.statistic["spent"] += spent
        
        # o uso externo da instace de 'statistic', garante a soma de todos os meses
        self.statistic.add_yearly_spent( spent )
        self.update_remainder()
        
        static = shared.TableHeader.getBaseDict()
        created = shared.getFormatedDate( ticket_created_at )
        static["created"] = created
        static["estimated"] = estimated
        static["spent"] = spent
        
        nice_id = ticket.get("nice_id", 0)
        static["id"] = {
            "link": self.site+"/agent/#/tickets/%s"%str(nice_id),
            "label": "#"+str(nice_id)
        }
        subject = ticket.get("subject", "...")
        static["subject"] = subject
        
        self.ticket_statistics.append( static )
        
########################### RUNNING ###########################
if __name__ == "__main__":
    try:
        project = "clipping-pue"; year = 2012; month = 8
        
        statistic = shared.Statistic(project_id=project, year=year, month=month)
        statistic.update(year, month)
        
        zen = Zendesk(project_id=project, year=year, month=month, statistic=statistic)
        for d in  zen.get_statistc_data():
            print d
        
        #for ticket in zen.get_tickets():
            #print ticket
            #print "-"*25
    except Exception as e:
        print "Err: ", e