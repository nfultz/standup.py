#!/usr/bin/python
# coding: utf-8
import copy
import re
import sys

from jira import JIRA
import requests

jira = JIRA(sys.argv[1])
issues = jira.search_issues('''assignee = currentUser()
                            AND sprint in openSprints()
                            AND status != Done
                            AND type != Epic''')

status_to_emoji = {
  'Blocked': ':scream:',
  'In Progress': ':sunglasses:',
  'Open': ':doge:',
  'Soft Launch': ':pray:',
  'Rollout': ':chart_with_upwards_trend:'
}


lines = []
issue_changes = []
for i in issues:
    # Make copy to separate changes
    i_copy = copy.deepcopy(i)
    print u'• %s[%s]\t%s' % (i.key.ljust(10), i.fields.status, i.fields.summary)
    lastcomment = jira.comments(i)
    if lastcomment:
        lastcomment = max(lastcomment, key=lambda c: c.updated)
        print '> ', lastcomment.body
        print '-' * 40

    # Ask if wanting to transition the ticket
    transition_selection = ''
    transition_response = raw_input("Would you like to transition this ticket?(y/n) ")
    if transition_response == 'y':
        transitions = jira.transitions(i)
        transition_dict = {}
        for t in transitions:
            transition_dict[t['id']] = t['name']
            print t['id'], '->', t['name']
        transition_options = set(transition_dict.keys())
        while transition_selection not in transition_options:
            transition_selection = raw_input("Where do you want to move the ticket? ")
        # Changes status name to whatever user chooses
        i_copy.fields.status.name = transition_dict[transition_selection]

    # Adds current info to be printed
    txt = u'• <%s|%s>[%s]\t%s' % (i_copy.permalink(), i_copy.key, status_to_emoji[i_copy.fields.status.name],
                                  i_copy.fields.summary)
    lines.append(txt)

    # Add a comment to ticket
    comment = raw_input("Comment> ")
    if comment == 'a':
        comment = lastcomment.body
    elif comment:
        lines.append('> ' + comment)
        issue_changes.append((i, comment, transition_selection))
    else:
        comment = ''
        issue_changes.append((i, comment, transition_selection))

# Add final commentary
final_comment = raw_input("Any last thoughts? ")
lines.append('Other thoughts: ' + final_comment)

print '-' * 78
for line in lines:
    print re.sub('http[^|]*[|]', '', line)

# Commit changes to Jira
commit = raw_input('Commit these changes to Jira?(yn) ')
if commit == 'y':
    for issue, comment, transition in issue_changes:
        if comment != '':
            jira.add_comment(issue, comment)
        if transition != '':
            jira.transition_issue(issue, transition)
else:
    print 'Terminated without implementing changes.'
    sys.exit()

post = raw_input('post to slack?(yn) ')
if len(sys.argv) <= 2 or post != 'y':
    print 'Terminated without posting to slack.'
    sys.exit()

w_url = sys.argv[2]

requests.post(w_url, json=dict(text='\n'.join(lines)))

