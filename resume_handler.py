# resume_downloader.py

# modules
import secret

# third party modules
import json
import os
import requests
import urllib

class ResumeHandler:

    """
    Class to download resume files from FilePicker and upload them to Dropbox.
    """

    def __init__(self, application_url, application_username, application_password):
        """Constructor."""
        self.application_url = application_url
        self.site_username = application_username
        self.site_password = application_password

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
        """Download application json from application_url."""
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
                # add hash as a key to the value to track later
                value['hash'] = key
                self.apps.append(value)

            elif key == 'statuses':
                self._handle_statuses(value)

        return self.apps

    def transfer_files(self):
        """
        Programatically download a file, rename it, upload to
        Dropbox and then delete.
        """
        apps = self.download_applications()
        for app in apps:
            if app['hash'] in self.accepted:
                try:
                    resume_string = app['resume']
                    resume_dict = json.loads(resume_string)
                except (KeyError, ValueError):
                    pass
                resume_url = resume_dict['url']

                filename = '{first}-{last}-Resume.pdf'.format(
                    first=app['first-name'].strip(),
                    last=app['last-name'].strip()
                )
                self._download_file(filename, resume_url)

    def _download_file(self, filename, url):
        """Download file given a filename and url link."""
        urllib.urlretrieve(url, filename)

    def _delete_file(self, filename):
        """Delete a file with the given file path."""
        os.remove(filename)


def main():
    handler = ResumeHandler(
        secret.application_url,
        secret.application_username,
        secret.application_password
    )
    handler.transfer_files()

if __name__ == '__main__':
    main()
