import os, datetime, time, urllib, re

import requests, records, arrow, sqlalchemy

import secrets


class messaging:
    prev_message = None
    fail_count = 0
    fail_count_24 = 0
    last_checkin = None


def bot_say(slack_str):
    def encode(s):
        return urllib.quote(s.encode("utf-8"))

    channel = encode('#data_corruption')
    slack_str = encode(slack_str)
    url = (
        "https://slack.com/api/chat.postMessage?token={slack_api_key}"
        "&channel={channel}&text={slack_str}&pretty=1');").format(
        slack_api_key=secrets.slack_api_key, channel=channel, slack_str=slack_str)
    print 'url:', url
    requests.post(url);


def run_tests():
    query = (
        "SELECT COUNT(*) FROM customer_cert_associations "
        "JOIN certifications ON certifications.id = customer_cert_associations.certification_id "
        "WHERE certifications.state = 'DELETED'")
    expected_value = 0

    test_failure_strs = []

    for _db_url_with_creds in secrets.DB_URLS:
        def add_failure_str(expected, actual):
            test_failure_strs.append(
                'expected: {}; actual: {};\nsafe_db_url: ```{}```\nquery: \n```{}```'.format(
                    expected, actual, safe_db_url, query))

        safe_db_url = re.sub(
            '://([a-zA-Z0-9]+:[a-zA-Z0-9]+)@', '://<user>:<pass>@', _db_url_with_creds)
        print 'safe_db_url:', safe_db_url
        db = records.Database(_db_url_with_creds)
        should_expect_error = ('ent-prod' in safe_db_url)
        got_error = False
        try:
            rows = db.query(query)
        except sqlalchemy.exc.ProgrammingError:
            if should_expect_error:
                got_error = True
            else:
                raise
        else:
            count = rows[0]['count']
            if count != expected_value:
                add_failure_str(expected_value, count)
        finally:
            if should_expect_error != got_error:
                add_failure_str(should_expect_error, got_error)

    return test_failure_strs


def main():
    now = arrow.utcnow()
    print 'running tests', now.isoformat()

    if not messaging.last_checkin:
        messaging.last_checkin = now
        bot_say("Bot launched at {}".format(messaging.last_checkin))
    elif now - messaging.last_checkin > datetime.timedelta(days=1):
        messaging.last_checkin = now
        bot_say("Test fail count in last 24 hours: {}".format(messaging.fail_count_24));
        messaging.fail_count_24 = 0

    slack_str = 'no data corruption detected'
    test_failure_strs = run_tests()
    if test_failure_strs:
        messaging.fail_count += 1
        messaging.fail_count_24 += 1
        if messaging.fail_count > 10:
            slack_str = '\n'.join(
                test_failure_strs + ['<!channel> data corruption detected'])
    else:
        print 'everything looks good!'
        messaging.fail_count = 0

    print 'messaging.fail_count:', messaging.fail_count
    print 'slack_str:', slack_str
    print 'test_failure_strs:', test_failure_strs
    print 'prev_message:', messaging.prev_message

    if slack_str != messaging.prev_message:
        bot_say(slack_str)

    messaging.prev_message = slack_str


if __name__ == '__main__':
    while True:
        main()
        time.sleep(10)

