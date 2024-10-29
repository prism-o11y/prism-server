package template

import (
	"bytes"
	"html/template"
	"sync"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/alert"
)

type Manager struct {
	templatePool *sync.Pool
}

func NewManager() (*Manager, error) {
	tmpl, err := template.New("alert").Parse(alertTemplate)
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

func (m *Manager) GenerateAlertBody(data *alert.Data) (string, error) {
	tmpl := m.templatePool.Get().(*template.Template)
	defer m.templatePool.Put(tmpl)

	var buffer bytes.Buffer
	if err := tmpl.Execute(&buffer, data); err != nil {
		return "", err
	}

	return buffer.String(), nil
}
