package template

import (
	"bytes"
	"html/template"
	"sync"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/models"
)

type Manager struct {
	templatePool *sync.Pool
}

func NewManager() (*Manager, error) {
	tmpl, err := template.New("alert").Parse(AlertTemplate)
	if err != nil {
		return nil, err
	}

	return &Manager{
		templatePool: &sync.Pool{
			New: func() interface{} {
				return tmpl
			},
		},
	}, nil
}

func (m *Manager) GenerateNotifyBody(data *models.NotifyRequest) (string, error) {
	tmpl := m.templatePool.Get().(*template.Template)
	defer m.templatePool.Put(tmpl)

	var buffer bytes.Buffer
	if err := tmpl.Execute(&buffer, data); err != nil {
		return "", err
	}

	return buffer.String(), nil
}
