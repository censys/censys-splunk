import unittest
from unittest.mock import MagicMock, patch

from censys_asm_hosts_command import CensysAsmHostsCommand


class TestCensysAsmHostsCommand(unittest.TestCase):
    def test_empty_pipeline_input_returns_no_records(self):
        """Validate empty piped input is treated as no results, not standalone mode."""
        command = CensysAsmHostsCommand()

        # An empty upstream pipeline should behave like "no matching rows",
        # not like a standalone invocation that requires ip=...
        with patch.object(command, "_request_headers", return_value={}):
            self.assertEqual(list(command.stream(iter(()))), [])

    def test_large_batch_size_caps_thread_pool_workers(self):
        """Oversized batch_size does not spawn more workers than distinct IPs in the batch."""
        command = CensysAsmHostsCommand()
        # Bypass Option Integer(1,100) to simulate an unvalidated / internal value.
        command._batch_size = 1_000_000

        records = [{"ip": f"192.0.2.{i}"} for i in range(1, 41)]
        executor = MagicMock()
        executor.__enter__.return_value = executor
        executor.map.side_effect = lambda fn, ips: [fn(ip) for ip in ips]

        with (
            patch.object(command, "_request_headers", return_value={}),
            patch.object(
                command,
                "add_field",
                side_effect=lambda record, field_name, field_value: record.__setitem__(
                    field_name, field_value
                ),
            ),
            patch.object(
                command,
                "_fetch_host_json",
                side_effect=lambda ip, headers: ({"ip": ip, "discoveryTrail": []}, False),
            ),
            patch(
                "censys_asm_hosts_command.ThreadPoolExecutor", return_value=executor
            ) as mock_pool,
        ):
            list(command.stream(iter(records)))

        self.assertEqual(mock_pool.call_args.kwargs["max_workers"], 40)
