package conf

import (
	"context"
	"strings"

	"github.com/go-playground/validator"
	"github.com/rs/zerolog/log"
	"github.com/sethvargo/go-envconfig"
)

type Tokens []string

func (t *Tokens) UnmarshalText(text []byte) error {
	*t = Tokens(strings.Split(string(text), ","))
	return nil
}

type Config struct {
	Server    Server    `env:", prefix=SERVER_"`
	Databases Databases `env:", prefix=DATABASE_"`
	Smtp      Smtp      `env:", prefix=SMTP_"`
}

func New() (*Config, error) {
	cfg := &Config{}
	if err := envconfig.Process(context.Background(), cfg); err != nil {
		log.Error().Err(err).Send()
		return nil, err
	}

	if err := validator.New().Struct(cfg); err != nil {
		log.Error().Err(err).Send()
		return nil, err
	}

	return cfg, nil
}
