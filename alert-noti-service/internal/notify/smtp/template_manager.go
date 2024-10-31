package smtp

import (
	"bytes"
	"html/template"
	"sync"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/models"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/smtp/templates"
)

type TemplateManager struct {
	templatePool *sync.Pool
}

func NewTemplateManager() (*TemplateManager, error) {
	tmpl, err := template.New("alert").Parse(templates.AlertTemplate)
	if err != nil {
		return nil, err
	}

	return &TemplateManager{
		templatePool: &sync.Pool{
			New: func() interface{} {
				return tmpl
			},
		},
	}, nil
}

func (m *TemplateManager) GenerateNotifyBody(data *models.NotifyRequest) (string, error) {
	tmpl := m.templatePool.Get().(*template.Template)
	defer m.templatePool.Put(tmpl)

	var buffer bytes.Buffer
	if err := tmpl.Execute(&buffer, data); err != nil {
		return "", err
	}

	return buffer.String(), nil
}
