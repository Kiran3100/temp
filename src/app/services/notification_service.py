class NotificationService:
    def __init__(self, sendgrid_key=None, fcm_key=None):
        self.sendgrid_key = sendgrid_key
        self.fcm_key = fcm_key

    def send_email(self, to_email, subject, html):
        # use sendgrid API client
        pass

    def send_push(self, device_token, data):
        # use HTTP request to fcm endpoint with server key
        pass

    def send_slack_alert(self, text):
        # post to slack webhook url
        pass
