// internal/alert/models.go
package alert

import (
	"encoding/json"
	"time"

	"github.com/rs/zerolog/log"
)

type Data struct {
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

func ParseAlertData(msg []byte) (*Data, error) {
	var data Data
	if err := json.Unmarshal(msg, &data); err != nil {
		log.Error().Err(err).Msg("Failed to parse alert data")
		return nil, err
	}
	return &data, nil
}
