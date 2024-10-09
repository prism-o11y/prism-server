package template

var userNotificationTemplate = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }
        .email-container {
            max-width: 600px;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin: auto;
        }
        .header {
            font-size: 24px;
            color: #333;
            font-weight: bold;
        }
        .message-content {
            font-size: 16px;
            margin-top: 20px;
            color: #555;
        }
        .footer {
            margin-top: 30px;
            font-size: 12px;
            color: #888;
        }
        .cta {
            margin-top: 20px;
            text-align: center;
        }
        .cta-button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">🔔 Notification</div>
        <p>Hi {{.RecipientName}},</p>
        <p class="message-content">{{.Message}}</p>
        <div class="cta">
            <a href="{{.ActionLink}}" class="cta-button">Take Action</a>
        </div>
        <div class="footer">Thank you for being a part of our community.</div>
    </div>
</body>
</html>
`
