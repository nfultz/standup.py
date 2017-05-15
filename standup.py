#!/usr/bin/python
# coding: utf-8
import sys
import re
from jira import JIRA
import requests

jira = JIRA(sys.argv[1])
issues = jira.search_issues('assignee = currentUser() and status = Open')

lines = []
for i in issues:
    print u'• %s\t%s' % (i.key.ljust(10), i.fields.summary)
    txt = u'• <%s|%s>\t%s' % (i.permalink(), i.key, i.fields.summary)
    lines.append(txt)
    lastcomment = jira.comments(i)
    if lastcomment:
        lastcomment = max(lastcomment, key=lambda c: c.updated)
        print '> ', lastcomment.body
    comment = raw_input("Comment> ")
    if comment == 'a':
        comment = lastcomment.body
    elif comment:
        jira.add_comment(i, comment)
    if comment:
        lines.append('> ' + comment)

print '-' * 78
for line in lines:
    print re.sub('http[^|]*[|]', '', line)

post = raw_input('post to slack?(yn) ')
if len(sys.argv) <= 2 or post != 'y':
    sys.exit()

w_url = sys.argv[2]

requests.post(w_url, json=dict(text='\n'.join(lines)))
