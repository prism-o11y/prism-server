package template

import (
	"html/template"
)

type templates struct {
	Alert *template.Template
	User  *template.Template
}

type Manager struct {
	Templates *templates
}

func NewManager() (*Manager, error) {
	tmpls := &templates{}
	if err := tmpls.loadTemplates(); err != nil {
		return nil, err
	}

	return &Manager{
		Templates: tmpls,
	}, nil
}

func (t *templates) loadTemplates() error {
	alertTmpl, err := template.New("alert").Parse(alertTemplate)
	if err != nil {
		return err
	}

	userTmpl, err := template.New("user").Parse(userTemplate)
	if err != nil {
		return err
	}

	t.Alert = alertTmpl
	t.User = userTmpl

	return nil
}
