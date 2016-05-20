#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.conf import settings
from calaccess_raw import get_model_list
from django.template.loader import render_to_string
from calaccess_raw.management.commands import CalAccessCommand


class Command(CalAccessCommand):
    help = 'Generate documentation for raw CAL-ACCESS database tables'

    def handle(self, *args, **kwargs):
        self.docs_dir = os.path.join(
            settings.REPO_DIR,
            'docs',
            'calaccess',
            'dbtables',
        )
        os.path.exists(self.docs_dir) or os.makedirs(self.docs_dir)

        model_list = sorted(get_model_list(), key=lambda x:x().klass_name)
        group_list = {}
        for m in model_list:
            # add doc_title (key) and list of pages (value) to each model
            m.docs = {}
            for doc in m().DOCUMENTCLOUD_PAGES:
                try:
                    m.docs[doc.title].extend(doc.pages)
                except KeyError:
                    m.docs[doc.title] = doc.pages
            # add choice field list to model
            m.choice_fields = []
            for field in m._meta.fields:
                if len(field.choices) > 0:
                    # add doc title, page_url list to each choice field
                    field.docs = {}
                    for doc in field.documentcloud_pages:
                        try:
                            field.docs[doc.title].extend(doc.pages)
                        except KeyError:
                            field.docs[doc.title] = doc.pages
                    m.choice_fields.append(field)
            try:
                group_list[m().klass_group].append(m)
            except KeyError:
                group_list[m().klass_group] = [m]
        
        for group, models in group_list.iteritems():
            context = {
                'group_name': group,
                'model_list': models,
                'model_count': len(models),
            }

            template_name = '{}_tables.rst'.format(group)
            rendered = render_to_string(template_name, context)
            target_file = os.path.join(
                self.docs_dir,
                template_name,
            )

            with open(target_file, 'w') as f:
                f.write(rendered)