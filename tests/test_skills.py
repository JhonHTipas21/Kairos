"""
Unit tests for Kairos OS modular skills using pytest.
"""

from unittest.mock import MagicMock, patch

import main
from skills.gcalendar import list_upcoming_events
from skills.gmail import send_gmail_message
from skills.greeting import get_systems_briefing
from skills.persona import change_voice_persona
from skills.weather import get_current_weather


def test_change_voice_persona():
    """
    Test that the dynamic voice persona switches between J.A.R.V.I.S. and F.R.I.D.A.Y.
    and updates the global current_voice variable.
    """
    # Reset to default
    main.current_voice = "es-MX-JorgeNeural"

    # Test switching to Friday (female persona)
    res_female = change_voice_persona("friday")
    assert "F.R.I.D.A.Y." in res_female
    assert main.current_voice == "es-MX-DaliaNeural"

    # Test switching back to Jarvis (male persona)
    res_male = change_voice_persona("jarvis")
    assert "J.A.R.V.I.S." in res_male
    assert main.current_voice == "es-MX-JorgeNeural"


@patch("urllib.request.urlopen")
def test_get_current_weather_success(mock_urlopen):
    """
    Test that get_current_weather correctly handles wttr.in responses
    and parses weather data successfully.
    """
    # Mock response from wttr.in
    mock_response = MagicMock()
    mock_response.read.return_value = b"Sunny +25C Humedad:50% Viento:10km/h"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    res = get_current_weather("Cali")
    assert "Cali" in res
    assert "Sunny" in res
    assert "25C" in res


@patch("urllib.request.urlopen")
def test_get_current_weather_failure(mock_urlopen):
    """
    Test that get_current_weather handles request failures gracefully
    and returns a descriptive error message.
    """
    # Mock failure
    mock_urlopen.side_effect = Exception("Connection Timeout")

    res = get_current_weather("Bogota")
    assert "No he podido recuperar el reporte del clima" in res
    assert "Connection Timeout" in res


@patch("skills.greeting.get_battery_status")
@patch("skills.greeting.get_real_cpu_usage")
def test_get_systems_briefing(mock_cpu, mock_battery):
    """
    Test that the systems briefing coordinates greeting, time, battery status,
    and CPU utilization into a unified narrative.
    """
    mock_battery.return_value = "Estado de batería actual: 80% (conectado)"
    mock_cpu.return_value = 15.4

    briefing = get_systems_briefing()
    assert "señor" in briefing.lower()
    assert "batería" in briefing.lower()
    assert "15.4%" in briefing


@patch("skills.gcalendar.get_google_credentials")
@patch("skills.gcalendar.build")
def test_list_upcoming_events(mock_build, mock_creds):
    """
    Test that list_upcoming_events parses events from Google Calendar API
    successfully using MagicMocks.
    """
    mock_creds.return_value = MagicMock()
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    mock_events_list = MagicMock()
    mock_service.events.return_value.list.return_value = mock_events_list
    mock_events_list.execute.return_value = {
        "items": [{"summary": "Reunión de prueba", "start": {"dateTime": "2026-08-20T12:00:00Z"}}]
    }

    res = list_upcoming_events()
    assert "Reunión de prueba" in res


@patch("skills.gmail.get_google_credentials")
@patch("skills.gmail.build")
def test_send_gmail_message(mock_build, mock_creds):
    """
    Test that send_gmail_message properly builds, encodes and sends
    a raw email message via the Gmail API using MagicMocks.
    """
    mock_creds.return_value = MagicMock()
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    mock_messages = MagicMock()
    mock_service.users.return_value.messages.return_value = mock_messages

    res = send_gmail_message("test@example.com", "Asunto", "Contenido del mensaje")
    assert "Éxito" in res
    mock_messages.send.assert_called_once()
