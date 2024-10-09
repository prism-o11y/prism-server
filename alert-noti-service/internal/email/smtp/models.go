package smtp

import (
	"gopkg.in/gomail.v2"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/conf"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/email/smtp/template"
)

type TransportData struct {
	Recipient string
	Template  *template.Template
}

func NewTransportData(conf *conf.Config, recipient string, data string, t template.Types) *TransportData {
	m := gomail.NewMessage()
	m.SetHeader("From", conf.Smtp.Email)

	return &TransportData{
		Recipient: recipient,
		Template:  template.NewTemplate(t),	
	}
}
