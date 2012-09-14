# -*- coding: UTF-8 -*-
import os, sys
import json, urllib2

curdir = os.path.dirname(os.path.abspath(__file__))
pardir = os.path.dirname(curdir)

# para executar o script, ele deve estar devidamente configurado.
if __name__ == '__main__':
    curdir = os.path.dirname(os.path.abspath(__file__))
    basedir = os.path.dirname(os.path.dirname(curdir))
    if not basedir in sys.path: sys.path.append( basedir )
    basename = os.path.basename( os.path.dirname(curdir) )
    os.environ["DJANGO_SETTINGS_MODULE"] = basename+".settings"

from viewer.main import shared
import configobj

########################################################################
crendpath = os.path.join(pardir, "credentials", "cred.cfg")
cred_params = configobj.ConfigObj(crendpath)

class Redmine(object):
    site = cred_params["site"]
    key = cred_params["key"]
    headers = {"X-Redmine-API-Key": key}
    
    # --------------------------------------------------------
    name = "REDMINE"

    def __init__(self, project_id="", month=0, year=0, offset=0, limit=100, statistic=None, **params):
        self.decoder = json.JSONDecoder()
        self.issues_statistics = []
        # gera a estatistica de horas
        self.statistic = statistic
        self.project_id = project_id
        self.month = month
        self.year = year
        self.params = params
        self.offset = offset
        self.limit = limit
        self.total = 0
    # --------------------------------------------------------
    def get_projects(self):
        has_next_page = True
        while has_next_page:
            params = dict(offset= self.offset, limit= self.limit)
            query = "&".join(["%s=%s"%(k,params[k]) for k in params.keys()])

            site = self.site + "/projects.json?"+ query
            req = urllib2.Request(site, headers=self.headers)
            resp = urllib2.urlopen( req )
            jd = resp.read(); resp.close()

            data = self.decoder.decode( jd )

            has_next_page = self.check_next_page( data )

            for project in data["projects"]:
                name = project.get("parent",{}).get("name","empty")
                id = project["identifier"]
                yield (name, id)

    # --------------------------------------------------------
    def get_date_interval(self):
        date = self.statistic.date
        start = "%d-%02d-%02d"%(date.year, date.month, 1)
        finish = "%d-%02d-%02d"%(date.year, date.month, date.day)
        return "><%s|%s"%(start, finish)

    # --------------------------------------------------------
    def check_next_page(self, data):
        self.limit = data.get("limit",100)
        self.offset = data["offset"]
        self.total = data["total_count"]
        offset = self.offset + self.limit
        if offset > self.total:
            offset = offset - (offset - self.total)
        self.offset = offset
        return self.total - self.offset > 0

    # --------------------------------------------------------
    def get_issues(self):
        has_next_page = True
        params = dict(
            project_id = self.project_id,
            created_on = self.get_date_interval(),
            status_id  = self.params.get("status_id", "*")
        )
        while has_next_page:
            params["offset"] = self.offset
            params["limit"] = self.limit

            query = "&".join(["%s=%s"%(k, params[k]) for k in params.keys()])
            print query
            site = self.site + "/issues.json?"+ query
            req = urllib2.Request(site, headers=self.headers)
            resp = urllib2.urlopen( req )
            jd = resp.read(); resp.close()

            data = self.decoder.decode( jd )
            has_next_page = self.check_next_page( data )
            issues = data.get("issues",[])

            for issue in issues:
                site = self.site + "/issues/%s.json"%issue["id"]
                req = urllib2.Request(site, headers=self.headers)
                resp = urllib2.urlopen( req )
                jd = resp.read(); resp.close()
                yield self.decoder.decode(jd)

    def update_remainder(self):
        if self.statistic["total_hours"] > 0.0:
            remainder = self.statistic["total_hours"] - self.statistic["spent"]
            self.statistic["remainder"] = remainder	
    
    def get_statistc_data(self, detail_view=False):
        for issue in self.get_issues():
            self.update_statistic( issue )
            
        self.update_remainder()
        
        if detail_view: data = self.issues_statistics
        else: data = self.statistic.get_data()
        return data
    
    def update_statistic(self, issue):
        _issue = issue["issue"]
        issue_created_on = _issue["created_on"]
        
        # ignora issues anteriores a data do plano anual
        created_dt = shared.parser.parse( issue_created_on )
        start_dt = self.statistic.yearlyPlanStartDate
        
        if (created_dt.date() - start_dt).days < 0: return
        
        estimated = int(_issue.get("estimated_hours", 0.0))
        spent = int(_issue.get("spent_hours", 0.0))
        self.statistic["estimated"] += estimated
        self.statistic["spent"] += spent
        
        # o uso externo da instace de 'statistic', garante a soma de todos os meses
        self.statistic.add_yearly_spent( spent )
        
        static = shared.TableHeader.getBaseDict()
        static["project"] = self.statistic["project"]
        static["created"] = created_dt.strftime( shared.DATE_FORMAT )
        static["created_hour"] = created_dt.strftime( shared.HOUR_FORMAT )
        static["estimated"] = estimated
        static["spent"] = spent
        
        issue_id = _issue.get("id", -1)
        static["id"] = {
            "link": self.site+"/issues/%s" % str(issue_id),
            "label": "#"+str(issue_id)
        }
        subject = _issue.get("subject", "...")
        static["subject"] = subject
        
        self.issues_statistics.append( static )

# --------------------------------------------------------
if __name__ == "__main__":
    try:
        project = "clipping-pue"; year = 2012; month = 8
        statistic = shared.Statistic(project_id=project, year=year, month=month)
        statistic.update(year, month)
        
        redmine = Redmine(
            project_id = project, month = 8,
            statistic = statistic
        )
        # estatíscas geral.
        print redmine.get_statistc_data()
        #for n, i in redmine.get_projects():
            #print n, "-- ",i
    except Exception, err:
        print "Err: ",err