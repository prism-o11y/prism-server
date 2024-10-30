package models

import (
	"encoding/json"
	"time"

	"github.com/rs/zerolog/log"
)

type NotifyRequest struct {
	Recipient string        `json:"recipient"`
	Severity  AlertSeverity `json:"severity"`
	Message   string        `json:"message"`
	DateTime  time.Time     `json:"dateTime"`
}

type AlertSeverity string

const (
	Critical AlertSeverity = "CRITICAL"
	Warning  AlertSeverity = "WARNING"
	Info     AlertSeverity = "INFO"
)

func ParseNotifyRequest(msg []byte) (*NotifyRequest, error) {
	data := &NotifyRequest{}
	if err := json.Unmarshal(msg, data); err != nil {
		log.Error().Err(err).Msg("Failed to parse alert data")
		return nil, err
	}
	return data, nil
}
