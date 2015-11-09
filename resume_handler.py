# resume_downloader.py

# modules
import secret

# third party modules
import requests

class ResumeHandler:

    def __init__(self, application_url, application_username, application_password):
        self.application_url = application_url
        self.site_username = site_username
        self.site_password = site_password

    def _handle_statuses(self, obj):
        """Create set of accepted, rejected, waitlist students."""
        self.accepted = set()
        self.rejected = set()
        self.waitlist = set()

        for key, value in obj.iteritems():
            if value == 'accepted':
                self.accepted.add(key)
            elif value == 'rejected':
                self.rejected.add(key)
            elif value == 'waitlist':
                self.waitlist.add(key)

    def download_applications(self):
        """Download application json."""
        response = requests.get(
            self.application_url,
            auth=(self.site_username, self.site_password)
        )

        self.hash_to_email = {}
        self.response_json = response.json()
        self.apps = []

        # create a mapping of hash to email
        for key, value in self.response_json.iteritems():
            if '@' in key:
                # email
                if value not in self.hash_to_email:
                    self.hash_to_email[value] = key

            elif len(key) == 64:
                self.apps.append(value)

            elif key == 'statuses':
                self._handle_statuses(value)

        return self.apps

def main():
    handler = ResumeHandler(
        secret.application_url,
        secret.application_username,
        secret.application_password
    )
    apps = handler.download_applications()
    print apps

if __name__ == '__main__':
    main()
