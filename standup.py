#!/usr/bin/python
# coding: utf-8
import sys
from jira import JIRA
jira = JIRA(sys.argv[1])
issues = jira.search_issues('assignee = currentUser() and status = Open')
for i in issues :
    print u'• %s\t%s' % (i.key.ljust(10), i.fields.summary)
