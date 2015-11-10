# resume_downloader.py

# modules
from exception import TransferError
import secret

# third party modules
import json
import os
import requests
import urllib

class ResumeHandler:

    """
    Script to download resume files from FilePicker and upload them to Dropbox.
    """

    def __init__(
        self, application_url, application_username, application_password,
        dropbox_access_token
    ):
        """Constructor."""
        self.application_url = application_url
        self.site_username = application_username
        self.site_password = application_password
        self.dropbox_access_token = dropbox_access_token

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
        Dropbox and then delete it.
        """
        count = 0
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

                # keep track of files that failed download/upload
                retry_list = []

                try:
                    print 'Downloading file: {filename}...'.format(filename=filename)
                    self._download_file(filename, resume_url)
                    self._upload_file(filename)
                    self._delete_file(filename)
                    count += 1

                except TransferError as e:
                    print '!!!!!!!'
                    print e
                    print '!!!!!!!'
                    retry_list.append(filename)

        print '----____----____----____----'
        print '{count} files transferred to Dropbox!'.format(count=count)
        print '----____----____----____----'

        if len(retry_list) == 0:
            print 'All resumes transferred successfully!'
        else:
            print 'The following resumes failed to be transferred: '
            print retry_list

    def _download_file(self, filename, url):
        """Download file given a filename and url link."""
        try:
            urllib.urlretrieve(url, filename)
        except IOError as e:
            raise TransferError('Downloading Error occurred with {filename}'.format(
                filename=filename
            ))

    def _delete_file(self, filename):
        """Delete a file with the given file path."""
        os.remove(filename)

    def _upload_file(self, filename):
        """Upload a file to Dropbox."""
        f = open(filename, 'r')
        size = os.path.getsize(filename)
        url = 'https://content.dropboxapi.com/1/files_put/auto/{path}?overwrite=true'.format(
            path=filename
        )
        try:
            response = requests.put(url, f, headers={
                'Content-Length': size,
                'Authorization': 'Bearer {access_token}'.format(access_token=self.dropbox_access_token)
            })
        except requests.exceptions.HTTPError as e:
            raise TransferError('Uploading Error occurred with {filename}'.
                format(filename=filename)
            )

        if response.status_code == 200:
            print 'Uploaded file: {filename}!'.format(filename=filename)
        else:
            print 'Error in Dropbox uploading. Filename: {filename}'.format(
                filename=filename
            )

def main():
    handler = ResumeHandler(
        secret.application_url,
        secret.application_username,
        secret.application_password,
        secret.dropbox_access_token
    )
    handler.transfer_files()

if __name__ == '__main__':
    main()
