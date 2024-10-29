package depends

import (
	"time"

	"github.com/prism-o11y/prism-server/shared/data/kafka"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/conf"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/email/smtp"
)

type Dependencies struct {
	Config       *conf.Config
	SMTPProvider *smtp.Provider
	ConsManager  *kafka.ConsumerManager
}

func New() (*Dependencies, error) {
	conf, err := conf.New()
	if err != nil {
		return nil, err
	}

	smtpProvider, err := smtp.NewProvider(conf.Smtp)
	if err != nil {
		return nil, err
	}

	consManager := kafka.NewConsumerManager(
		[]string{conf.Databases.KafkaAddress},
		conf.Databases.Topics,
		conf.Databases.ConsumerGroups,
		time.Duration(5)*time.Second,
	)

	return &Dependencies{
		Config:       conf,
		SMTPProvider: smtpProvider,
		ConsManager:  consManager,
	}, nil
}
