package smtp

import (
	"sync"

	"gopkg.in/gomail.v2"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/alert"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/email/smtp/template"
)

type Provider struct {
	dialer      *gomail.Dialer
	tmplManager *template.Manager
	messagePool *sync.Pool
}

func NewProvider(host string, port int, email string, password string) (*Provider, error) {
	tmplManager, err := template.NewManager()
	if err != nil {
		return nil, err
	}

	return &Provider{
		dialer:      gomail.NewDialer(host, port, email, password),
		tmplManager: tmplManager,
		messagePool: &sync.Pool{
			New: func() interface{} {
				return gomail.NewMessage()
			},
		},
	}, nil
}

func (p *Provider) SendMail(data *alert.Data) error {
	m := p.messagePool.Get().(*gomail.Message)
	defer p.messagePool.Put(m)

	m.SetHeader("From", p.dialer.Username)
	m.SetHeader("To", data.Recipient)
	m.SetHeader("Subject", "Alert Notification")

	body, err := p.tmplManager.GenerateAlertBody(data)
	if err != nil {
		return err
	}

	m.SetBody("text/html", body)

	return p.dialer.DialAndSend(m)
}
