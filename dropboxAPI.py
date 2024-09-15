# coding=utf-8
import dropbox
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, file_from, file_to):
        """ upload a file to Dropbox using API v2 """
        dbx = dropbox.Dropbox(self.access_token)

        with open(file_from , mode='rb') as f:
            binaryFile = f.read()
            dbx.files_upload(binaryFile, file_to, mode=dropbox.files.WriteMode.overwrite)



def uploadToDropbox(file_from, file_to):
    access_token = 'dropbox-token'
    transferData = TransferData(access_token)

    # API v2
    transferData.upload_file(file_from, file_to)

if __name__ == '__main__':
    print ('\nThis is not a executable. Use the import to get the functions!!!\n')
    print ('Public functions:')
    print ('uploadToDropbox(file_from, file_to)')
