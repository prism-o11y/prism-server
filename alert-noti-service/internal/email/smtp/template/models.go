package template

type Types string

const (
	Alert Types = "alert"
	Email Types = "email"
)

type Template struct {
	Body string
	Type Types
}

func NewTemplate(t Types) *Template {
	tmpl := &Template{Type: t}
	tmpl.setBody()
	return tmpl
}

func (t *Template) setBody() {
	if t.Type == Alert {
		t.Body = alertTemplate
	} else if t.Type == Email {
	}
}

func (t *Template) getSubject(data string) string {
	if t.Type == Alert {
		getAlertStyles(data)
	} else if t.Type == Email {
	}
	return ""
}
