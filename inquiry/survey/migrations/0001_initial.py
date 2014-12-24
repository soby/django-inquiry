# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('question', models.TextField()),
                ('question_type', models.CharField(max_length=1024, choices=[[b'boolean', 'Boolean'], [b'choice', 'Choice'], [b'multiple choice', 'Multiple Choice'], [b'text', 'Text'], [b'textarea', 'Text Area'], [b'file', 'File']])),
                ('created_by', models.ForeignKey(related_name='survey_question_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='survey_question_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_question_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('name', models.CharField(max_length=1024)),
                ('value', models.CharField(max_length=1024)),
                ('help_text', models.CharField(max_length=1024, null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='survey_questionchoice_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='survey_questionchoice_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_questionchoice_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('resource', models.FileField(upload_to=b'')),
                ('resource_type', models.CharField(max_length=1024, choices=[[b'file', 'File'], [b'image', 'Image'], [b'flash', 'Flash Movie'], [b'movie', 'Movie']])),
                ('content_type', models.CharField(max_length=1024, null=True, blank=True)),
                ('size', models.IntegerField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='survey_questionresource_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='survey_questionresource_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_questionresource_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('answer', models.TextField()),
                ('created_by', models.ForeignKey(related_name='survey_questionresponse_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='survey_questionresponse_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_questionresponse_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('question', models.ForeignKey(to='survey.Question')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionResponseResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('resource', models.FileField(upload_to=b'')),
                ('resource_type', models.CharField(max_length=1024, choices=[[b'file', 'File'], [b'image', 'Image'], [b'flash', 'Flash Movie'], [b'movie', 'Movie']])),
                ('content_type', models.CharField(max_length=1024, null=True, blank=True)),
                ('size', models.IntegerField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='survey_questionresponseresource_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='survey_questionresponseresource_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_questionresponseresource_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('question_response', models.ForeignKey(to='survey.QuestionResponse')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('resource', models.FileField(upload_to=b'')),
                ('resource_type', models.CharField(max_length=1024, choices=[[b'file', 'File'], [b'image', 'Image'], [b'flash', 'Flash Movie'], [b'movie', 'Movie']])),
                ('content_type', models.CharField(max_length=1024, null=True, blank=True)),
                ('size', models.IntegerField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='survey_resource_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='survey_resource_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_resource_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('passed', models.NullBooleanField()),
                ('score', models.IntegerField(null=True, blank=True)),
                ('completed_date', models.DateTimeField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='survey_response_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='survey_response_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_response_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResponseSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(related_name='survey_responsesection_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='survey_responsesection_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_responsesection_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('response', models.ForeignKey(to='survey.Response')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('name', models.CharField(max_length=1024)),
                ('description', models.TextField()),
                ('created_by', models.ForeignKey(related_name='survey_section_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='survey_section_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_section_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SRGroupObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(to='survey.Response')),
                ('group', models.ForeignKey(to='auth.Group')),
                ('permission', models.ForeignKey(to='auth.Permission')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SRObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(related_name='responsepermission', to='survey.Response')),
                ('permission', models.ForeignKey(to='auth.Permission')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024)),
                ('label', models.CharField(max_length=1024, null=True, blank=True)),
                ('help_text', models.CharField(max_length=1024, null=True, blank=True)),
                ('closed_state', models.BooleanField(default=False, help_text='This is a final state')),
                ('created_by', models.ForeignKey(related_name='survey_status_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='survey_status_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_status_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StatusGroupObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(to='survey.Status')),
                ('group', models.ForeignKey(to='auth.Group')),
                ('permission', models.ForeignKey(to='auth.Permission')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StatusObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(related_name='statuspermission', to='survey.Status')),
                ('permission', models.ForeignKey(to='auth.Permission')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024)),
                ('description', models.TextField()),
                ('created_by', models.ForeignKey(related_name='survey_survey_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='survey_survey_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_survey_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyGroupObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(to='survey.Survey')),
                ('group', models.ForeignKey(to='auth.Group')),
                ('permission', models.ForeignKey(to='auth.Permission')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(related_name='surveypermission', to='survey.Survey')),
                ('permission', models.ForeignKey(to='auth.Permission')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024)),
                ('created_by', models.ForeignKey(related_name='survey_type_created_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('initial_status', models.ForeignKey(related_name='surveytype_initial_statuses', to='survey.Status')),
                ('modified_by', models.ForeignKey(related_name='survey_type_modified_by_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('org', models.ForeignKey(to='core.Org')),
                ('owner', models.ForeignKey(related_name='survey_type_owner_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('statuses', models.ManyToManyField(to='survey.Status')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TypeGroupObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(to='survey.Type')),
                ('group', models.ForeignKey(to='auth.Group')),
                ('permission', models.ForeignKey(to='auth.Permission')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TypeObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(related_name='typepermission', to='survey.Type')),
                ('permission', models.ForeignKey(to='auth.Permission')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='typeobjectpermission',
            unique_together=set([('user', 'permission', 'content_object')]),
        ),
        migrations.AlterUniqueTogether(
            name='typegroupobjectpermission',
            unique_together=set([('group', 'permission', 'content_object')]),
        ),
        migrations.AlterUniqueTogether(
            name='surveyobjectpermission',
            unique_together=set([('user', 'permission', 'content_object')]),
        ),
        migrations.AlterUniqueTogether(
            name='surveygroupobjectpermission',
            unique_together=set([('group', 'permission', 'content_object')]),
        ),
        migrations.AddField(
            model_name='survey',
            name='survey_type',
            field=models.ForeignKey(to='survey.Type'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='statusobjectpermission',
            unique_together=set([('user', 'permission', 'content_object')]),
        ),
        migrations.AlterUniqueTogether(
            name='statusgroupobjectpermission',
            unique_together=set([('group', 'permission', 'content_object')]),
        ),
        migrations.AlterUniqueTogether(
            name='status',
            unique_together=set([('name', 'org')]),
        ),
        migrations.AlterUniqueTogether(
            name='srobjectpermission',
            unique_together=set([('user', 'permission', 'content_object')]),
        ),
        migrations.AlterUniqueTogether(
            name='srgroupobjectpermission',
            unique_together=set([('group', 'permission', 'content_object')]),
        ),
        migrations.AddField(
            model_name='section',
            name='parent',
            field=models.ForeignKey(to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='responsesection',
            name='survey',
            field=models.ForeignKey(to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='responsesection',
            name='survey_section',
            field=models.ForeignKey(to='survey.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='response',
            name='status',
            field=models.ForeignKey(to='survey.Status'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='response',
            name='survey',
            field=models.ForeignKey(to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='response',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='parent',
            field=models.ForeignKey(to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='section',
            field=models.ForeignKey(to='survey.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionresponseresource',
            name='response',
            field=models.ForeignKey(to='survey.Response'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionresponseresource',
            name='section',
            field=models.ForeignKey(to='survey.ResponseSection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionresponseresource',
            name='survey',
            field=models.ForeignKey(to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionresponse',
            name='response',
            field=models.ForeignKey(to='survey.Response'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionresponse',
            name='section',
            field=models.ForeignKey(to='survey.ResponseSection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionresponse',
            name='survey',
            field=models.ForeignKey(to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionresource',
            name='parent',
            field=models.ForeignKey(to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionresource',
            name='question',
            field=models.ForeignKey(to='survey.Question'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionresource',
            name='section',
            field=models.ForeignKey(to='survey.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionchoice',
            name='parent',
            field=models.ForeignKey(to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionchoice',
            name='question',
            field=models.ForeignKey(to='survey.Question'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionchoice',
            name='section',
            field=models.ForeignKey(to='survey.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='question',
            name='parent',
            field=models.ForeignKey(to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='question',
            name='section',
            field=models.ForeignKey(to='survey.Section'),
            preserve_default=True,
        ),
    ]
