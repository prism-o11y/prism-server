	package smtp

	import (
		"time"

		"github.com/google/uuid"
		jsoniter "github.com/json-iterator/go"
		"github.com/prism-o11y/prism-server/shared/data"
		"github.com/rs/zerolog/log"
	)

	type AlertType string

	const (
		Critical AlertType = "critical"
		Warning  AlertType = "warning"
		Info     AlertType = "info"
	)

	func (a AlertType) GetStyle() string {
		switch a {
		case Critical:
			return "🚨"
		case Warning:
			return "⚠️"
		case Info:
			return "ℹ️"
		default:
			log.Warn().Str("alert", string(a)).Msg("Unknown alert type")
			return ""
		}
	}

	type AlertPayload struct {
		UserID    uuid.UUID
		AlertType AlertType
		Source    data.SourceType
		Timestamp time.Time
		Data      string
		MetaData  map[string]interface{}
	}

	func NewAlertPayload(data []byte) (*AlertPayload, error) {
		a := &AlertPayload{}
		if err := jsoniter.Unmarshal(data, a); err != nil {
			log.Error().Err(err).Msg("Failed to decode alert notification.")
			return nil, err
		}
		return a, nil
	}

	func (a *AlertPayload) Bytes() []byte {
		data, err := jsoniter.Marshal(a)
		if err != nil {
			log.Error().Err(err).Msg("Failed to encode alert notification.")
			return nil
		}
		return data
	}
