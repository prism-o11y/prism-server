package smtp

import (
	"gopkg.in/gomail.v2"
)

type Provider struct {
	dialer *gomail.Dialer
}

func NewProvider(host, email, password string, port int) *Provider {
	dialer := gomail.NewDialer(host, port, email, password)
	return &Provider{
		dialer: dialer,
	}
}

func (s *Provider) SendMail() error {
	return nil
}
