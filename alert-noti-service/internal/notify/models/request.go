package models

import (
	"encoding/json"
	"time"

	"github.com/rs/zerolog/log"
)

type NotifyRequest struct {
	Recipient string        `json:"recipient"`
	Severity  AlertSeverity `json:"severity"`
	Action    Action        `json:"action"`
	Message   string        `json:"message"`
	DateTime  time.Time     `json:"dateTime"`
}

type AlertSeverity string

const (
	Critical AlertSeverity = "CRITICAL"
	Warning  AlertSeverity = "WARNING"
	Info     AlertSeverity = "INFO"
)

type Action string

const (
	SSE  Action = "SSE"
	SMTP Action = "SMTP"
)

func ParseNotifyRequest(msg []byte) (*NotifyRequest, error) {
	data := &NotifyRequest{}
	if err := json.Unmarshal(msg, data); err != nil {
		log.Error().Err(err).Msg("Failed to parse alert data")
		return nil, err
	}
	return data, nil
}
