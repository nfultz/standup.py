#!/usr/bin/python3
# coding: utf-8
import re
import sys

from github import Github
import requests

gh = Github(sys.argv[1])
repo = gh.get_repo(sys.argv[2])
issues = repo.get_issues(assignee=gh.get_user().login, state='open')

w_url = sys.argv[3]

status_to_emoji = {
  'Blocked': ':scream:',
  'In Progress': ':sunglasses:',
  'Open': ':doge:',
  'Soft Launch': ':pray:',
  'Rollout': ':chart_with_upwards_trend:',
  'Done': ':tada:'
}


lines = []
comments = []
to_close = []
to_block = []
to_unblock = []

for i in issues:
    s = 'blocked' if 'blocked' in {x.name for x in i.labels} else 'open'
    print( u'• %s[%s]\t%s' % (str(i.number).ljust(10), s, i.title) )
    lastcomment = [x for x in i.get_comments()]
    if lastcomment:
        lastcomment = lastcomment[-1]
        print( '> ', lastcomment.body)
        print( '-' * 40)

    emoji = ':thinking_face:' if s == 'open' else ':aargh:'

    # Ask if wanting to transition the ticket
    comment = input("Comment on this ticket?(prefix with !bu)")
    if comment.startswith('!'):
        to_close.append(i)
        emoji = ":toot:"
        comment = comment[1:].strip()
    elif comment.startswith('b'):
        to_block.append(i)
        emoji = ":aargh:"
        comment = comment[1:].strip()
    elif comment.startswith('!'):
        to_unblock.append(i)
        emoji = ":sunglasses:"
        comment = comment[1:].strip()

    # Adds current info to be printed
    txt = u'• <%s|%s>[%s]\t%s' % (i.html_url, i.number, emoji, i.title)
    lines.append(txt)

    # Add a comment to ticket
    if comment:
        lines.append('> ' + comment)
        comments.append((i, comment))

# Add final commentary
final_comment = input("Any last thoughts? ")
if final_comment:
    lines.append('Other thoughts: ' + final_comment)

print( '-' * 78)
for line in lines:
    print( re.sub('http[^|]*[|]', '', line))


post = input('post to slack?(yn) ')
if len(sys.argv) <= 2 or post != 'y':
    print( 'Terminated without posting to slack.')
    sys.exit()


requests.post(w_url, json=dict(text='\n'.join(lines)))

for issue, comment in comments:
    issue.create_comment(comment)

for issue in to_close:
    issue.edit(state="closed")

for issue in to_block:
    issue.add_to_labels("blocked")

for issue in to_unblock:
    issue.remove_from_labels("blocked")
