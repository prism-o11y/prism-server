// alert-noti-service/internal/notify/smtp/sender.go

package smtp

import (
	"sync"

	"gopkg.in/gomail.v2"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/conf"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/models"
)

type EmailSender struct {
	dialer      *gomail.Dialer
	tmplManager *templateManager
	msgPool     *sync.Pool
	Config      *conf.Smtp
}

func NewEmailSender(cfg *conf.Smtp) (*EmailSender, error) {
	tmplManager, err := newTemplateManager()
	if err != nil {
		return nil, err
	}

	return &EmailSender{
		dialer:      gomail.NewDialer(cfg.Host, cfg.Port, cfg.Email, cfg.Password),
		tmplManager: tmplManager,
		msgPool: &sync.Pool{
			New: func() interface{} {
				return gomail.NewMessage()
			},
		},
		Config: cfg,
	}, nil
}

func (p *EmailSender) SendEmail(data *models.SMTPNotification) error {
	m := p.msgPool.Get().(*gomail.Message)
	defer func() {
		m.Reset()
		p.msgPool.Put(m)
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
