#!/usr/bin/python
# coding: utf-8
import sys
from jira import JIRA
import requests



jira = JIRA(sys.argv[1])
issues = jira.search_issues('assignee = currentUser() and status = Open')

text = []
for i in issues :
    txt = u'• <%s|%s>\t%s' % (i.permalink(), i.key,i.fields.summary)
    print txt
    text.append(txt)
    lastcomment = [c for c in jira.comments(i) if c.body.endswith(';')]
    if lastcomment:
        lastcomment = max(lastcomment, key=lambda c: c.updated)
        print '>', lastcomment.body[:-2]
    comment = raw_input("Comment> ")
    if comment == 'a':
        comment = lastcomment.body[:-2]
    elif comment:
        jira.add_comment(i, comment + ' ;')
    if comment:
        text.append('>' +  comment)

post = raw_input('post to slack?') 
if len(sys.argv) <= 2 or not post: sys.exit()

w_url = sys.argv[2]

requests.post(w_url, json=dict(text='\n'.join(text)))
