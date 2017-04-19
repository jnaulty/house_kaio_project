import smtplib
                                                                                                                                                                                                               
def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
    server = smtplib.SMTP(smtpserver)
    [to_addr_list.append(addr) for addr in cc_addr_list]
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems
                                                                                                                                                                                                               
if __name__=="__main__":

	sendemail(from_addr    = 'watchmyraspberry@gmail.com',
		  to_addr_list = ['jnaulty@gmail.com'],
		  cc_addr_list = ['watchmyraspberry@gmail.com', 'cde.delcourt@gmail.com' ],
		  subject      = 'Howdy',
		  message      = 'Door OPENED at 12:52PM',
		  login        = 'watchmyraspberry',
		  password     = 'Get@c0nnecting')
