package smtp

import (
	"sync"

	"gopkg.in/gomail.v2"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/conf"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/models"
)

type EmailSender struct {
	dialer      *gomail.Dialer
	tmplManager *TemplateManager
	messagePool *sync.Pool
}

func NewEmailSender(cfg *conf.Smtp, tmplManager *TemplateManager) (*EmailSender, error) {
	return &EmailSender{
		dialer:      gomail.NewDialer(cfg.Host, cfg.Port, cfg.Email, cfg.Password),
		tmplManager: tmplManager,
		messagePool: &sync.Pool{
			New: func() interface{} {
				return gomail.NewMessage()
			},
		},
	}, nil
}

func (p *EmailSender) SendMail(data *models.NotifyRequest) error {
	m := p.messagePool.Get().(*gomail.Message)
	defer func() {
		m.Reset()
		p.messagePool.Put(m)
	}()

	m.SetHeader("From", p.dialer.Username)
	m.SetHeader("To", data.Recipient)
	m.SetHeader("Subject", "Alert Notification")

	body, err := p.tmplManager.GenerateNotifyBody(data)
	if err != nil {
		return err
	}

	m.SetBody("text/html", body)

	return p.dialer.DialAndSend(m)
}
