# coding=utf-8
import json
import smtplib # to send mail

def sendServerEmail(data):
	fromAddress = '<user-name>@gmail.com'
	toAddress  = ['<user-name>@gmail.com']
	subject = 'Stats Server Update Log'
	body = json.dumps(data, indent=4, sort_keys=True, separators=(',', ' : '))
	msg = 'Subject: %s\n\n%s' % (subject, body)

	# Credentials (if needed)
	username = '<user-name>'
	password = '<password>'

	# The actual mail send
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(username,password)
	for mail in toAddress:
		server.sendmail(fromAddress, mail, msg)
	server.quit()
	log = 'All logs sent!'
	return log

if __name__ == '__main__':
    print ('\nThis is not a executable. Use the import to get the functions!!!\n')
    print ('Public functions:')
    print ('sendServerEmail(data)')