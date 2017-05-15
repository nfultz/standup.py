# standup.py

This is a small script to generate a standup message based on JIRA tickets, and
optionally send it to slack.

## Installation

This script should be somewhere on your shell search path. Additionally, you
should add your JIRA account 'quick login' to `.netrc` in your home folder.

To use the slack functionality, you should enable an 'incoming webhook' and
note the URL.

## Usage

    standup.py $JIRA_URL $SLACK_URL

This will print each open ticket assigned to you, and prompt you to leave an
optional comment.

At the end, it will ask to post to slack. Type anything to send, and `^C` to
quit without posting.



