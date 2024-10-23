package smtp

import (
	"sync"

	"github.com/prism-o11y/prism-server/shared/data"
	"gopkg.in/gomail.v2"
)

type Provider struct {
	dialer      *gomail.Dialer
	messagePool *sync.Pool
}

func NewProvider(host string, email string, password string, port int) *Provider {
	return &Provider{
		dialer: gomail.NewDialer(host, port, email, password),
		messagePool: &sync.Pool{
			New: func() interface{} {
				return gomail.NewMessage()
			},
		},
	}
}

func (s *Provider) SendMail(eventData *data.EventData) error {
	m := s.messagePool.Get().(*gomail.Message)
	defer s.messagePool.Put(m)

	return nil
}
