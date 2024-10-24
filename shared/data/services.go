package data

import (
	"github.com/google/uuid"
	jsoniter "github.com/json-iterator/go"
	"github.com/rs/zerolog/log"
)

type SourceType string

const (
	AlertNotiService SourceType = "alert-noti-service"
	LogService       SourceType = "log-service"
	UserService      SourceType = "user-service"
)

type EventData struct {
	Source SourceType
	Data   []byte
	Email  string
	UserID uuid.UUID
}

func NewEventData(message []byte) (*EventData, error) {
	eventData := &EventData{}
	if err := jsoniter.Unmarshal(message, eventData); err != nil {
		log.Error().Err(err).Msg("Failed to unmarshal event message")
		return nil, err
	}
	return nil, nil
}
