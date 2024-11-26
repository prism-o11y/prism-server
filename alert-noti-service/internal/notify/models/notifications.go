package models

import (
	"encoding/json"
	"fmt"

	jsoniter "github.com/json-iterator/go"
	"github.com/rs/zerolog/log"
)

type Notification interface {}

type NotificationWrapper struct {
	Action Action          `json:"action"`
	Data   json.RawMessage `json:"data"`
}

func NewNotificationWrapper(action Action, data []byte) NotificationWrapper {
	return NotificationWrapper{
		Action: action,
		Data:   data,
	}
}

func ParseNotification(msg []byte) (Notification, error) {
	var wrapper NotificationWrapper
	if err := jsoniter.Unmarshal(msg, &wrapper); err != nil {
		log.Error().Err(err).Msg("Failed to unmarshal notification")
		return nil, err
	}

	switch wrapper.Action {
	case SMTP:
		var smtpNotification SMTPNotification
		if err := jsoniter.Unmarshal(wrapper.Data, &smtpNotification); err != nil {
			log.Error().Err(err).Msg("Failed to unmarshal SMTP notification")
			return nil, err
		}
		return &smtpNotification, nil
	case SSE:
		var sseNotification SSENotification
		if err := jsoniter.Unmarshal(wrapper.Data, &sseNotification); err != nil {
			log.Error().Err(err).Msg("Failed to unmarshal SSE notification")
			return nil, err
		}
		return &sseNotification, nil
	default:
		return nil, fmt.Errorf("unknown action: %s", wrapper.Action)
	}
}
