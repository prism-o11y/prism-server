package depends

import (
	"github.com/prism-o11y/prism-server/shared/data"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/conf"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/email/smtp"
)

type Dependencies struct {
	Config       *conf.Config
	SMTPProvider *smtp.Provider
	KafkaManager *data.KafkaManager
}

func New() (*Dependencies, error) {
	conf, err := conf.New()
	if err != nil {
		return nil, err
	}

	smtpProvider := smtp.NewProvider(conf.Smtp.Host, conf.Smtp.Email, conf.Smtp.Password, conf.Smtp.Port)
	kafkaManager := data.NewKafkaManager([]string{conf.Databases.KafkaAddress}, conf.Databases.Topics, conf.Databases.ConsumerGroups)

	return &Dependencies{
		Config:       conf,
		SMTPProvider: smtpProvider,
		KafkaManager: kafkaManager,
	}, nil
}
