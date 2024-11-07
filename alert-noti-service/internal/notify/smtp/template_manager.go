package smtp

import (
	"bytes"
	"html/template"
	"sync"

	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/models"
	"github.com/prism-o11y/prism-server/alert-noti-service/internal/notify/smtp/templates"
)

type templateManager struct {
	tmplPool *sync.Pool
}

func newTemplateManager() (*templateManager, error) {
	tmpl, err := template.New("alert").Parse(templates.AlertTemplate)
	if err != nil {
		return nil, err
	}

	return &templateManager{
		tmplPool: &sync.Pool{
			New: func() interface{} {
				return tmpl
			},
		},
	}, nil
}

func (m *templateManager) GenerateNotifyBody(data *models.NotifyRequest) (string, error) {
	tmpl := m.tmplPool.Get().(*template.Template)
	defer m.tmplPool.Put(tmpl)

	buffer := &bytes.Buffer{}
	if err := tmpl.Execute(buffer, data); err != nil {
		return "", err
	}

	return buffer.String(), nil
}
