from ....core.utils.test.data import Creator
import random


        
class StatusCreator(Creator):
    def create_for_users(self, users, count, save=True):
        res = {}
        for user in users:
            res[user] = self.make('survey.Status',
                                    owner=user,
                                    created_by=user,
                                    org=user.org,
                                    closed_state=False,
                                    _quantity=1,
                                    _fill_optional=bool(random.getrandbits(1)),
                                    save=save)
            if count > 1:
                res[user].extend(self.make('survey.Status',
                                    owner=user,
                                    created_by=user,
                                    org=user.org,
                                    _quantity=count-1,
                                    _fill_optional=bool(random.getrandbits(1)),
                                    save=save))
        return res
            


class TypeCreator(Creator):
    def create_for_users(self, users, count, statusCount=2, save=True):
        res = {}
        for user in users:
            statuses = StatusCreator()\
                .create_for_users([user], 2, save=save)\
                .values()[0]
            kwargs = {  'owner':user,
                        'created_by':user,
                        'org':user.org,
                        'statuses':statuses,
                        'initial_status':statuses[0],
                        '_quantity':count,
                        '_fill_optional':bool(random.getrandbits(1)),
                        'save':save
                      }
            if not save:
                # can't use M2M without saving
                kwargs.pop('statuses')
                
            res[user] = self.make('survey.Type',**kwargs)
                
        return res

class SurveyCreator(Creator):
    def create_for_users(self, users, count, save=True, sections=1,
                         questions=1):
        res = {}
        userTypes = TypeCreator().create_for_users(users, count)
        for user, types in userTypes.items():
            r = []
            for typ in types:
                forTypes = self.create_for_types([typ,], 1, save=save,
                                                 sections=sections,
                                                 questions=questions)
                r.append(forTypes.values()[0][0])
            res[user] = r
        return res
    
    def create_for_types(self, types, count, save=True, sections=1,
                         questions=1):
        res = {}
        for typ in types:
            res[typ] = self.make('survey.Survey',
                                    owner=typ.owner,
                                    created_by=typ.created_by,
                                    org=typ.org,
                                    survey_type=typ,
                                    _quantity=count,
                                    _fill_optional=bool(random.getrandbits(1)),
                                    save=save)
            if save:
                if sections:
                    secs = SectionCreator().create_for_surveys(
                                                res[typ], sections)
                    if questions:
                        for surv, secs in secs.items():
                            QuestionCreator().create_for_sections(secs,
                                                                  questions)

        return res
    
class SectionCreator(Creator):
    def create_for_users(self, users, count, surveyCount=1, save=True,
                         questions=1):
        res = {}
        userObjs = SurveyCreator().create_for_users(users, surveyCount,
                                                    sections=0)
        for user, objs in userObjs.items():
            r = []
            for o in objs:
                forObjs = self.create_for_surveys([o,], count, save=save,
                                                  questions=questions)
                r.append(forObjs.values()[0][0])
            res[user] = r
        return res 
    
    def create_for_surveys(self, surveys, count, save=True, questions=1):
        res = {}
        for survey in surveys:
            res[survey] = self.make('survey.Section',
                                     owner=survey.owner,
                                     created_by=survey.created_by,
                                     parent=survey,
                                     org=survey.org,
                                     _quantity=count,
                                     _fill_optional=bool(
                                                        random.getrandbits(1)),
                                     save=save
                                    )
            if save and questions:
                QuestionCreator().create_for_sections(res[survey], questions)
        return res


class ResourceCreator(Creator):
    def create_for_users(self, users, count, save=True):
        res = {}
        userObjs = SectionCreator().create_for_users(users, 1)
        for user, objs in userObjs.items():
            r = []
            for o in objs:
                forObjs = self.create_for_sections([o,], count, save=save)
                r.append(forObjs.values()[0][0])
            res[user] = r
        return res 
    
    def create_for_sections(self, objs, count, save=True):
        res = {}
        
        for obj in objs:
            res[obj] = self.make('survey.Resource',
                                 owner=obj.owner,
                                 created_by=obj.created_by,
                                 section=obj,
                                 parent=obj.parent,
                                 org=obj.org,
                                 _quantity=count,
                                 _fill_optional=True,
                                 save=save
                        )
        return res


class QuestionCreator(Creator):
    def create_for_users(self, users, count, save=True):
        res = {}
        userObjs = SectionCreator().create_for_users(users, 1)
        for user, objs in userObjs.items():
            r = []
            for o in objs:
                forObjs = self.create_for_sections([o,], count, save=save)
                r.append(forObjs.values()[0][0])
            res[user] = r
        return res 
    
    def create_for_sections(self, objs, count, save=True):
        res = {}
        
        for obj in objs:
            res[obj] = self.make('survey.Question',
                                 owner=obj.owner,
                                 created_by=obj.created_by,
                                 section=obj,
                                 parent=obj.parent,
                                 org=obj.org,
                                 _quantity=count,
                                 _fill_optional=True,
                                 save=save
                        )
        return res


class QuestionChoiceCreator(Creator):
    def create_for_users(self, users, count, save=True):
        res = {}
        userObjs = QuestionCreator().create_for_users(users, 1)
        for user, objs in userObjs.items():
            r = []
            for o in objs:
                forObjs = self.create_for_questions([o,], count, save=save)
                r.append(forObjs.values()[0][0])
            res[user] = r
        return res 
    
    def create_for_questions(self, objs, count, save=True):
        res = {}
        
        for obj in objs:
            res[obj] = self.make('survey.QuestionChoice',
                                 owner=obj.owner,
                                 created_by=obj.created_by,
                                 question=obj,
                                 section=obj.section,
                                 parent=obj.parent,
                                 org=obj.org,
                                 _quantity=count,
                                 _fill_optional=True,
                                 save=save
                        )
        return res


class QuestionResourceCreator(Creator):
    def create_for_users(self, users, count, save=True):
        res = {}
        userObjs = QuestionCreator().create_for_users(users, 1)
        for user, objs in userObjs.items():
            r = []
            for o in objs:
                forObjs = self.create_for_questions([o,], count, save=save)
                r.append(forObjs.values()[0][0])
            res[user] = r
        return res 
    
    def create_for_questions(self, objs, count, save=True):
        res = {}
        
        for obj in objs:
            res[obj] = self.make('survey.QuestionResource',
                                 owner=obj.owner,
                                 created_by=obj.created_by,
                                 question=obj,
                                 section=obj.section,
                                 parent=obj.parent,
                                 org=obj.org,
                                 _quantity=count,
                                 _fill_optional=True,
                                 save=save
                        )
        return res

class ResponseCreator(Creator):
    def create_for_users(self, users, count, save=True):
        res = {}
        userObjs = SurveyCreator().create_for_users(users, 1)
        for user, objs in userObjs.items():
            if save:    
                secInfo = SectionCreator().create_for_surveys(objs, 1)
                for surv, secs in secInfo.items():
                    QuestionCreator().create_for_sections(secs, 1)
            r = []
            for o in objs:
                forObjs = self.create_for_surveys([o,], count, save=save)
                r.append(forObjs.values()[0][0])
            res[user] = r
        return res 
    
    def create_for_surveys(self, objs, count, save=True):
        res = {}
        for obj in objs:
            status = obj.survey_type.statuses.filter(closed_state=False)[0]
            res[obj] = self.make('survey.Response',
                                 owner=obj.owner,
                                 created_by=obj.created_by,
                                 survey=obj,
                                 status=status,
                                 user=obj.owner,
                                 org=obj.org,
                                 _quantity=count,
                                 _fill_optional=True,
                                 save=save
                        )
        return res

class ResponseSectionCreator(Creator):
    def create_for_users(self, users, count, save=True):
        res = {}
        userObjs = ResponseCreator().create_for_users(users, 1)
        for user, objs in userObjs.items():
            r = []
            for o in objs:
                forObjs = self.create_for_responses([o,], count, save=save)
                r.append(forObjs.values()[0][0])
            res[user] = r
        return res 
    
    def create_for_responses(self, objs, count, save=True):
        res = {}
        
        for obj in objs:
            section = obj.survey.section_set.all()[0]
            res[obj] = self.make('survey.ResponseSection',
                                 owner=obj.owner,
                                 created_by=obj.created_by,
                                 response=obj,
                                 survey_section=section,
                                 org=obj.org,
                                 _quantity=count,
                                 _fill_optional=True,
                                 save=save
                        )
        return res


class QuestionResponseCreator(Creator):
    def create_for_users(self, users, count, save=True):
        res = {}
        userObjs = ResponseCreator().create_for_users(users, 1)
        for user, objs in userObjs.items():
            ResponseSectionCreator().create_for_responses(objs, 1)
            r = []
            for o in objs:
                forObjs = self.create_for_responses([o,], count, save=save)
                r.append(forObjs.values()[0][0])
            res[user] = r
        return res 
    
    def create_for_responses(self, objs, count, save=True):
        res = {}
        for obj in objs:
            section = obj.responsesection_set.all()[0]
            question = section.survey_section.question_set.all()[0]
            res[obj] = self.make('survey.QuestionResponse',
                                 owner=obj.owner,
                                 created_by=obj.created_by,
                                 response=obj,
                                 question=question,
                                 section=section,
                                 org=obj.org,
                                 _quantity=count,
                                 _fill_optional=True,
                                 save=save
                        )
        return res

from datetime import datetime 
class QuestionResponseResourceCreator(Creator):
    def create_for_users(self, users, count, save=True):
        res = {}
        userObjs = QuestionResponseCreator().create_for_users(users, 1)
        for user, objs in userObjs.items():
            r = []
            for o in objs:
                forObjs = self.create_for_questionresponses([o,], count, 
                                                            save=save)
                r.append(forObjs.values()[0][0])
            res[user] = r
        return res 
    
    def create_for_questionresponses(self, objs, count, save=True):
        res = {}
        for obj in objs:
            res[obj] = self.make('survey.QuestionResponseResource',
                                 owner=obj.owner,
                                 created_by=obj.created_by,
                                 question_response=obj,
                                 response=obj.response,
                                 section=obj.section,
                                 org=obj.org,
                                 _quantity=count,
                                 _fill_optional=True,
                                 save=save
                        )
        return res            
            
        