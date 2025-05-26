"""
Tests for dialog chain connectors
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from dialogchain.connectors import Connector, HttpConnector, MqttConnector

class TestConnectors:
    
    def test_base_connector_abstract(self):
        """Test that the base Connector class is abstract"""
        with pytest.raises(TypeError):
            Connector()
    
    @pytest.mark.asyncio
    async def test_http_connector(self):
        """Test the HTTP connector"""
        connector = HttpConnector({
            'base_url': 'http://example.com',
            'endpoint': '/test',
            'method': 'GET'
        })
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value={'result': 'success'})
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await connector.send({'test': 'data'})
            assert result == {'result': 'success'}
    
    @pytest.mark.asyncio
    async def test_mqtt_connector(self):
        """Test the MQTT connector"""
        connector = MqttConnector({
            'broker': 'mqtt://test.mosquitto.org',
            'topic': 'test/topic'
        })
        
        with patch('asyncio_mqtt.Client') as mock_mqtt:
            mock_client = AsyncMock()
            mock_mqtt.return_value.__aenter__.return_value = mock_client
            
            await connector.send({'test': 'data'})
            mock_client.publish.assert_called_once()
