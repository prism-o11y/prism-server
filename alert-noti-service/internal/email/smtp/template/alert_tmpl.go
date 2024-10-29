package template

const alertTemplate string = `
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
        .alert-type {
            font-size: 20px;
            color: red;
        }
        .error-details {
            font-size: 16px;
            margin-top: 20px;
            color: #555;
        }
        .footer {
            margin-top: 30px;
            font-size: 12px;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">System Alert Notification</div>
        <p>Hi {{.Recipient}},</p>
        <p class="alert-type">Alert Type: {{.Severity}}</p>
        <p class="error-details">Details: {{.Message}}</p>
        <p class="error-details">Date and Time: {{.DateTime}}</p>
        <p>If you need to take action, please review the logs and resolve the issue promptly.</p>
        <div class="footer">This is an automated message from your monitoring system.</div>
    </div>
</body>
</html>
`
