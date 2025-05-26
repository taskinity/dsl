import asyncio
import json
import subprocess
import tempfile
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from jinja2 import Template


class Processor(ABC):
    """Base class for all processors"""

    @abstractmethod
    async def process(self, message: Any) -> Optional[Any]:
        """Process a message and return result or None if filtered"""
        pass


class ExternalProcessor(Processor):
    """Processor that delegates to external commands/programs"""

    def __init__(self, config: Dict[str, Any]):
        self.command = config['command']
        self.input_format = config.get('input_format', 'json')
        self.output_format = config.get('output_format', 'json')
        self.is_async = config.get('async', False)
        self.config = config.get('config', {})
        self.timeout = config.get('timeout', 30)

    async def process(self, message: Any) -> Optional[Any]:
        """Execute external command with message as input"""
        try:
            # Prepare input data
            input_data = self._prepare_input(message)

            # Create temporary files for communication
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
                if self.input_format == 'json':
                    json.dump(input_data, input_file)
                elif self.input_format == 'frame_stream':
                    # For camera frames, save as binary
                    input_file.write(str(input_data))
                else:
                    input_file.write(str(input_data))

                input_file_path = input_file.name

            try:
                # Build command with input file
                cmd = f"{self.command} --input {input_file_path}"

                # Add config as environment variables
                env = os.environ.copy()
                for key, value in self.config.items():
                    env[f"CONFIG_{key.upper()}"] = str(value)

                if self.is_async:
                    # Start process without waiting
                    subprocess.Popen(cmd, shell=True, env=env)
                    return message  # Pass through original message
                else:
                    # Execute and wait for result
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=self.timeout,
                        env=env
                    )

                    if result.returncode != 0:
                        print(f"❌ External command failed: {result.stderr}")
                        return None

                    return self._parse_output(result.stdout)

            finally:
                # Cleanup temp file
                try:
                    os.unlink(input_file_path)
                except:
                    pass

        except Exception as e:
            print(f"❌ External processor error: {e}")
            return None

    def _prepare_input(self, message: Any) -> Dict[str, Any]:
        """Prepare message for external processing"""
        if isinstance(message, dict):
            return message
        else:
            return {"data": message, "config": self.config}

    def _parse_output(self, output: str) -> Any:
        """Parse output from external command"""
        if not output.strip():
            return None

        if self.output_format == 'json':
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {"raw_output": output}
        else:
            return {"output": output.strip()}


class FilterProcessor(Processor):
    """Filter messages based on conditions"""

    def __init__(self, config: Dict[str, Any]):
        self.condition = config['condition']

    async def process(self, message: Any) -> Optional[Any]:
        """Filter message based on condition"""
        try:
            # Simple template-based condition evaluation
            template = Template(self.condition)

            # Prepare context for condition evaluation
            if isinstance(message, dict):
                context = message
            else:
                context = {"message": message}

            # Render condition and evaluate
            condition_str = template.render(**context)

            # Simple evaluation (could be enhanced with more sophisticated parsing)
            if self._evaluate_condition(condition_str, context):
                return message
            else:
                return None

        except Exception as e:
            print(f"❌ Filter processor error: {e}")
            return message  # Pass through on error

    def _evaluate_condition(self, condition: str, context: Dict) -> bool:
        """Evaluate condition string - basic implementation"""
        try:
            # Replace template variables in condition
            for key, value in context.items():
                if isinstance(value, (int, float)):
                    condition = condition.replace(f"{{{{{key}}}}}", str(value))
                elif isinstance(value, str):
                    condition = condition.replace(f"{{{{{key}}}}}", f"'{value}'")

            # Simple eval (in production, use safer expression evaluator)
            return eval(condition)
        except:
            return True  # Pass through if evaluation fails


class TransformProcessor(Processor):
    """Transform messages using templates"""

    def __init__(self, config: Dict[str, Any]):
        self.template_str = config.get('template', '{{message}}')
        self.output_field = config.get('output_field', 'message')

    async def process(self, message: Any) -> Optional[Any]:
        """Transform message using template"""
        try:
            template = Template(self.template_str)

            # Prepare context
            if isinstance(message, dict):
                context = message
            else:
                context = {"message": message}

            # Render template
            result = template.render(**context)

            # Return transformed message
            if isinstance(message, dict):
                transformed = message.copy()
                transformed[self.output_field] = result
                return transformed
            else:
                return {self.output_field: result, "original": message}

        except Exception as e:
            print(f"❌ Transform processor error: {e}")
            return message


class AggregateProcessor(Processor):
    """Aggregate messages over time"""

    def __init__(self, config: Dict[str, Any]):
        self.strategy = config.get('strategy', 'collect')
        self.timeout = self._parse_timeout(config.get('timeout', '1m'))
        self.max_size = config.get('max_size', 100)
        self.buffer = []
        self.last_flush = asyncio.get_event_loop().time()

    async def process(self, message: Any) -> Optional[Any]:
        """Aggregate messages"""
        current_time = asyncio.get_event_loop().time()

        # Add message to buffer
        self.buffer.append({
            "timestamp": current_time,
            "message": message
        })

        # Check if we should flush
        should_flush = (
                len(self.buffer) >= self.max_size or
                (current_time - self.last_flush) >= self.timeout
        )

        if should_flush:
            result = self._create_aggregate()
            self.buffer.clear()
            self.last_flush = current_time
            return result

        return None  # Don't pass through individual messages

    def _create_aggregate(self) -> Dict[str, Any]:
        """Create aggregated message"""
        if self.strategy == 'collect':
            return {
                "count": len(self.buffer),
                "events": [item["message"] for item in self.buffer],
                "first_timestamp": self.buffer[0]["timestamp"] if self.buffer else None,
                "last_timestamp": self.buffer[-1]["timestamp"] if self.buffer else None
            }
        elif self.strategy == 'count':
            return {"count": len(self.buffer)}
        else:
            return {"messages": self.buffer}

    def _parse_timeout(self, timeout_str: str) -> float:
        """Parse timeout string to seconds"""
        if timeout_str.endswith('s'):
            return float(timeout_str[:-1])
        elif timeout_str.endswith('m'):
            return float(timeout_str[:-1]) * 60
        elif timeout_str.endswith('h'):
            return float(timeout_str[:-1]) * 3600
        else:
            return float(timeout_str)


class DebugProcessor(Processor):
    """Debug processor that logs messages"""

    def __init__(self, config: Dict[str, Any]):
        self.prefix = config.get('prefix', 'DEBUG')

    async def process(self, message: Any) -> Optional[Any]:
        """Log message and pass through"""
        print(f"🐛 {self.prefix}: {message}")
        return message