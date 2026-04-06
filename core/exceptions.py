from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            "success": False,
            "error": {
                "code": response.status_code,
                "message": response.data.get("detail", "An error occurred"),
            },
        }

        if isinstance(response.data, dict) and "detail" not in response.data:
            fields = {}
            for key, value in response.data.items():
                if isinstance(value, list):
                    fields[key] = value[0] if value else value
                else:
                    fields[key] = value
            if fields:
                custom_response_data["error"]["fields"] = fields

        response.data = custom_response_data

    return response
