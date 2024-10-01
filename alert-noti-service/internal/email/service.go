package email

import "github.com/prism-o11y/prism-server/alert-noti-service/internal/email/smtp"

type service struct {
	smtpProvider *smtp.Provider
}

func newService(smtpProvider *smtp.Provider) *service {
	return &service{
		smtpProvider: smtpProvider,
	}
}
